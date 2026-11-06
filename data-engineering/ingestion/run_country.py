"""Country-aware LinkedIn collection with a hard budget guard.
  python -m ingestion.run_country --countries sa,ae            # dry run
  python -m ingestion.run_country --countries sa,ae --go       # spend
  python -m ingestion.run_country --countries sa --smoke --go  # 10-job test
"""
import argparse, collections, datetime as dt, hashlib, json, os, sys, time
from pathlib import Path
import requests
from dotenv import load_dotenv
from processing.clean import resolve_country

load_dotenv(".env")
ACTOR = "meka.im~linkedin-jobs-scraper"
PRICE = 0.30 / 1000
API = "https://api.apify.com/v2"
LOCATION = {"eg": "Egypt", "sa": "Saudi Arabia", "ae": "United Arab Emirates"}
ROLES = ["software engineer", "data engineer", "data scientist", "devops engineer",
         "frontend developer", "backend developer", "cybersecurity engineer",
         "machine learning engineer"]
RAW, LEDGER = Path("data/raw/linkedin"), Path("data/spend_ledger.jsonl")


def token():
    for n in ("APIFY_TOKEN", "APIFY_API_TOKEN", "APIFY_API_KEY"):
        if os.environ.get(n):
            return os.environ[n]
    sys.exit("No Apify token in .env (expected APIFY_TOKEN). Add it there; never paste it in chat.")


def spent():
    if not LEDGER.exists():
        return 0.0
    return sum(json.loads(l)["est_usd"] for l in LEDGER.read_text().splitlines() if l.strip())


def run_actor(inp, max_usd):
    h = {"Authorization": f"Bearer {token()}"}
    r = requests.post(f"{API}/acts/{ACTOR}/runs", headers=h, json=inp, timeout=300,
                      params={"waitForFinish": 240, "maxTotalChargeUsd": round(max_usd, 4)})
    r.raise_for_status()
    run, t0 = r.json()["data"], time.time()
    while run["status"] in ("READY", "RUNNING") and time.time() - t0 < 600:
        time.sleep(5)
        run = requests.get(f"{API}/actor-runs/{run['id']}", headers=h, timeout=60).json()["data"]
    if run["status"] in ("READY", "RUNNING"):
        requests.post(f"{API}/actor-runs/{run['id']}/abort", headers=h, timeout=60)
        raise RuntimeError("run timed out, aborted")
    if run["status"] != "SUCCEEDED":
        raise RuntimeError(f"run {run['status']}")
    d = requests.get(f"{API}/datasets/{run['defaultDatasetId']}/items", headers=h,
                     params={"clean": "true"}, timeout=120)
    d.raise_for_status()
    return d.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--countries", default="sa,ae")
    ap.add_argument("--roles", default=",".join(ROLES))
    ap.add_argument("--cap", type=int, default=100)
    ap.add_argument("--budget", type=float, default=0.70, help="total USD cap for ALL runs in the ledger")
    ap.add_argument("--window", default="pastMonth")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--go", action="store_true")
    a = ap.parse_args()
    countries = [c.strip().lower() for c in a.countries.split(",")]
    roles = ["software engineer"] if a.smoke else [r.strip() for r in a.roles.split(",")]
    cap = 10 if a.smoke else a.cap
    plan = [(c, r) for c in countries for r in roles]
    worst = len(plan) * cap * PRICE
    print(f"searches={len(plan)} cap={cap} max_cost=${worst:.3f} spent_so_far=${spent():.3f} budget=${a.budget:.2f}")
    if spent() + worst > a.budget:
        sys.exit("REFUSED: plan would exceed the budget. Lower --cap or --roles.")
    if not a.go:
        print("dry run - add --go to spend")
        return
    RAW.mkdir(parents=True, exist_ok=True)
    stats, fails = collections.Counter(), 0
    for c, r in plan:
        inp = {"keywords": r, "location": LOCATION[c], "datePosted": a.window, "limitPerSource": cap}
        wk = dt.date.today().isocalendar()[:2]
        key = hashlib.sha1(json.dumps({"a": ACTOR, "i": inp, "w": wk}, sort_keys=True).encode()).hexdigest()[:16]
        f = RAW / f"{key}.json"
        if f.exists():
            print(f"cached  {c} {r}")
            continue
        try:
            items = run_actor(inp, cap * PRICE + 0.02)
        except Exception as e:
            fails += 1
            print(f"FAILED  {c} {r}: {e}")
            if fails >= 3:
                sys.exit("3 failures in a row, stopping to protect credit")
            continue
        fails = 0
        for it in items:
            it["_search_country"], it["_search_role"] = c.upper(), r
        f.write_text(json.dumps(items))
        with LEDGER.open("a") as lg:
            lg.write(json.dumps({"ts": dt.datetime.now().isoformat(timespec="seconds"), "country": c,
                                 "role": r, "items": len(items), "est_usd": round(len(items) * PRICE, 5)}) + "\n")
        got = collections.Counter(resolve_country(i.get("location"), fallback=c.upper()) for i in items)
        stats.update(got)
        print(f"saved   {c} {r}: {len(items)} jobs {dict(got)}")
    print(f"done. resolved countries={dict(stats)} total_spent_est=${spent():.3f}")
    if a.smoke and not stats:
        sys.exit(1)


if __name__ == "__main__":
    main()
