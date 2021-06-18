import logging
import smtplib
from email.header import Header
from email.mime.text import MIMEText
import requests


logger = logging.getLogger(__name__)


class Notify:
    def __init__(self, config):
        self._config = config

    def telegram(self, title, message):
        """
        Send message by telegram bot.
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

    def email(self, title, message):
        """
        Send message by email
        :param title:
        :param message:
        :return:
        """
        config = self._config["email"]
        host, port = config["server"].split(":")
        port = int(port)
        serv = smtplib.SMTP_SSL(host, port)
        msg = MIMEText(message, "plain", "utf-8")
        msg["From"] = Header(config["username"], "utf-8")
        msg["To"] = Header(config["receiver"], "utf-8")
        msg["Subject"] = Header(title, "utf-8")
        try:
            serv.login(config["username"], config["password"])
            serv.sendmail(config["username"], config["receiver"], msg.as_string())
            return True
        except smtplib.SMTPException as e:
            logger.exception(e)
            return False

    def notify(self, title, message):
        channel = self._config["channel"]
        try:
            func = getattr(self, channel)
        except AttributeError:
            raise ValueError("Invalid channel name")
        return func(title, message)
