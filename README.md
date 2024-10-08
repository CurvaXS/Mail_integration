```markdown
# Mail Integration Project

## Описание
Проект представляет собой систему для интеграции с почтовым сервисом через протокол IMAP. Приложение получает письма в реальном времени, отображает их на веб-странице и сохраняет в базу данных. Redis используется для кэширования сообщений, а WebSockets — для обновления страницы с письмами в реальном времени.

### Основные функции
- Аутентификация почтового аккаунта через веб-форму.
- Получение писем с помощью IMAP (с поддержкой IDLE) и сохранение их в базу данных PostgreSQL.
- Отображение списка писем на веб-странице с помощью Django.
- Реализация прогресс-бара, который показывает процесс загрузки писем.
- Обновление страницы с новыми письмами в реальном времени с использованием WebSockets.
- Использование Redis для кэширования сообщений.

## Установка и настройка

### 1. Клонирование репозитория
```bash
git clone <URL вашего репозитория>
cd <название вашего проекта>
```

### 2. Установка виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных PostgreSQL
Создайте базу данных и укажите настройки подключения в `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'App',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}
```

### 5. Выполнение миграций
```bash
python manage.py migrate
```

### 6. Запуск Redis
Для работы WebSockets и кэширования сообщений необходимо запустить Redis сервер:

```bash
redis-server
```

### 7. Запуск Daphne (ASGI сервер для WebSockets)
```bash
daphne -p 8001 mail_integration.asgi:application
```

### 8. Запуск Django сервера
```bash
python manage.py runserver
```

## Использование

1. Перейдите на главную страницу проекта (обычно это `http://127.0.0.1:8000/`).
2. Введите почтовый адрес и пароль.
3. Приложение начнет получать письма через IMAP и отображать их на странице.
4. Сообщения будут обновляться в реальном времени с использованием WebSockets.

## Основные файлы проекта

- **models.py**: Описание моделей `MailAccount` и `MailMessage`, которые используются для хранения информации о почтовых аккаунтах и письмах.
- **views.py**: Основная логика для отображения сообщений и работы с почтовыми аккаунтами.
- **get_emails.py**: Скрипт для работы с IMAP сервером и получения писем.
- **AsyncMailConsumer (settings.py)**: Реализация WebSockets для получения и отображения сообщений в реальном времени.
- **requirements.txt**: Зависимости проекта.
- **mail_list.html**: Шаблон для отображения списка писем и прогресс-бара.

## Требования

- Python 3.8+
- PostgreSQL
- Redis
- IMAP доступ к почтовому серверу

## Примечания

- Приложение поддерживает только почтовые аккаунты с доступом через IMAP.
- В текущей реализации используется Redis для хранения сообщений. При необходимости, сообщения могут также извлекаться из базы данных при отсутствии их в Redis.

## Лицензия
Этот проект распространяется под лицензией MIT. Для получения дополнительной информации смотрите файл LICENSE.

```

Этот файл README.md предоставляет базовую информацию о проекте, инструкции по установке, настройке и использованию. Если у вас есть дополнительные требования или изменения в функционале, их можно добавить в соответствующие разделы.