import feedparser
import requests
import time
import threading
from datetime import datetime
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# 飞书 Webhook 地址（用户提供）
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/48775750-ec02-452e-95e3-eff99f29a145"

# 路透 RSS 源
RSS_URL = "https://reutersnew.buzzing.cc/feed.xml"

# 存储已推送链接，避免重复
sent_links = set()

# 格式化推送内容
def format_message(entry):
    pub_time = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d %H:%M:%S')
    return f"【Reuters】\n📢 {entry.title}\n🕒 {pub_time}\n🔗 {entry.link}"

# 发送到飞书
def send_to_feishu(text):
    headers = {"Content-Type": "application/json"}
    data = {
        "msg_type": "text",
        "content": {"text": text}
    }
    try:
        resp = requests.post(WEBHOOK_URL, json=data, headers=headers)
        print(f"[Feishu] Status: {resp.status_code}")
    except Exception as e:
        print(f"[Feishu Error] {e}")

# 抓取路透并推送
def fetch_and_push():
    print(f"[RSS] Fetching at {datetime.now()}")
    feed = feedparser.parse(RSS_URL)
    for entry in feed.entries[:5]:
        if entry.link not in sent_links:
            sent_links.add(entry.link)
            msg = format_message(entry)
            send_to_feishu(msg)

# 设置定时任务
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_push, 'interval', minutes=1)
scheduler.start()

# 首次运行立即推送一次欢迎信息和最近新闻
def run_once():
    send_to_feishu("✅ Reuters RSS Bot 已成功部署，开始每分钟自动推送最新新闻。")
    fetch_and_push()

@app.route('/')
def home():
    return "🟢 Feishu Reuters RSS Bot is running."

if __name__ == '__main__':
    run_once()
    app.run(host="0.0.0.0", port=10000)
