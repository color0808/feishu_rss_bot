# 飞书 RSS 推送机器人（适配 Render 部署）

## 功能

- 每分钟抓取并推送以下 4 个 RSS 源：
  - Reuters · World
  - Reuters · China
  - Reuters · US
  - Reuters · Opinions

## 消息格式示例

```
【Reuters · China】
📢 China's Premier Vows Support for Private Sector
🕒 2025-06-25 07:30
🔗 https://www.reuters.com/world/china/chinas-premier-vows-support-private-sector
```

## Render 部署步骤

1. 上传本项目到你的 GitHub
2. 打开 [https://render.com](https://render.com)，点击 `New → Web Service`
3. 配置如下：
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python rss_to_feishu.py`
   - Port: 10000

项目部署后即可每分钟推送最新 RSS 更新到飞书群聊。
