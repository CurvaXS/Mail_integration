from django.shortcuts import render
from .models import MailMessage


def mail_list(request):
    messages = MailMessage.objects.all()
    return render(request, 'mail_app/mail_list.html', {'messages': messages})
