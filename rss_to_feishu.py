import feedparser
import requests
import hashlib
import hmac
import base64
import time
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from urllib.parse import urlparse
import threading

app = Flask(__name__)

# 飞书 Webhook 配置
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/48775750-ec02-452e-95e3-eff99f29a145"
SIGNING_SECRET = "HC5W7genr5mMcb8uyhnvge"

# RSS 源与分类标签映射
RSS_FEED_SOURCES = {
    "https://rsshub.app/reuters/world": "Reuters · World",
    "https://rsshub.app/reuters/world/china": "Reuters · China",
    "https://rsshub.app/reuters/world/us": "Reuters · US",
    "https://rsshub.app/reuters/breakingviews": "Reuters · Opinions"
}

# 用于避免重复推送
pushed_links = set()

# 签名生成函数
def generate_signature(timestamp, secret):
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(secret.encode(), string_to_sign.encode(), digestmod=hashlib.sha256).digest()
    return base64.b64encode(hmac_code).decode()

# 推送消息到飞书
def send_to_feishu(text):
    timestamp = str(int(time.time()))
    sign = generate_signature(timestamp, SIGNING_SECRET)

    headers = {"Content-Type": "application/json"}
    data = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "text",
        "content": {
            "text": text
        }
    }
    response = requests.post(WEBHOOK_URL, json=data, headers=headers)
    print("[Feishu]", response.status_code, response.text)

# 构造格式化文本内容
def format_message(source, entry):
    published = entry.published if 'published' in entry else ''
    return f"【{source}】\n📢 {entry.title}\n🕒 {published}\n🔗 {entry.link}"

# 抓取并推送 RSS 内容
def fetch_and_push_rss():
    print("[RSS] Starting RSS fetch...")
    for url, source_label in RSS_FEED_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            if entry.link in pushed_links:
                continue
            pushed_links.add(entry.link)
            text = format_message(source_label, entry)
            print("[RSS] New entry:", text.replace('\n', ' | '))
            send_to_feishu(text)
    print("[RSS] Fetch complete.")

# 设置定时任务
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_push_rss, 'interval', minutes=1)
scheduler.start()

# 首次启动立即抓取一次
def run_once():
    threading.Thread(target=fetch_and_push_rss).start()

@app.route('/')
def home():
    return 'RSS to Feishu Bot is running. Check logs for activity.'

if __name__ == '__main__':
    run_once()
    app.run(host='0.0.0.0', port=10000)
