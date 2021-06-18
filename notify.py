import logging
import requests


logger = logging.getLogger(__name__)


class Notify:
    def __init__(self, config):
        self._config = config

    def telegram(self, title, message):
        """
        Send message from telegram bot.
        :param title:
        :param message:
        :return: True or False
        """
        config = self._config["telegram"]
        url = config["api_url"] + "/sendMessage"
        data = {
            "chat_id": config["chat_id"],
            "text": "%s:\n%s" % (title, message)
        }
        r = requests.post(url, data)
        if r.status_code != 200 or (not r.json()["ok"]):
            logger.error("telegram notify failed. status_code: %s, source: %s", r.status_code, r.json())
            return False
        return True
