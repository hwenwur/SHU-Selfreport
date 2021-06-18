import logging
import base64
import json
from rich.logging import RichHandler
import api


logging.basicConfig(level=logging.DEBUG, handlers=[RichHandler()])
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)


def main():
    with open("config.json", "r") as cfg:
        config = json.load(cfg)

    chrome_driver = config["chrome_driver"]
    password = config["password"]
    password = base64.b64decode(password.encode()).decode()
    username = config["username"]

    user = api.User(username, password, chrome_driver)

    # for debug
    # ------
    # user.session.cookies.set(".ncov2019selfreport", "1E75A6FBF888B4212DAE6BC032CB408711E23B4B340DCE33243823948BB615663B7EBB97C895AE8AC98883D361A07A8D7B52BA0EE52ADE00E4A4FB921B241943DC2E5835102E2F2B5387DAD0522482C18AAADA2EBA7879FC28BE852CBB07A8632931C557943ABE2D031CADE76A4C401C", domain="selfreport.shu.edu.cn")
    # user.session.cookies.set("ASP.NET_SessionId", "ja5u2uonanyas1axcb0vnuhb", domain="selfreport.shu.edu.cn")
    # ------
    user.login()
    # https://selfreport.shu.edu.cn/res/css/slick.css
    # history = user.fetch_history()
    if user.finish_today():
        print("填报成功")
    else:
        print("填报失败")


if __name__ == '__main__':
    main()
