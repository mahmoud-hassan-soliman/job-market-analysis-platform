import os, json, hashlib, time
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()
RAW_DIR = Path("data/raw/jsearch"); RAW_DIR.mkdir(parents=True, exist_ok=True)
URL = "https://jsearch.p.rapidapi.com/search-v2"
from datetime import date
def _week():
    y, w, _ = date.today().isocalendar()
    return f"{y}-W{w:02d}"

def _headers():
    return {"X-RapidAPI-Key": os.environ["RAPIDAPI_KEY"],
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}

def fetch(query, page=1, country="eg", date_posted="week", force=False):
    params = {"query": query, "page": page, "num_pages": 1,
              "country": country, "date_posted": date_posted}
    key = hashlib.sha1(json.dumps({**params, "week": _week()}, sort_keys=True).encode()).hexdigest()[:16]
    path = RAW_DIR / f"{key}.json"
    if path.exists() and not force:
        print(f"CACHE HIT {query} p{page}")
        return json.loads(path.read_text())
    r = requests.get(URL, headers=_headers(), params=params, timeout=90)
    r.raise_for_status()
    payload = {"fetched_at": int(time.time()), "params": params, "response": r.json()}
    path.write_text(json.dumps(payload, ensure_ascii=False))
    print(f"API CALL {query} p{page} (remaining: {r.headers.get('x-ratelimit-requests-remaining')})")
    return payload

if __name__ == "__main__":
    out = fetch("data engineer in Cairo, Egypt")
    jobs = out["response"]["data"]["jobs"]
    print(len(jobs), "jobs")
