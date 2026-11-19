"""Adds search_role and role_category to jobs from the _search_role tag in raw LinkedIn files."""
import glob, json
from processing.extra_sources import normalize_linkedin
from processing.load import connect

BIZ = {"accountant", "financial analyst", "marketing specialist", "hr specialist",
       "sales manager", "business analyst", "project manager", "operations manager"}
CLOUD = {"cloud engineer", "solutions architect", "site reliability engineer"}
IT = {"network engineer", "system administrator"}


def category(role):
    if role in BIZ:
        return "business"
    if role in CLOUD:
        return "cloud"
    if role in IT:
        return "it"
    return "tech" if role else None


def main():
    conn = connect()
    cur = conn.cursor()
    cur.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS search_role text")
    cur.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS role_category text")
    seen = {}
    for f in sorted(glob.glob("data/raw/linkedin/*.json")):
        items = json.load(open(f))
        if not isinstance(items, list):
            continue
        for it in items:
            role = it.get("_search_role")
            if not role:
                continue
            jid = normalize_linkedin(it).get("job_id")
            if jid and jid not in seen:
                seen[jid] = role
    cur.execute("UPDATE jobs SET search_role = NULL, role_category = NULL")
    cur.executemany("UPDATE jobs SET search_role = %s, role_category = %s WHERE source = 'linkedin' AND job_id = %s",
                    [(r, category(r), j) for j, r in seen.items()])
    conn.commit()
    cur.execute("""SELECT country, coalesce(role_category, 'unknown'), count(*),
                   count(*) FILTER (WHERE is_valid_for_analysis)
                   FROM jobs GROUP BY 1, 2 ORDER BY 1, 2""")
    print("country | category | jobs | valid")
    for row in cur.fetchall():
        print(" | ".join(str(x) for x in row))


if __name__ == "__main__":
    main()
