import time
import requests
from datetime import datetime, timedelta

# === CONFIG ===
TELEGRAM_TOKEN = "TELEGRAM_TOKEN"
CHAT_ID = "CHAT_ID"
MIN_MAGNITUDE = 2

# === URLs ===
USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

# Store already-sent quake IDs
seen = set()


def fetch_quakes():
    # Get quakes in the last hour above threshold
    starttime = (datetime.utcnow() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
    params = {
        "format": "geojson",
        "starttime": starttime,
        "minmagnitude": MIN_MAGNITUDE
    }
    r = requests.get(USGS_URL, params=params)
    return r.json().get("features", [])


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)


def main():
    print("🌍 Earthquake alert bot running...")
    while True:
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

        time.sleep(300)  # wait 5 minutes between checks


if __name__ == "__main__":
    main()







