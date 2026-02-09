import requests
import re
import json
import time


class SteamWebMail:
    def __init__(self, email, password, proxy=None):
        self.email = email
        self.password = password
        self.base_url = "https://steamwebmail.com/"
        self.session = requests.Session()

        # Настройка прокси
        if proxy:
            # Формат прокси: "http://user:pass@host:port" или "http://host:port"
            self.session.proxies = {
                "http": proxy,
                "https": proxy
            }

        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://steamwebmail.com",
            "Referer": "https://steamwebmail.com/",
        }
        self.session.headers.update(self.headers)

        self.xtoken = None
        self.auth_hash = "0"  # Изначально мы гости

    def _get_app_data(self):
        """Внутренний метод для получения актуального токена и хеша сессии"""
        timestamp = int(time.time() * 1000)
        # Если мы уже авторизованы, auth_hash обновится автоматически из ответа
        url = f"{self.base_url}?/AppData@no-mobile-0/{self.auth_hash}/{timestamp}/"

        try:
            resp = self.session.get(url, timeout=10)
            match = re.search(r'window\.__initAppData\((.*)\);', resp.text)
            if match:
                data = json.loads(match.group(1))
                self.xtoken = data.get("System", {}).get("token")
                # Обновляем хеш аккаунта, если он появился (после логина)
                if data.get("AuthAccountHash"):
                    self.auth_hash = data.get("AuthAccountHash")
                return data
        except Exception as e:
            print(f"[-] Ошибка получения AppData: {e}")
        return None

    def login(self):
        """Метод для авторизации"""
        print(f"[*] Попытка входа для {self.email}...")

        # 1. Получаем стартовый токен
        if not self._get_app_data():
            return False

        # 2. Шлем запрос на логин
        login_url = f"{self.base_url}?/Ajax/&q[]=/0/"
        payload = {
            "Email": self.email,
            "Login": "",
            "Password": self.password,
            "Language": "",
            "AdditionalCode": "",
            "AdditionalCodeSignMe": "0",
            "SignMe": "0",
            "Action": "Login",
            "XToken": self.xtoken
        }

        try:
            resp = self.session.post(login_url, data=payload, timeout=10)
            result = resp.json()

            if result.get("Result") is True:
                print("[+] Логин успешен. Обновляем сессию...")
                # После логина ОБЯЗАТЕЛЬНО обновляем AppData, чтобы получить AuthAccountHash
                self._get_app_data()
                return True
            else:
                print(f"[-] Ошибка входа: {result}")
                return False
        except Exception as e:
            print(f"[-] Исключение при логине: {e}")
            return False

    def get_folders(self):
        """Возвращает список папок"""
        url = f"{self.base_url}?/Ajax/&q[]=/{self.auth_hash}/"
        payload = {"Action": "Folders", "XToken": self.xtoken}

        try:
            resp = self.session.post(url, data=payload)
            return resp.json()
        except Exception as e:
            return {"Error": str(e)}

    def get_messages(self, folder="INBOX", page=1):
        """Возвращает список писем в указанной папке"""
        url = f"{self.base_url}?/Ajax/&q[]=/{self.auth_hash}/"
        payload = {
            "Action": "MessageList",
            "Folder": folder,
            "Page": page,
            "Offset": 0,
            "Search": "",
            "XToken": self.xtoken
        }

        try:
            resp = self.session.post(url, data=payload)
            data = resp.json()

            if not data.get("Result"):
                return []

            messages = []
            collection = data["Result"].get("@Collection", [])

            for msg in collection:
                # Парсим отправителя (учитываем странности их API)
                from_email = "Unknown"
                from_data = msg.get("From")
                if isinstance(from_data, list) and len(from_data) > 0:
                    from_email = from_data[0].get("Email")
                elif isinstance(from_data, dict):
                    from_email = from_data.get("@Collection", [{}])[0].get("Email")

                messages.append({
                    "uid": msg.get("Uid"),
                    "subject": msg.get("Subject"),
                    "from": from_email,
                    "date": msg.get("DateRaw")
                })
            return messages
        except Exception as e:
            print(f"[-] Ошибка получения писем: {e}")
            return []

    def get_message_body(self, uid, folder="INBOX"):
        """Получает полное содержимое письма по UID"""
        url = f"{self.base_url}?/Ajax/&q[]=/{self.auth_hash}/"
        payload = {
            "Action": "Message",
            "Folder": folder,
            "Uid": uid,
            "XToken": self.xtoken
        }

        try:
            resp = self.session.post(url, data=payload)
            data = resp.json()
            if data.get("Result"):
                res = data["Result"]
                return res.get("Html") or res.get("Plain") or "Тело письма пустое"
            return None
        except Exception as e:
            print(f"[-] Ошибка получения тела письма: {e}")
            return None


# --- Пример использования ---
# if __name__ == "__main__":
#     # Можно добавить прокси: "http://login:pass@ip:port"
#     # или оставить None
#     PROXY = None
#
#     mail = SteamWebMail(
#         email="dy446323@buyma31.icu",
#         password="22324504",
#         proxy=PROXY
#     )
#
#     if mail.login():
#         # 1. Папки
#         folders = mail.get_folders()
#         print(f"[*] Доступно папок: {len(folders.get('Result', {}).get('@Collection', []))}")
#
#         # 2. Письма
#         messages = mail.get_messages(folder="INBOX")
#         print(f"[*] Найдено писем в INBOX: {len(messages)}")
#
#         for m in messages:
#             print(f"--- [{m['uid']}] {m['from']} : {m['subject']}")
#
#         # 3. Чтение последнего письма
#         if messages:
#             last_uid = messages[0]['uid']
#             body = mail.get_message_body(last_uid)
#             print("\n[ТЕКСТ ПОСЛЕДНЕГО ПИСЬМА]:")
#             print(body[:2000] + "...")  # Печатаем первые 2000 символов