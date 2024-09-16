import json
import redis
from asgiref.sync import sync_to_async, async_to_sync

from .models import *
from .signals import get_mail_message_count, MESSAGE_LIMIT
from .views import thread
from .get_emails import stop_idle_listener

from channels.generic.websocket import AsyncWebsocketConsumer

# Настройки подключения к Redis
redis_client = redis.StrictRedis(host="127.0.0.1", port=6379, db=0)


def sanitize_group_name(email):
    # Заменяем символы, которые не подходят для имени группы
    new_email = email.replace('@', '_at_').replace('.', '_dot_')
    return new_email.replace('@', '_at_').replace('.', '_dot_')

class AsyncMailConsumer(AsyncWebsocketConsumer):
    # Получение почтового аккаунта
    async def get_mail_account(self, email):
        try:
            # Используем sync_to_async для вызова синхронных методов Django ORM
            return await sync_to_async(MailAccount.objects.get)(email=email)
        except MailAccount.DoesNotExist:
            return None

    # Получение сообщений из базы данных
    async def get_messages_from_db(self, account):
        # Используем sync_to_async для вызова синхронных методов Django ORM
        return await sync_to_async(list)(MailMessage.objects.filter(mail_account=account))

    # Сохранение нового сообщения в базу данных
    async def save_message_to_db(self, message):
        await sync_to_async(message.save)()

    async def connect(self):
        self.email = self.scope['url_route']['kwargs']['email']
        
        self.group_name = sanitize_group_name(self.email)

        self.redis_key = f"messages:{self.group_name}"
        # Подключаемся к группе для отслеживания сообщений
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

        if redis_client.exists(self.redis_key):
            # Достаем сообщения из Redis и отправляем пользователю
            messages = redis_client.lrange(self.redis_key, 0, -1)
            for message in messages:
                message_data = json.loads(message.decode('utf-8'))
                await self.send(text_data=json.dumps({
                    'message': message_data.get('message')
                }))
                print('сообщение в редис:', message_data)
        else:
            # Если в Redis нет сообщений, загружаем их из базы данных
            account = await self.get_mail_account(self.email)
            if account:
                messages = await self.get_messages_from_db(account)
                for message in messages:
                    message_count = await get_mail_message_count()  # Получаем текущее количество сообщений
                    progress = (message_count / MESSAGE_LIMIT) * 100  # Вычисляем прогресс в процентах
                    message_data = {
                        'id': message.id,
                        'subject': message.subject,
                        'sent_date': str(message.sent_date),
                        'received_date': str(message.received_date),
                        'body': str(message.body[:50] + '...'),
                        'progress': progress,  # Передаем прогресс
                        'message_count': message_count,
                        'message_limit': MESSAGE_LIMIT
                    }
                    message_data_json = json.dumps({'message': message_data})

                    await self.send(text_data=message_data_json)
                    print('Новое сообщение:', message_data)
                    # Сохраняем сообщения в Redis
                    redis_client.rpush(self.redis_key, message_data_json)

        # await self.accept()

    async def disconnect(self, close_code):
        # Отключаемся от группы
        stop_idle_listener(thread)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        redis_client.rpush(self.redis_key, json.dumps(message))

        account = await self.get_mail_account(self.email)
        if account:
            new_message = MailMessage(
                account=account,
                body=message['body'],
                subject=message['subject'],
                sent_date=message['sent_date'],
                received_date=message['received_date']
            )
            await self.save_message_to_db(new_message)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'new_email',
                'message': message
            }
        )

    # Обработка события новой записи
    async def new_email(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
