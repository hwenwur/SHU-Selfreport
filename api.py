import re
import logging
import time
from collections import namedtuple

import utils
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException


# RSA 公钥
SHU_RSA_PUBKEY = """
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDl/aCgRl9f/4ON9MewoVnV58OL
OU2ALBi2FKc5yIsfSpivKxe7A6FitJjHva3WpM7gvVOinMehp6if2UNIkbaN+plW
f5IwqEVxsNZpeixc4GsbY9dXEk3WtRjwGSyDLySzEESH/kpJVoxO7ijRYqU+2oSR
wTBNePOk1H+LRQokgQIDAQAB
-----END PUBLIC KEY-----"""

# group: 1 - description, 2 - url location
HISTORY_RE = re.compile(r'\["","(.*?)",\d+,"","(.*?)","",(?:true|false)]')
Question = namedtuple("Question", ["desc", "xpath", "type_"])
FORM = [
    Question(
        desc="我承诺，以下报送内容真实有效并可用于学校管理需要！",
        xpath="//div[@id='p1_ChengNuo']/div[@class='f-field-body-cell']//i",
        type_="checkbox"
    ),
    Question(
        desc="当前身体状况",
        xpath="//div[@id='p1_DangQSTZK']//td[1]/div/div[@class='f-field-body-cell']//i",
        type_="radio"
    ),
    Question(
        desc="当天是否在上海",
        xpath="//div[@id='p1_ShiFSH']//td[1]/div/div[@class='f-field-body-cell']//i",
        type_="radio"
    ),
    Question(
        desc="当天是否住学校",
        xpath="//div[@id='p1_ShiFZX']//td[1]/div/div[@class='f-field-body-cell']//i",
        type_="radio"
    ),
    Question(
        desc="是否家庭地址",
        xpath="//div[@id='p1_ShiFZJ']//td[2]/div/div[@class='f-field-body-cell']//i",
        type_="radio"
    )
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9"
}
logger = logging.getLogger(__name__)


class User:
    def __init__(self, username, passwd, chrome_driver_path):
        self.username = username
        self.passwd = passwd
        self.chrome_driver_path = chrome_driver_path
        self.session = requests.Session()
        self.session.headers.update(headers)
        # proxies = {
        #     "http": "http://127.0.0.1:8080",
        #     "https": "http://127.0.0.1:8080"
        # }
        # self.session.proxies.update(proxies)
        # self.session.verify = False

    def login(self):
        session = self.session
        r = session.get("https://selfreport.shu.edu.cn/Default.aspx")
        url = r.url

        # encrypt password
        password = utils.rsa_encrypt(SHU_RSA_PUBKEY, self.passwd.encode())
        data = dict(username=self.username, password=password)

        r = session.post(url, data, headers={"Referer": url})
        if r.status_code == 200 and "学工号：" in r.text:
            logger.debug("Login success.")
            return True
        else:
            logger.error("Login failed. status_code%s, url:%s\ntext:%s", r.status_code, r.url, r.text)
            return False

    def fetch_history(self):
        """
        获取历史填报记录
        :return: [("2021-06-17(未填报，请点击此处补报)", "/DayReport.aspx?day=2021-06-17"), ...]
        """
        r = self.session.get("https://selfreport.shu.edu.cn/ReportHistory.aspx")
        js_object = utils.substring(r.text, "f2_state=", ";")
        history = HISTORY_RE.findall(js_object)
        return history

    def finish_today(self):
        """
        调用 selenium 完成当天的 每日一报
        :return: None
        """
        with webdriver.Chrome(executable_path=self.chrome_driver_path) as driver:
            # 设置 cookies
            driver.get("https://selfreport.shu.edu.cn/res/css/slick.css")
            cookies_name = ["ASP.NET_SessionId", ".ncov2019selfreport"]
            cookiejar = self.session.cookies
            for name in cookies_name:
                driver.add_cookie(dict(name=name, value=cookiejar.get(name, domain="selfreport.shu.edu.cn")))
            # 打开填报页面
            # TODO 处理“历史填报未完成弹窗”

            # 检测是否正在加载
            def is_loading():
                try:
                    loading = driver.find_element_by_id("f_ajax_loading")
                    if loading.is_displayed():
                        return True
                except NoSuchElementException:
                    pass
                return False

            # 等待加载完成
            def waiting_loading():
                time.sleep(1)
                while is_loading():
                    print("Waiting for loading...")
                    time.sleep(0.1)

            driver.get("https://selfreport.shu.edu.cn/DayReport.aspx")

            if not driver.current_url.startswith("https://selfreport.shu.edu.cn/DayReport.aspx"):
                logger.info("invalid cookies")
                return False

            for ques in FORM:
                waiting_loading()
                element = driver.find_element_by_xpath(ques.xpath)
                try:
                    element.click()
                except ElementNotInteractableException:
                    logger.error("ElementNotInteractableException: %s", ques.desc)

            # 校验表单
            is_ok = driver.execute_script("return F.validateForm('p1', '_self', true, false);")
            if not is_ok:
                logger.warning("表单未完成")
                return False

            # 提交表单
            driver.execute_script("__doPostBack('p1$ctl01$btnSubmit', '');")
            waiting_loading()
            if "日报信息提交成功" in driver.page_source:
                return True
            else:
                logger.warning("提交失败")
                logger.warning("Current url: %s, Page Source:\n%s", driver.current_url, driver.page_source)
                return False
