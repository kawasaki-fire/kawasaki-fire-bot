import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# LINEトークン（GitHub Secretsから取得）
LINE_TOKEN = os.environ["LINE_TOKEN"]
URL = "https://sc.city.kawasaki.jp/saigai/index.htm"

def send_line(msg):
    """LINE公式アカウントに通知"""
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "messages": [
            {"type": "text", "text": msg}
        ]
    }
    requests.post("https://api.line.me/v2/bot/message/broadcast",
                  headers=headers, json=body)

# -----------------------------
# 川崎市災害情報スクレイピング
# -----------------------------
html = requests.get(URL).text
soup = BeautifulSoup(html, "html.parser")

rows = soup.select("div.news_body li")
current = []

for r in rows:
    date = r.select_one("span").text.strip()
    title = r.select_one("a").text.strip()
    link = "https://sc.city.kawasaki.jp" + r.select_one("a")["href"]
    
    # -----------------------------
    # カスタム条件：多摩区かつ消防車出場情報のみ
    # -----------------------------
    if "多摩区" in title and "消防車が出場" in title:
        current.append({"date": date, "title": title, "link": link})

# -----------------------------
# 前回取得データ読み込み
# -----------------------------
try:
    with open("prev.json", "r", encoding="utf-8") as f:
        prev = json.load(f)
except FileNotFoundError:
    prev = []

# -----------------------------
# 新着のみ抽出
# -----------------------------
new_items = [x for x in current if x not in prev]

# -----------------------------
# LINE通知
# -----------------------------
for item in new_items:
    msg = f"""🔥 川崎市 消防出動情報
{item['date']}
{item['title']}
{item['link']}"""
    send_line(msg)

# -----------------------------
# 前回データ保存
# -----------------------------
with open("prev.json", "w", encoding="utf-8") as f:
    json.dump(current, f, ensure_ascii=False, indent=2)

# -----------------------------
# テスト送信（初回確認用）
# 必要がなければコメントアウト可
# -----------------------------
# send_line("✅ テスト通知です。GitHub Actions から送信されました")
