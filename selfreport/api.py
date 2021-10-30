import re
import logging
import time
from collections import namedtuple

from . import utils
import requests
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException


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
Record = namedtuple("Record", ["complete", "desc", "location"])
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
    def __init__(self, username, passwd, chrome_driver):
        self.username = username
        self.passwd = passwd
        self.chrome_driver= chrome_driver
        self.session = requests.Session()
        self.session.headers.update(headers)
        # proxies = {
        #     "http": "http://127.0.0.1:7890",
        #     "https": "http://127.0.0.1:7890"
        # }
        # self.session.proxies.update(proxies)
        # self.session.verify = False

    def set_cookie(self, oauth_session, asp_session_id, ncov2019selfreport):
        self.session.cookies.set("SHU_OAUTH2_SESSION", oauth_session, domain="newsso.shu.edu.cn")
        self.session.cookies.set("ASP.NET_SessionId", asp_session_id, domain="selfreport.shu.edu.cn")
        self.session.cookies.set(".ncov2019selfreport", ncov2019selfreport, domain="selfreport.shu.edu.cn")

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

        :return: [Record(False, "2021-06-17(未填报，请点击此处补报)", "/DayReport.aspx?day=2021-06-17"), ...]
        """
        r = self.session.get("https://selfreport.shu.edu.cn/ReportHistory.aspx")
        if not r.url.startswith("https://selfreport.shu.edu.cn/"):
            raise RuntimeError("invalid cookie")
        js_object = utils.substring(r.text, "f2_state=", ";")
        history = HISTORY_RE.findall(js_object)
        ret = []
        for desc, url in history:
            if "未填报" in desc:
                ret.append(Record(complete=False, desc=desc, location=url))
            else:
                ret.append(Record(complete=True, desc=desc, location=url))
        return ret

    def finish_today(self):
        """
        调用 selenium 完成当天的 每日一报
        :return: True on success, False on failed
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        if self.chrome_driver.startswith("http"):
            chrome = webdriver.Remote
        else:
            chrome = webdriver.Chrome
        with chrome(self.chrome_driver, desired_capabilities=options.to_capabilities()) \
                as driver:
            # 设置 selfreport.shu.edu.cn cookie
            driver.get("https://selfreport.shu.edu.cn/res/css/slick.css")
            # cookies_name = ["ASP.NET_SessionId", ".ncov2019selfreport"]
            cookies_name = [".ncov2019selfreport"]
            cookiejar = self.session.cookies
            for name in cookies_name:
                driver.add_cookie(dict(name=name, value=cookiejar.get(name, domain="selfreport.shu.edu.cn")))

            # 设置 newsso.shu.edu.cn cookie
            driver.get("https://newsso.shu.edu.cn/static/css/alert-a1b99b3681.css")
            driver.add_cookie(dict(
                name="SHU_OAUTH2_SESSION",
                value=cookiejar.get("SHU_OAUTH2_SESSION", domain="newsso.shu.edu.cn")
            ))
            # 打开填报页面
            # TODO 处理“历史填报未完成弹窗”

            # 检测是否正在加载
            def is_loading():
                js = """return (function(){
                    let loading = $("#f_ajax_loading"); 
                    if(loading.length > 0) {return loading.is(":visible");} 
                    return false; 
                })(); 
                """
                return driver.execute_script(js)

            # 等待加载完成
            def waiting_loading():
                time.sleep(1)
                while is_loading():
                    print("Waiting for loading...")
                    time.sleep(0.1)

            driver.get("https://selfreport.shu.edu.cn/DayReport.aspx")

            if not driver.current_url.startswith("https://selfreport.shu.edu.cn/DayReport.aspx"):
                logger.info("invalid cookies, page redirect to: %s", driver.current_url)
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
            else:
                logger.info("表单校验完成")

            # 提交表单
            driver.execute_script("__doPostBack('p1$ctl01$btnSubmit', '');")
            waiting_loading()
            if "日报信息提交成功" in driver.page_source:
                logger.info("提交成功")
                return True
            else:
                logger.warning("提交失败")
                logger.warning("Current url: %s, Page Source:\n%s", driver.current_url, driver.page_source)
                return False
