from enum import Enum
import requests
import logging

logging.basicConfig(filename='../errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(pathname)s - Line %(lineno)d - %(message)s')


class Condition(Enum):

    INFO = "✅"


class Telegram:

    def __init__(self, token, chat_id, use):
        self._token = token
        self._chat_id = chat_id
        self._use = use
        self._url = f"https://api.telegram.org/bot{token}/"

    def log(self, message, condition=None):
        text = message
        if condition is not None:
            text = f"{condition.value} {text}"

        url = self._url + "sendMessage"
        resp = requests.post(
            url=url,
            params = {
                "chat_id": self._chat_id,
                "text": text
            }
        )
        resp.raise_for_status()

    def info(self, message):
        if not self._use:
            ...
        else:
            try:
                self.log(message, Condition.INFO)
            except requests.exceptions.HTTPError as e:
                logging.error(f"Warning -requests.exceptions.HTTPError: {e}")
            
        