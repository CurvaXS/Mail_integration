import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer


class AsyncMailConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Подключаемся к группе для отслеживания сообщений
        await self.channel_layer.group_add("mail_messages", self.channel_name)
        await self.accept()


    async def disconnect(self, close_code):
        # Отключаемся от группы
        await self.channel_layer.group_discard("mail_messages", self.channel_name)

    # async def receive(self, text_data):
    #     pass

    # Обработка события новой записи
    async def new_email(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

