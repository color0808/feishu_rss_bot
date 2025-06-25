import feedparser
import requests
import time
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from urllib.parse import urlparse
import threading

app = Flask(__name__)

# 飞书 Webhook（无需签名）
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/48775750-ec02-452e-95e3-eff99f29a145"

# RSS 源与来源标签
RSS_FEED_SOURCES = {
    "https://rsshub.app/reuters/world": "Reuters · World",
    "https://rsshub.app/reuters/world/china": "Reuters · China",
    "https://rsshub.app/reuters/world/us": "Reuters · US",
    "https://rsshub.app/reuters/breakingviews": "Reuters · Opinions"
}

# 去重存储已推送链接
pushed_links = set()

# 推送消息到飞书（不使用签名）
def send_to_feishu(text):
    headers = {"Content-Type": "application/json"}
    data = {
        "msg_type": "text",
        "content": {
            "text": text
        }
    }
    response = requests.post(WEBHOOK_URL, json=data, headers=headers)
    print("[Feishu]", response.status_code, response.text)

# 构造消息格式
def format_message(source, entry):
    published = entry.published if 'published' in entry else ''
    return f"【{source}】\n📢 {entry.title}\n🕒 {published}\n🔗 {entry.link}"

# 抓取 RSS 并推送新内容
def fetch_and_push_rss():
    print("[RSS] Starting RSS fetch...")
    for url, source_label in RSS_FEED_SOURCES.items():
        print(f"[DEBUG] Parsing feed: {url}")
        feed = feedparser.parse(url)

        if hasattr(feed, 'status'):
            print(f"[DEBUG] Feed status: {feed.status}")
        print(f"[DEBUG] Entry count: {len(feed.entries)}")

        for entry in feed.entries[:5]:
            if entry.link in pushed_links:
                continue
            pushed_links.add(entry.link)
            text = format_message(source_label, entry)
            print("[RSS] New entry:", text.replace('\n', ' | '))
            send_to_feishu(text)
    print("[RSS] Fetch complete.")

# 定时任务设置
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_push_rss, 'interval', minutes=1)
scheduler.start()

# 启动时立即执行一次
def run_once():
    threading.Thread(target=fetch_and_push_rss).start()

@app.route('/')
def home():
    return 'RSS to Feishu Bot is running. Check logs for activity.'

if __name__ == '__main__':
    run_once()
    app.run(host='0.0.0.0', port=10000)
