# SHU-Selfreport
上海大学 每日一报

## 特点
- 无论成功、失败还是异常都会有通知
- 通知形式支持 `telegram` 机器人、 `QQ` 邮箱
- 和手动操作行为高度一致
- 目前只会回答以下几个问题：
  - 我承诺，以下报送内容真实有效并可用于学校管理需要！【勾选】
  - 当前身体状况【良好】
  - 当天是否在上海【是】
  - 当天是否住学校【是】
  - 是否家庭地址【不是】

## 安装
Linux & python3.8 & docker
```shell
git clone https://github.com/hwenwur/SHU-Selfreport.git
cd SHU-Selfreport
pip install -r requirements.txt
```

## 配置
```shell
cp config.example.json config.json
echo -n '明文密码' | base64
vim config.json
```

## 运行
```shell
docker run -p 127.0.0.1:3000:3000 -d --rm browserless/chrome
python main.py
```

## 定时任务
```shell
crontab -e
# 添加行
# 30 8 * * * bash -c 'cd ~/SHU-Selfreport && python main.py'
# 每天 08:30 运行。注意服务器时区问题。
```
