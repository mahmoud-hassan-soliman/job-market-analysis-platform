import os, sys, json, time, requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.environ["APIFY_TOKEN"]
H = {"Authorization": f"Bearer {TOKEN}"}
actor, name, inp = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])

r = requests.post(f"https://api.apify.com/v2/acts/{actor}/runs?waitForFinish=240",
                  headers=H, json=inp, timeout=300)
r.raise_for_status()
run = r.json()["data"]
while run["status"] in ("READY", "RUNNING"):
    time.sleep(5)
    run = requests.get(f"https://api.apify.com/v2/actor-runs/{run['id']}", headers=H).json()["data"]
items = requests.get(f"https://api.apify.com/v2/datasets/{run['defaultDatasetId']}/items", headers=H).json()
Path("data/raw/probe").mkdir(parents=True, exist_ok=True)
json.dump(items, open(f"data/raw/probe/{name}.json", "w"), ensure_ascii=False, indent=2)

def filled(*keys):
    return sum(1 for i in items if any(i.get(k) for k in keys))
n = len(items)
print(f"status={run['status']} jobs={n} cost=${run.get('usageTotalUsd')}")
if n:
    print("fields:", sorted(items[0].keys()))
    txt = json.dumps(items).lower()
    print("mentions egypt:", txt.count("egypt"), "| cairo:", txt.count("cairo"))
