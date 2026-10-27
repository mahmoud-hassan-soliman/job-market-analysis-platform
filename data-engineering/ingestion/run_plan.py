import sys, time
import requests
from ingestion.jsearch_client import fetch
from ingestion.queries import plan

def main():
    qs = plan()
    period = "month" if "--month" in sys.argv else "week"
    pages = 2 if "--page2" in sys.argv else 1
    print(f"{len(qs)} queries planned (date_posted={period}, max pages={pages})")
    if "--go" not in sys.argv:
        print("Dry run, no requests spent. Add --go to execute.")
        return
    for q in qs:
        for p in range(1, pages + 1):
            try:
                out = fetch(q, page=p, date_posted=period)
            except requests.RequestException as e:
                print("STOP:", e)
                return
            n = len(out["response"]["data"]["jobs"])
            print(f"  p{p} -> {n} jobs")
            time.sleep(1)
            if n < 10:
                break

main()
