from django.db.models.signals import post_save
from django.dispatch import receiver

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import MailMessage


@receiver(post_save, sender=MailMessage)
def get_new_email(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "mail_messages",
            {
                "type": "new_email",
                "message": [
                    instance.id,
                    instance.subject,
                    f'{instance.sent_date}',
                    f'{instance.received_date}',
                    instance.body[:50],
                ]
            }
        )
