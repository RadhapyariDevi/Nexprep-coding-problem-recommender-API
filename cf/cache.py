import json
import os
import time

CACHE_DIR = "codeforces/data"
CACHE_EXPIRY_HOURS = 24

os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_path(handle, data_type):
    return f"{CACHE_DIR}/{handle}_{data_type}.json"

def save(handle, data_type, data):
    payload = {
        "fetched_at": time.time(),
        "data": data
    }
    with open(_cache_path(handle, data_type), "w") as f:
        json.dump(payload, f)

def load(handle, data_type):
    path = _cache_path(handle, data_type)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        payload = json.load(f)
    age_hours = (time.time() - payload["fetched_at"]) / 3600
    if age_hours > CACHE_EXPIRY_HOURS:
        return None  # stale, refetch
    return payload["data"]

def get_or_fetch(handle, data_type, fetch_fn):
    cached = load(handle, data_type)
    if cached:
        print(f"[cache] loaded {data_type} for {handle}")
        return cached
    print(f"[fetch] hitting API for {data_type} — {handle}")
    data = fetch_fn()
    save(handle, data_type, data)
    return data