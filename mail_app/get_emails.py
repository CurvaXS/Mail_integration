import time
import json
import threading

from imap_tools import MailBox, AND

from .models import *


MAIL_PASS = "pprxyurridjfvoiv"
MAIL_USER = "mm.pyshkin@yandex.ru"


def create_db_object(m_subject, m_date, m_html, m_attachments):
    MailMessage.objects.create(
        subject=m_subject,
        sent_date=m_date,
        received_date=m_date,
        body=m_html,
        attachments=m_attachments,
    )


def idle_fetch_emails():
    with MailBox("imap.yandex.ru").login(MAIL_USER, MAIL_PASS, "Inbox") as mb:
        # print(mb.folder.list())

        # Входим в режим ожидания (IDLE)
        while True:
            print("Ждем новое сообщение...")
            mb.idle.wait(timeout=60)

            messages = mb.fetch(reverse=True, mark_seen=False)

            for msg in messages:

                if msg.attachments:
                    for att in msg.attachments:
                        attach_json = json.dumps({
                            'filename': f'{att.filename}',
                            'payload': f'{att.payload}',
                            'size': f'{att.size}'
                        })

                    create_db_object(msg.subject, msg.date,
                                     msg.html, attach_json)
                else:
                    create_db_object(msg.subject, msg.date, 
                                     msg.html, [])

                time.sleep(5)


def start_idle_listener():
    thread = threading.Thread(target=idle_fetch_emails)
    thread.daemon = True  # Фоновый режим
    thread.start()
