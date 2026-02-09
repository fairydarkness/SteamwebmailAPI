import requests
import re
import json
import time
import logging

logger = logging.getLogger(__name__)


class SteamWebMail:
    def __init__(self, email, password, proxy=None):
        self.email = email
        self.password = password
        self.base_url = "https://steamwebmail.com/"
        self.session = requests.Session()

        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}

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
        self.auth_hash = "0"

    def _get_app_data(self):
        timestamp = int(time.time() * 1000)
        url = f"{self.base_url}?/AppData@no-mobile-0/{self.auth_hash}/{timestamp}/"

        try:
            resp = self.session.get(url, timeout=10)
            match = re.search(r'window\.__initAppData\((.*)\);', resp.text)
            if match:
                data = json.loads(match.group(1))
                self.xtoken = data.get("System", {}).get("token")
                if data.get("AuthAccountHash"):
                    self.auth_hash = data.get("AuthAccountHash")
                return data
        except Exception as e:
            logger.error(f"Error getting AppData: {e}")
        return None

    def login(self):
        if not self._get_app_data():
            return False

        login_url = f"{self.base_url}?/Ajax/&q[]=/0/"
        payload = {
            "Email": self.email, "Login": "", "Password": self.password,
            "Language": "", "AdditionalCode": "", "AdditionalCodeSignMe": "0",
            "SignMe": "0", "Action": "Login", "XToken": self.xtoken
        }

        try:
            resp = self.session.post(login_url, data=payload, timeout=10)
            result = resp.json()

            if result.get("Result") is True:
                self._get_app_data()
                return True
            return False
        except Exception as e:
            logger.error(f"Login exception: {e}")
            return False

    def get_folders(self):
        url = f"{self.base_url}?/Ajax/&q[]=/{self.auth_hash}/"
        payload = {"Action": "Folders", "XToken": self.xtoken}
        try:
            return self.session.post(url, data=payload).json()
        except:
            return None

    def get_messages(self, folder="INBOX", page=1):
        url = f"{self.base_url}?/Ajax/&q[]=/{self.auth_hash}/"
        payload = {
            "Action": "MessageList", "Folder": folder, "Page": page,
            "Offset": 0, "Search": "", "XToken": self.xtoken
        }
        try:
            resp = self.session.post(url, data=payload)
            data = resp.json()
            if not data.get("Result"): return []

            messages = []
            for msg in data["Result"].get("@Collection", []):
                from_email = "Unknown"
                from_data = msg.get("From")
                if isinstance(from_data, list) and len(from_data) > 0:
                    from_email = from_data[0].get("Email")
                elif isinstance(from_data, dict):
                    from_email = from_data.get("@Collection", [{}])[0].get("Email")

                messages.append({
                    "uid": msg.get("Uid"), "subject": msg.get("Subject"),
                    "from": from_email, "date": msg.get("DateRaw")
                })
            return messages
        except:
            return []

    def get_message(self, uid, folder="INBOX"):
        """Возвращает полный JSON письма со всеми метаданными"""
        url = f"{self.base_url}?/Ajax/&q[]=/{self.auth_hash}/"
        payload = {
            "Action": "Message", "Folder": folder, "Uid": uid, "XToken": self.xtoken
        }
        try:
            resp = self.session.post(url, data=payload)
            return resp.json()
        except Exception as e:
            logger.error(f"Get message error: {e}")
            return None

    def get_message_body(self, uid, folder="INBOX"):
        """Возвращает только текст/HTML письма"""
        data = self.get_message(uid, folder)
        if data and data.get("Result"):
            res = data["Result"]
            return res.get("Html") or res.get("Plain") or ""
        return ""
