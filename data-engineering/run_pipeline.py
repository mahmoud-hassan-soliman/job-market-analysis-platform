"""Automated pipeline: collect -> load -> verify. Dry run unless --go."""
import sys, json, argparse, datetime, requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from ingestion.run_scale import fetch, SOURCES, ALL_ROLES
from processing.load import load_all, connect


def fee(source):
    return 0.005 if source == "wuzzuf" else 0.0


def collect(sources, roles, cap, window):
    stats = {}
    for s in sources:
        st = {"raw": 0, "api": 0, "cached": 0, "failed": 0, "stopped": None, "est_cost": 0.0}
        price = SOURCES[s][1]
        for role in roles:
            try:
                items, cached = fetch(s, role, cap, window)
            except RuntimeError as e:          # actor run failed: skip this search
                st["failed"] += 1
                print(f"SKIP  {s}/{role}: {e}")
                continue
            except requests.RequestException as e:   # network/credit problem: stop this source
                st["stopped"] = f"{role}: {e}"
                print(f"STOP  {s} at {role}: {e}")
                break
            st["raw"] += len(items)
            if cached:
                st["cached"] += 1
            else:
                st["api"] += 1
                st["est_cost"] += len(items) * price / 1000 + fee(s)
            print(f"{'CACHE' if cached else 'API  '} {s}/{role}: {len(items)}")
        stats[s] = st
    return stats


def db_count():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM jobs")
    n = cur.fetchone()[0]
    conn.close()
    return n


def verify():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT count(*), count(posted_at), count(description), count(location_city), "
                "max(posted_at)::date FROM jobs")
    total, dated, desc, city, newest = cur.fetchone()
    conn.close()
    pct = lambda n: round(100 * n / total) if total else 0
    checks = {
        "jobs in DB > 0": total > 0,
        "descriptions >= 90%": pct(desc) >= 90,
        "posted date >= 90%": pct(dated) >= 90,
        "newest posting within 14 days": bool(newest) and (datetime.date.today() - newest).days <= 14,
    }
    print(f"\nVERIFY: total={total} dated={pct(dated)}% description={pct(desc)}% city={pct(city)}% newest={newest}")
    for name, ok in checks.items():
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    return checks


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--go", action="store_true", help="actually collect and load (spends credit)")
    ap.add_argument("--window", choices=["week", "month"], default="week")
    ap.add_argument("--cap", type=int, default=50)
    ap.add_argument("--sources", default="linkedin,wuzzuf")
    ap.add_argument("--roles", help="comma-separated; default is the full role list")
    ap.add_argument("--skip-collect", action="store_true", help="only load and verify")
    a = ap.parse_args()
    sources = [x.strip() for x in a.sources.split(",")]
    roles = [r.strip() for r in a.roles.split(",")] if a.roles else ALL_ROLES
    maxc = sum(len(roles) * (a.cap * SOURCES[s][1] / 1000 + fee(s)) for s in sources)
    print(f"PLAN: sources={sources} roles={len(roles)} cap={a.cap} window={a.window}")
    print(f"max cost at listed price: ${maxc:.2f} (real cost is lower when searches return fewer than the cap)")
    if not a.go:
        print("DRY RUN. Add --go to run.")
        sys.exit(0)
    before = db_count()
    stats = {} if a.skip_collect else collect(sources, roles, a.cap, a.window)
    load_all()
    after = db_count()
    checks = verify()
    est = sum(s["est_cost"] for s in stats.values())
    print(f"\nSUMMARY: unique jobs {before} -> {after} (+{after - before}), estimated cost ${est:.2f}")
    Path("data").mkdir(exist_ok=True)
    with open("data/pipeline_runs.jsonl", "a") as f:
        f.write(json.dumps({"time": datetime.datetime.now().isoformat(timespec="seconds"),
                            "window": a.window, "cap": a.cap, "before": before, "after": after,
                            "new_unique": after - before, "est_cost": round(est, 3),
                            "stats": stats, "checks": checks}) + "\n")
    sys.exit(0 if all(checks.values()) else 1)
