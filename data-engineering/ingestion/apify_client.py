import os, json, hashlib, time
from datetime import date
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()
RAW_DIR = Path("data/raw/apify"); RAW_DIR.mkdir(parents=True, exist_ok=True)
URL = "https://api.apify.com/v2/acts/automation-lab~wuzzuf-jobs-scraper/run-sync-get-dataset-items"

def _week():
    y, w, _ = date.today().isocalendar()
    return f"{y}-W{w:02d}"

def fetch(query, max_items=50, posted_within_days=30, force=False):
    body = {"searchQueries": [query], "location": "Egypt",
            "postedWithinDays": posted_within_days, "maxItems": max_items}
    key = hashlib.sha1(json.dumps({**body, "week": _week()}, sort_keys=True).encode()).hexdigest()[:16]
    path = RAW_DIR / f"{key}.json"
    if path.exists() and not force:
        print(f"CACHE HIT {query}")
        return json.loads(path.read_text())
    headers = {"Authorization": f"Bearer {os.environ['APIFY_TOKEN']}"}
    r = requests.post(URL, headers=headers, json=body, timeout=300)
    r.raise_for_status()
    items = r.json()
    payload = {"fetched_at": int(time.time()), "input": body, "items": items}
    path.write_text(json.dumps(payload, ensure_ascii=False))
    print(f"API CALL {query} -> {len(items)} jobs")
    return payload

if __name__ == "__main__":
    out = fetch("data engineer", max_items=10)
    if out["items"]:
        print(sorted(out["items"][0].keys()))
