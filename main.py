
import os
import json
import urllib.request
import urllib.error

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

    try:
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode("utf-8"))
            print(result)
    except urllib.error.HTTPError as error:
        print("Telegram error:")
        print(error.read().decode("utf-8"))
        raise

if __name__ == "__main__":
    send_message("⚽ سڵاو! ئەمە تاقیکردنەوەی بۆتی هەواڵی تۆپی پێیە.")
