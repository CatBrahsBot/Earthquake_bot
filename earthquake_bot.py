import os
import time
import json
import requests
from datetime import datetime, timedelta, timezone

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MIN_MAGNITUDE = float(os.getenv("MIN_MAGNITUDE", 4))
POLL_SECONDS = int(os.getenv("POLL_SECONDS", 30))
USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
SEEN_FILE = "seen.json"

# === STATE ===
seen = set()
last_check = datetime.now(timezone.utc) - timedelta(minutes=5)

# === HELPERS ===
def load_seen():
    """Load seen quake IDs from file."""
    global seen
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                seen = set(json.load(f))
        except Exception as e:
            print("Error loading seen file:", e)
            seen = set()

def save_seen():
    """Persist seen quake IDs to file."""
    try:
        with open(SEEN_FILE, "w") as f:
            json.dump(list(seen), f)
    except Exception as e:
        print("Error saving seen file:", e)

def fetch_quakes():
    """Get recent earthquakes since last check."""
    global last_check
    # 2-minute overlap so we don’t miss delayed reports
    start = (last_check - timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%S") + "Z"
    params = {
        "format": "geojson",
        "starttime": start,
        "minmagnitude": MIN_MAGNITUDE,
        "orderby": "time"
    }
    try:
        r = requests.get(USGS_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json().get("features", [])
    except Exception as e:
        print("Error fetching quakes:", e)
        data = []
    last_check = datetime.now(timezone.utc)





















