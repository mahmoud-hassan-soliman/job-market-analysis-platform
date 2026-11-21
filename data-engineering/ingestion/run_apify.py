import sys, time
import requests
from ingestion.apify_client import fetch
from ingestion.queries import ROLES

def main():
    print(f"{len(ROLES)} Wuzzuf searches planned (max 50 jobs each)")
    if "--go" not in sys.argv:
        print("Dry run, nothing spent. Add --go to execute.")
        return
    for role in ROLES:
        try:
            fetch(role, max_items=50)
        except requests.RequestException as e:
            print("STOP:", e)
            return
        time.sleep(1)

main()
