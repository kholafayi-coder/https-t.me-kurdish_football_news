
import os
import json
import urllib.request

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = "@kurdish_football_news"

def send_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHANNEL,
        "text": message
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    if not result.get("ok"):
        raise RuntimeError(result)

    print("Message sent successfully!")

if __name__ == "__main__":
    send_message(
        "⚽ سڵاو لە هەموو خۆشەویستانی تۆپی پێ!\n\n"
        "بە زوویی نوێترین هەواڵەکانی تۆپی پێی ئەورووپا "
        "بە زمانی کوردیی سۆرانی لێرە بڵاودەکەینەوە. ❤️"
    )
