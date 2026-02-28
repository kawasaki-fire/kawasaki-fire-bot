import requests
from bs4 import BeautifulSoup
import json
import os
import time

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
    requests.post(
        "https://api.line.me/v2/bot/message/broadcast",
        headers=headers,
        json=body
    )


def check_fire():
    print("=== チェック開始 ===")

    html = requests.get(URL, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")

    rows = soup.select("div.news_body li")
    current = []

    for r in rows:
        date = r.select_one("span").text.strip()
        title = r.select_one("a").text.strip()
        link = "https://sc.city.kawasaki.jp" + r.select_one("a")["href"]

        if "多摩区" in title and "消防車が出場" in title:
            current.append({"date": date, "title": title, "link": link})

    try:
        with open("prev.json", "r", encoding="utf-8") as f:
            prev = json.load(f)
    except FileNotFoundError:
        prev = []

    new_items = [x for x in current if x not in prev]

    for item in new_items:
        msg = f"""🔥 川崎市 消防出動情報
{item['date']}
{item['title']}
{item['link']}"""
        send_line(msg)

    with open("prev.json", "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)

    print("=== チェック終了 ===")


# -----------------------------
# 1分ループ
# -----------------------------
if __name__ == "__main__":
    while True:
        try:
            check_fire()
        except Exception as e:
            print("エラー発生:", e)

        print("=== 60秒待機 ===")
        time.sleep(60)
