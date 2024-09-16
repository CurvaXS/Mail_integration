import threading
from django.shortcuts import render, redirect

from django.views.generic.detail import DetailView

from .models import MailMessage, MailAccount
from .forms import MailAccountForm
from . import get_emails

imap_idle_running = False
current_email = None
thread =  None

def index(request):
    global imap_idle_running, current_email, thread
    
    if request.method == "POST":
        form = MailAccountForm(request.POST)
        if form.is_valid() and not imap_idle_running:
            # Если форма валидна и IMAP IDLE не запущен
            mail_user = form.cleaned_data.get("email")
            mail_pass = form.cleaned_data.get("password")

            current_email = mail_user

            try:
                # Ищем запись по email
                account = MailAccount.objects.get(email=mail_user)
                
                # Проверяем пароль
                if account.password == mail_pass:
                    # Если пароль верный, запускаем слушатель
                    if not imap_idle_running:
                        imap_idle_running = True  # Помечаем, что IMAP IDLE запущен
                        get_emails.start_idle_listener(mail_user, mail_pass)
                        thread = get_emails.start_idle_listener(mail_user, mail_pass)
                    return redirect('mail_list')
                else:
                    # Если пароль неверный, выводим ошибку
                    form.add_error('password', 'Неверный пароль.')

            except MailAccount.DoesNotExist:
                # Если аккаунт не найден, сохраняем новый
                form.save()
                if not imap_idle_running:
                    imap_idle_running = True  # Помечаем, что IMAP IDLE запущен
                    get_emails.start_idle_listener(mail_user, mail_pass)
                    thread = get_emails.start_idle_listener(mail_user, mail_pass)
                return redirect('mail_list')
    else:
        form = MailAccountForm()

    return render(request, 'mail_app/index.html', {'form': form})


def mail_list(request):
    messages = MailMessage.objects.all()
    return render(request, 'mail_app/mail_list.html', {
        # 'messages': messages,
        'current_email': current_email
        })

class MailDetail(DetailView):
    model = MailMessage
    context_object_name = 'mess'
    template_name = 'mail_app/mail_detail.html'
    
