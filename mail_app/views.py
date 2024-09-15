import threading

from django.shortcuts import render, redirect

from .models import MailMessage
from .forms import MailAccountForm
from . import get_emails


imap_idle_running = False


def index(request):

    global imap_idle_running  # Используем глобальную переменную для контроля статуса

    if request.method == "POST":
        form = MailAccountForm(request.POST)
        if form.is_valid() and not imap_idle_running:
            # Если форма валидна и IMAP IDLE не запущен
            imap_idle_running = True  # Помечаем, что IMAP IDLE запущен

            # Получаем значения почты (можно добавить поля в форму для ввода этих данных)
            mail_user = form.cleaned_data.get("email")
            mail_pass = form.cleaned_data.get("password")
            form.save()

            # Запускаем IMAP IDLE в отдельном потоке и передаем почту
            get_emails.start_idle_listener(mail_user, mail_pass)

            return redirect('mail_list')
    else:
        form = MailAccountForm()

    return render(request, 'mail_app/index.html', {'form': form})


def mail_list(request):
    messages = MailMessage.objects.all()
    return render(request, 'mail_app/mail_list.html', {'messages': messages})
