import os, sys, json, time, hashlib, argparse, datetime, requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
H = {"Authorization": f"Bearer {os.environ['APIFY_TOKEN']}"}

ROLES = ["software engineer", "data engineer", "data analyst", "data scientist",
         "machine learning engineer", "devops engineer", "backend developer",
         "frontend developer", "full stack developer", "python developer",
         "AI engineer", "qa engineer", "product manager", "cloud engineer"]
EXTRA_IT = ["system administrator", "network engineer", "cybersecurity engineer",
            "mobile developer", "ui ux designer", "java developer", ".net developer",
            "php developer", "business analyst", "project manager", "it support",
            "embedded engineer", "data architect"]
BUSINESS = ["accountant", "financial analyst", "auditor", "digital marketing",
            "marketing manager", "social media specialist", "hr specialist", "recruiter"]
ALL_ROLES = ROLES + EXTRA_IT + BUSINESS

# source: (actor, listed price per 1K jobs, input builder)
SOURCES = {
    "linkedin": ("meka.im~linkedin-jobs-scraper", 0.30,
        lambda role, cap, window="month": {"keywords": role, "location": "Egypt",
                           "datePosted": "pastWeek" if window == "week" else "pastMonth",
                           "limitPerSource": cap}),
    "bayt": ("parsebird~bayt-jobs-scraper", 1.99,
        lambda role, cap, window="month": {"startUrl": f"https://www.bayt.com/en/egypt/jobs/{role.lower().replace(' ', '-')}-jobs/",
                           "results_wanted": cap, "max_pages": cap // 10 + 2}),
    "wuzzuf": ("automation-lab~wuzzuf-jobs-scraper", 0.92,
        lambda role, cap, window="month": {"searchQueries": [role], "location": "Egypt",
                           "postedWithinDays": 7 if window == "week" else 30, "maxItems": cap}),
}
FOLDER = {"wuzzuf": "apify"}  # loader reads Wuzzuf files from data/raw/apify

def week():
    y, w, _ = datetime.date.today().isocalendar()
    return f"{y}-W{w:02d}"

def fetch(source, role, cap, window="month"):
    actor, _, mk = SOURCES[source]
    inp = mk(role, cap, window)
    key = hashlib.sha1(json.dumps({"a": actor, "i": inp, "w": week()}, sort_keys=True).encode()).hexdigest()[:16]
    path = Path(f"data/raw/{FOLDER.get(source, source)}/{key}.json")
    if path.exists():
        return json.load(open(path)), True
    r = requests.post(f"https://api.apify.com/v2/acts/{actor}/runs?waitForFinish=240",
                      headers=H, json=inp, timeout=300)
    r.raise_for_status()
    run = r.json()["data"]
    while run["status"] in ("READY", "RUNNING"):
        time.sleep(5)
        run = requests.get(f"https://api.apify.com/v2/actor-runs/{run['id']}", headers=H, timeout=60).json()["data"]
    if run["status"] != "SUCCEEDED":
        raise RuntimeError(f"run ended as {run['status']}")
    items = requests.get(f"https://api.apify.com/v2/datasets/{run['defaultDatasetId']}/items",
                         headers=H, timeout=120).json()
    path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(items, open(path, "w"), ensure_ascii=False)
    return items, False

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("source", choices=SOURCES)
    ap.add_argument("--cap", type=int, default=200)
    ap.add_argument("--roles", help="comma-separated, overrides the default list")
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--window", choices=["week", "month"], default="month")
    a = ap.parse_args()
    roles = [r.strip() for r in a.roles.split(",")] if a.roles else ROLES
    price = SOURCES[a.source][1]
    print(f"{len(roles)} {a.source} searches planned, cap {a.cap} each: {roles}")
    fee = 0.005 if a.source == "wuzzuf" else 0
    print(f"max cost at listed price: ${len(roles) * (a.cap * price / 1000 + fee):.2f}")
    if not a.go:
        print("DRY RUN. Add --go to spend.")
        sys.exit()
    total = 0
    for role in roles:
        try:
            items, cached = fetch(a.source, role, a.cap, a.window)
        except RuntimeError as e:
            print(f"SKIP '{role}': {e}")
            continue
        except requests.RequestException as e:
            print(f"STOP at '{role}': {e}")
            break
        total += len(items)
        print(f"{'CACHE' if cached else 'API  '} {role}: {len(items)} jobs")
    print(f"total jobs this run: {total}")
