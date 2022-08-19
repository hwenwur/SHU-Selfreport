# SHU-Selfreport
上海大学 每日一报

**---------------------------------------**

**本人已经毕业，项目不在维护**

**本人已经毕业，项目不在维护**

**本人已经毕业，项目不在维护**

**---------------------------------------**

## 特点
- 无论成功、失败还是异常都会有通知
- 通知形式支持 `telegram` 机器人、 `QQ` 邮箱
- 和手动操作行为高度一致
- 目前只会回答以下几个问题：
  - 我承诺，以下报送内容真实有效并可用于学校管理需要！【勾选】
  - 消防安全问题【选择正确答案】
  - 当前身体状况【良好】
  - 当天是否在上海【是】
  - 当天是否住学校【是】
  - 是否家庭地址【不是】

## 安装
linux 服务器需要安装 `docker`, 桌面系统(windows, linux)需要下载 Chrome Driver.

- 桌面系统
安装 Chrome 浏览器，Python3.8 以上。
点击本页面右上方的 Download zip, 然后解压后在终端运行`pip install -r requirements.txt`。

- linux 服务器
```shell
git clone https://github.com/hwenwur/SHU-Selfreport.git
cd SHU-Selfreport
pip install -r requirements.txt
```

## 配置
将 `config.example.json` 重命名（或者复制）为 `config.json`，用编辑器打开，按照以下说明修改。
 ```
 {
  // 学号
  "username": "18111111",
  // base64 编码后的密码，可以打开 https://base64.us/ ，输入密码，然后点击 '编码' 按钮
  "password": "cGFzc3dvcmQ=",
  // chrome_driver 的路径。可以在这里下载：https://chromedriver.chromium.org/downloads
  "chrome_driver": "D:\\path\\to\\chromedriver.exe",
  // 日志输出文件名，不用改。
  "log_path": "logging.txt",
  "notify": {
    // 通知渠道，填 email 就行。
    "channel": "email",
    // 如果渠道填了 email, 这部分可以不管。
    "telegram": {
      "chat_id": 123456789,
      "api_url": "https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    },
    // 邮箱的配置。可以自己发给自己，微信也会有推送。
    "email": {
      // 发送方邮件地址
      "username": "sender@qq.com",
      // 密码，注意不是 QQ 密码
      "password": "abcedasas",
      // 如果是 QQ 邮箱，这里不用改
      "server": "smtp.qq.com:465",
      // 接受方邮件地址，可以和发送方一样，也就是自己发给自己。
      "receiver": "receiver@qq.com"
    }
  }
}
 ```

## 运行
```shell
python main.py
```
如果是 linux server, 需要先运行：`docker run -p 127.0.0.1:3000:3000 -d --rm browserless/chrome`, 并把配置文件中的 `chrome_driver` 改为 `http://127.0.0.1:3000/webdriver`。

## 定时任务(linux server only)
```shell
crontab -e
# 添加行
# 30 8 * * * bash -c 'cd ~/SHU-Selfreport && python main.py'
# 每天 08:30 运行。注意服务器时区问题。
```
