import os
import base64
import json
import logging

from rich.logging import RichHandler

from selfreport import api
from selfreport.notify import Notify


NOTIFY_TITLE = "每日一报bot"


def setup_logger(file_path):
    hds = [logging.FileHandler(file_path)]
    if os.isatty(2):
        hds.append(RichHandler())
    logging.basicConfig(format="%(asctime)s " + logging.BASIC_FORMAT, level=logging.DEBUG, handlers=hds)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)


def run(user, notify):
    user.login()
    history = user.fetch_history()
    if history[0].complete:
        # 已完成
        notify.notify(NOTIFY_TITLE, "检测到已被提交: %s" % history[0].desc)
    else:
        # 未完成
        ok = user.finish_today()
        if ok:
            history = user.fetch_history()
            notify.notify(NOTIFY_TITLE, "自动填报完成: %s" % history[0].desc)
        else:
            notify.notify(NOTIFY_TITLE, "自动填报失败")


def main():
    with open("config.json", "r") as cfg:
        config = json.load(cfg)

    setup_logger(config["log_path"])
    notify = Notify(config["notify"])

    chrome_driver = config["chrome_driver"]
    password = config["password"]
    password = base64.b64decode(password.encode()).decode()
    username = config["username"]

    user = api.User(username, password, chrome_driver)

    try:
        run(user, notify)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        notify.notify(NOTIFY_TITLE, "程序运行失败：%s" % str(e))
        raise


if __name__ == '__main__':
    main()
