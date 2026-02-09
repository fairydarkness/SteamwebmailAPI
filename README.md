# SteamwebmailAPI
Unofficial Python API for steamwebmail.com
Fast, lightweight, and browserless library for automating steamwebmail.com. Support for session management, proxy, folder navigation, and message retrieval.

Неофициальное Python API для steamwebmail.com
Быстрая, легкая и не требующая браузера библиотека для автоматизации steamwebmail.com. Поддержка управления сессиями, прокси, навигации по папкам и извлечения сообщений.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Requests](https://img.shields.io/badge/library-requests-orange.svg)

[English](#en)
[Русский](#ru)

<a name="en"></a>
## 🇬🇧 English

# Introduction
This code was written to automate the retrieval of emails from steamwebmail due to the lack of an official IMAP/API. It uses the requests library and the sessions method, which allows you to simulate login to access messages. Be sure to use a proxy for requests from Russia.

### ✨ Key Features
- 🚀 **High Speed:** Significantly faster performance by using direct AJAX requests without the overhead of a heavy browser.
- 🧠 **Smart Sessions:** Automatic handling of `XToken` and `AuthAccountHash` parameters with no user intervention required.
- 🌐 **Proxy Support:** Full compatibility with HTTP/HTTPS proxies (essential for stable access in restricted regions).
- 🪶 **Lightweight:** Minimal RAM consumption and no bloated dependencies (only `requests` library is required).

# Quick start

python>=3.11

```bash
pip install -r requirements.txt
```

```python
from SteamwebmailAPI import SteamWebMail

# Proxy format: "http://user:pass@host:port" or "http://host:port"
mail = SteamWebMail(email="login@example.com", password="password", proxy=None)

if mail.login():
    # Get messages from INBOX
    messages = mail.get_messages(folder="INBOX")
    
    if messages:
        # Show latest message body
        uid = messages[0]['uid']
        body = mail.get_message_body(uid)
        print(f"Latest Subject: {messages[0]['subject']}")
        print(f"Content: {body}")
```

### Methods Reference

| Method | Description |
| :--- | :--- |
| `login()` | Performs authentication and session synchronization. |
| `get_folders()` | Returns a dictionary of all available folders. |
| `get_messages(folder, page)` | Returns a list of message headers (`uid`, `subject`, `from`, `date`). |
| `get_message(uid, folder)` | Returns the full JSON response for a specific email. |
| `get_message_body(uid, folder)` | Returns only the HTML or Plain text content of the email. |

<a name="ru"></a>
## 🇷🇺 Русский

# Описание
Библиотека разработана для автоматизации работы с почтой steamwebmail.com. Главное преимущество — отсутствие браузера. Работа через прямые AJAX-запросы позволяет использовать её в многопоточных скриптах (авторегеры, чекеры) с минимальным потреблением ОЗУ.

### ✨ Основные возможности
- 🚀 **Высокая скорость:** В разы быстрее Selenium за счет работы на прямых AJAX-запросах без загрузки тяжелого браузера.
- 🧠 **Умные сессии:** Автоматическая обработка параметров `XToken` и `AuthAccountHash` без участия пользователя.
- 🌐 **Поддержка прокси:** Полная совместимость с HTTP/HTTPS прокси (критически важно для стабильного доступа из РФ).
- 🪶 **Легкость:** Минимальное потребление ОЗУ и отсутствие лишних зависимостей (нужен только `requests`).

# Быстрый старт
python>=3.11

```bash
pip install -r requirements.txt
```

```python
from SteamwebmailAPI import SteamWebMail

# Proxy format: "http://user:pass@host:port" or "http://host:port"
mail = SteamWebMail(email="login@example.com", password="password", proxy=None)

if mail.login():
    # Получает сообщения из папки Входящие (INBOX)
    messages = mail.get_messages(folder="INBOX")
    
    if messages:
        # Показывает тело последнего письма
        uid = messages[0]['uid']
        body = mail.get_message_body(uid)
        print(f"Latest Subject: {messages[0]['subject']}")
```

### Таблица методов

| Метод | Описание |
| :--- | :--- |
| `login()` | Выполняет авторизацию и синхронизацию сессии. |
| `get_folders()` | Возвращает словарь всех доступных папок. |
| `get_messages(folder, page)` | Возвращает список заголовков писем (`uid`, `subject`, `from`, `date`). |
| `get_message(uid, folder)` | Возвращает полный JSON-ответ для конкретного письма. |
| `get_message_body(uid, folder)` | Возвращает только HTML или текстовое содержимое письма. |

# ⚠️ Disclaimer
This project is for educational purposes only. The author is not responsible for any use that violates steamwebmail.com terms of service.

# 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
