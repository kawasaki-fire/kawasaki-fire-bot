import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

LINE_TOKEN = os.environ["LINE_TOKEN"]
URL = "https://sc.city.kawasaki.jp/saigai/index.htm"

def send_line(msg):
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

# 川崎市サイトのスクレイピング
html = requests.get(URL).text
soup = BeautifulSoup(html, "html.parser")

rows = soup.select("div.news_body li")
current = []

for r in rows:
    date = r.select_one("span").text.strip()
    title = r.select_one("a").text.strip()
    link = "https://sc.city.kawasaki.jp" + r.select_one("a")["href"]
    
    # 消防団向けカスタム例
    if "火災" in title:       # 火災のみ
        if "川崎区" in title:  # 川崎区のみ（任意）
            current.append({"date": date, "title": title, "link": link})

# 前回取得データ
try:
    with open("prev.json", "r", encoding="utf-8") as f:
        prev = json.load(f)
except:
    prev = []

# 新着のみ抽出
new_items = [x for x in current if x not in prev]

# LINE送信
for item in new_items:
    msg = f"""🔥 川崎市 火災情報
{item['date']}
{item['title']}
{item['link']}"""
    send_line(msg)

# 前回データ保存
with open("prev.json", "w", encoding="utf-8") as f:
    json.dump(current, f, ensure_ascii=False, indent=2)
