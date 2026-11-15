
import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = "@kurdish_football_news"

FEED_URL = "https://www.theguardian.com/football/rss"
SEEN_FILE = "seen.json"
MAX_NEWS_PER_RUN = 3

IMPORTANT_WORDS = [
    "premier league", "la liga", "bundesliga", "serie a",
    "ligue 1", "champions league", "europa league",
    "transfer", "signing", "signed", "deal agreed",
    "injury", "sacked", "appointed", "manager",
    "final", "semi-final", "derby", "title race",
    "record", "relegation", "qualify", "eliminated",
    "arsenal", "chelsea", "liverpool", "manchester city",
    "manchester united", "tottenham", "newcastle",
    "real madrid", "barcelona", "atletico",
    "bayern", "dortmund", "leverkusen",
    "inter", "juventus", "milan", "napoli",
    "paris saint-germain", "psg", "marseille"
]


def load_seen():
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as file:
            return set(json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as file:
        json.dump(list(seen)[-500:], file, ensure_ascii=False)


def send_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHANNEL,
        "text": message,
        "disable_web_page_preview": False
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))

    if not result.get("ok"):
        raise RuntimeError(result)

    print("News sent successfully!")


def get_news():
    request = urllib.request.Request(
        FEED_URL,
        headers={"User-Agent": "KurdFootballNewsBot/1.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    channel = root.find("channel")

    if channel is None:
        raise RuntimeError("RSS channel not found")

    return channel.findall("item")


def main():
    seen = load_seen()
    now = datetime.now(timezone.utc)
    news_items = []

    for item in get_news():
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        guid = item.findtext("guid", "").strip() or link
        pub_date = item.findtext("pubDate", "").strip()

        if not title or not link or not guid or not pub_date:
            continue

        if guid in seen:
            continue

        try:
            published = parsedate_to_datetime(pub_date)

            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)

            published = published.astimezone(timezone.utc)
        except (TypeError, ValueError):
            continue

        if published > now + timedelta(minutes=5):
            continue

        if now - published > timedelta(hours=24):
            continue

        text = title.casefold()

        if not any(word in text for word in IMPORTANT_WORDS):
            continue

        news_items.append({
            "title": title,
            "link": link,
            "guid": guid,
            "published": published
        })

    news_items.sort(key=lambda news: news["published"])

    for news in news_items[:MAX_NEWS_PER_RUN]:
        message = (
            "⚽ هەواڵی تۆپی پێ\n\n"
            f"{news['title']}\n\n"
            f"🔗 سەرچاوە: {news['link']}"
        )

        send_message(message)
        seen.add(news["guid"])
        save_seen(seen)

    print(f"Finished. {min(len(news_items), MAX_NEWS_PER_RUN)} news sent.")


if __name__ == "__main__":
    main()
