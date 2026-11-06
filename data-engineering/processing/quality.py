"""Data-quality metrics: missing % per field and jobs invalid for analysis."""
import csv
from pathlib import Path
from processing.load import connect

FIELDS = ["title", "company", "description", "location_raw", "posted_at"]
VALID = """(title IS NOT NULL AND btrim(title) <> '' AND company IS NOT NULL AND btrim(company) <> ''
  AND description IS NOT NULL AND length(description) >= 100
  AND location_raw IS NOT NULL AND btrim(location_raw) <> ''
  AND posted_at IS NOT NULL AND coalesce(is_duplicate, false) = false)"""


def miss(f):
    return f"round(100.0 * avg((({f}) IS NULL OR btrim(({f})::text) = '')::int), 1)"


def main():
    conn = connect()
    cur = conn.cursor()
    cur.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS is_duplicate boolean DEFAULT false")
    cur.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS is_valid_for_analysis boolean")
    cur.execute(f"UPDATE jobs SET is_valid_for_analysis = {VALID}")
    conn.commit()
    cur.execute(f"""SELECT coalesce(country,'ALL'), coalesce(source,'ALL'), count(*),
        {', '.join(miss(f) for f in FIELDS)},
        count(*) FILTER (WHERE NOT is_valid_for_analysis)
        FROM jobs GROUP BY GROUPING SETS ((country, source), (country), (source), ()) ORDER BY 1, 2""")
    head = ["country", "source", "jobs"] + [f"miss_{f}_%" for f in FIELDS] + ["invalid"]
    rows = cur.fetchall()
    Path("export").mkdir(exist_ok=True)
    with open("export/quality_report.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(head)
        w.writerows(rows)
    print(" | ".join(head))
    for r in rows:
        print(" | ".join(str(x) for x in r))
    cur.execute("""SELECT count(*) FILTER (WHERE title IS NULL OR btrim(title) = ''),
        count(*) FILTER (WHERE company IS NULL OR btrim(company) = ''),
        count(*) FILTER (WHERE description IS NULL OR length(description) < 100),
        count(*) FILTER (WHERE location_raw IS NULL OR btrim(location_raw) = ''),
        count(*) FILTER (WHERE posted_at IS NULL),
        count(*) FILTER (WHERE coalesce(is_duplicate, false)),
        count(*) FILTER (WHERE is_valid_for_analysis) FROM jobs""")
    names = ["no_title", "no_company", "no_or_short_description", "no_location", "no_posted_date",
             "near_duplicate", "VALID_UNIQUE_FOR_ANALYSIS"]
    print(dict(zip(names, cur.fetchone())))


if __name__ == "__main__":
    main()
