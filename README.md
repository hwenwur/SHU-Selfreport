# SHU-Selfreport
上海大学 每日一报

# 安装
Linux & python3.8 & docker
```shell
git clone https://github.com/hwenwur/SHU-Selfreport.git
cd SHU-Selfreport
pip install -r requirements.txt
```

# 配置
```shell
cp config.example.json config.json
echo -n '明文密码' | base64
vim config.json
```

# 运行
```shell
docker run -p 127.0.0.1:3000:3000 -d --rm browserless/chrome
python main.py
```

# 定时任务
```shell
crontab -e
# 添加行
# 30 8 * * * bash -c 'cd ~/SHU-Selfreport && python main.py'
# 每天 08:30 运行。注意服务器时区问题。
```
