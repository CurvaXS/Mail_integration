from django.contrib import admin

from .models import MailAccount, MailMessage

admin.site.register(MailAccount)
admin.site.register(MailMessage)
