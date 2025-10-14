import os
import sys
import time
import requests
import threading
from datetime import datetime, timedelta
from flask import Flask

# === LIVE LOGGING FIX ===
sys.stdout.reconfigure(line_buffering=True)

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MIN_MAGNITUDE = 2

# === URLS ===
USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

# === KEEP RENDER ALIVE ===
app = Flask(__name__)

@app.route('/')
def home():
    return "🌍 CatBrahsQuakeAlertBot is running and monitoring earthquakes!"

def run_server():
    app.run(host="0.0.0.0", port=8080)

# === FUNCTIONS ===
seen = set()

def fetch_quakes():
    """Get quakes from the past hour above the magnitude threshold."""
    starttime = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S") + "Z"
    params = {
        "format": "geojson",
        "starttime": starttime,
        "minmagnitude": MIN_MAGNITUDE
    }
    r = requests.get(USGS_URL, params=params)
    if r.status_code != 200:
        print("Error fetching data:", r.text)
        return []
    return r.json().get("features", [])


def send_telegram(msg):
    """Send message to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print("Error sending message:", response.text)


def main():
    print("🌍 Earthquake alert bot running...")
    while True:
        print("Fetching new quakes...")
        quakes = fetch_quakes()
        print("Fetched", len(quakes), "earthquakes")

        for q in quakes:
            qid = q["id"]
            if qid not in seen:
                seen.add(qid)
                props = q["properties"]
                mag = props["mag"]
                place = props["place"]
                url = props["url"]
                time_ms = props["time"]
                time_str = datetime.utcfromtimestamp(time_ms / 1000).strftime("%Y-%m-%d %H:%M UTC")

                msg = f"*🌎 M{mag} earthquake*\n_{place}_\n🕒 `{time_str}`\n[USGS report]({url})"
                send_telegram(msg)
                print("Sent:", msg)

        time.sleep(300)  # check every 5 minutes


if __name__ == "__main__":
    # Start small Flask server to keep Render alive
    threading.Thread(target=run_server).start()
    main()










