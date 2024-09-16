import datetime
import time
import json
import threading

from imap_tools import MailBox, AND

# from .models import *
from .models import MailAccount, MailMessage

MAIL_PASS = "pprxyurridjfvoiv"
MAIL_USER = "mm.pyshkin@yandex.ru"


def create_db_object(mail_user, m_subject, m_date, m_html, m_attachments):
    try:
        mail_account = MailAccount.objects.get(email=mail_user)

        # m_date_str = m_date.isoformat() if isinstance(m_date, datetime) else m_date

        if not MailMessage.objects.filter(mail_account=mail_account, subject=m_subject, sent_date=m_date, body=m_html).exists():
            MailMessage.objects.create(
                mail_account=mail_account,
                subject=m_subject,
                sent_date=m_date,
                body=m_html,
                attachments=m_attachments,
            )
            print("Сообщение добавлено в базу данных")
        else:
            print("Дублирующее сообщение, не добавлено в базу данных")
    except MailAccount.DoesNotExist:
        # Обрабатываем конкретное исключение, если пользователь не найден
        print(f"Пользователь с email {mail_user} не найден в базе данных")
        return
    except Exception as e:
        # Обрабатываем другие исключения и выводим их
        print(f"Произошла ошибка: {str(e)}")
        return


def idle_fetch_emails(mail_user, mail_pass):
    with MailBox("imap.yandex.ru").login(mail_user, mail_pass, "Inbox") as mb:
        # print(mb.folder.list())

        # Входим в режим ожидания (IDLE)
        while True:
            print("Ждем новое сообщение...")
            mb.idle.wait(timeout=0.05)

            messages = mb.fetch(reverse=True, mark_seen=False)

            for msg in messages:

                if msg.attachments:
                    for att in msg.attachments:
                        attach_json = json.dumps({
                            'filename': f'{att.filename}',
                            'payload': f'{att.payload}',
                            'size': f'{att.size}'
                        })

                    create_db_object(mail_user, msg.subject, msg.date,
                                     msg.html, attach_json)
                else:
                    create_db_object(mail_user, msg.subject, msg.date,
                                     msg.html, [])

                time.sleep(0.05)


def start_idle_listener(m_user, m_pass):
    thread = threading.Thread(
        target=idle_fetch_emails,
        args=(m_user, m_pass)
    )
    thread.daemon = True
    thread.start()

def stop_idle_listener(thread):
    global stop_event
    stop_event.set()  # Установить флаг остановки
    thread.join()  # Дождаться завершения потока
# if __name__ == "__main__":
#     start_idle_listener("mm.pyshkin@yandex.ru", "pprxyurridjfvoiv")
