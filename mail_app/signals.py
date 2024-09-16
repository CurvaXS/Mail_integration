from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async


from .models import MailMessage

def sanitize_group_name(email):
    # Заменяем символы, которые не подходят для имени группы
    new_email = email.replace('@', '_at_').replace('.', '_dot_')
    return new_email.replace('@', '_at_').replace('.', '_dot_')

# Максимальное количество сообщений для завершения прогресса
MESSAGE_LIMIT = 600

@sync_to_async
def get_mail_message_count():
    return MailMessage.objects.count()

@receiver(post_save, sender=MailMessage)
def get_new_email(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        sanitized_email = sanitize_group_name(instance.mail_account.email)  # Преобразуем email
        message_count = async_to_sync(get_mail_message_count)()  # Получаем текущее количество сообщений
        progress = (message_count / MESSAGE_LIMIT) * 100  # Вычисляем прогресс в процентах

        # Получение количества сообщений через async_to_sync для синхронного вызова
        message_count = async_to_sync(get_mail_message_count)()

        async_to_sync(channel_layer.group_send)(
            sanitized_email,  # Используем email для группы
            {
                'type': 'new_email',
                'message': {
                    'id': instance.id,
                    'subject': instance.subject,
                    'sent_date': str(instance.sent_date),
                    'received_date': str(instance.received_date),
                    'body': str(instance.body[:50] + '...'),
                    'progress': progress,  # Передаем прогресс
                    'message_count': message_count,
                    'message_limit': MESSAGE_LIMIT # Используем результат вызова
                }
            }
        )
