import requests
import time

BASE = "https://codeforces.com/api"

def get_user_info(handle):
    r = requests.get(f"{BASE}/user.info?handles={handle}")
    r.raise_for_status()
    return r.json()["result"][0]

def get_submissions(handle, count=500):
    time.sleep(1)  # CF rate limit — be respectful
    r = requests.get(f"{BASE}/user.status?handle={handle}&count={count}")
    r.raise_for_status()
    return r.json()["result"]

def get_rating_history(handle):
    time.sleep(1)
    r = requests.get(f"{BASE}/user.rating?handle={handle}")
    r.raise_for_status()
    return r.json()["result"]