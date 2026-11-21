import os, re, json, glob, hashlib
from collections import Counter
from datetime import datetime, timezone
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from processing.clean import normalize_city, normalize_country, parse_iso, from_unix, parse_arabic_relative
from processing.extra_sources import normalize_linkedin, normalize_bayt

load_dotenv()

COLUMNS = ["job_id", "source", "title", "company", "description", "posted_at",
           "location_raw", "location_city", "country", "is_remote", "employment_type",
           "salary_min", "salary_max", "salary_period", "apply_link", "publisher",
           "source_skills", "career_level", "experience_years_min"]
# Dedup preference: richer source wins when the same title|company appears twice.
SOURCE_RANK = {"apify_wuzzuf": 4, "linkedin": 3, "jsearch": 2, "bayt": 1}


def clean(v):
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def normalize_jsearch(j, ref=None):
    loc = j.get("job_location")
    return {
        "job_id": j.get("job_id"), "source": "jsearch",
        "title": j.get("job_title"), "company": j.get("employer_name"),
        "description": j.get("job_description"),
        "posted_at": parse_iso(j.get("job_posted_at_datetime_utc"))
                     or from_unix(j.get("job_posted_at_timestamp"))
                     or parse_arabic_relative(j.get("job_posted_at"), ref),
        "location_raw": loc, "location_city": normalize_city(loc),
        "country": normalize_country(j.get("job_country")),
        "is_remote": j.get("job_is_remote"),
        "employment_type": j.get("job_employment_type"),
        "salary_min": j.get("job_min_salary"), "salary_max": j.get("job_max_salary"),
        "salary_period": j.get("job_salary_period"),
        "apply_link": j.get("job_apply_link"), "publisher": j.get("job_publisher"),
        "source_skills": None, "career_level": None, "experience_years_min": None,
    }


def normalize_apify(j):
    sal, exp = j.get("salary") or {}, j.get("experienceYears") or {}
    types = j.get("jobTypes") or []
    wp = clean(j.get("workplace"))
    desc = "\n\n".join(x for x in (clean(j.get("description")), clean(j.get("requirements"))) if x)
    return {
        "job_id": j.get("jobId"), "source": "apify_wuzzuf",
        "title": j.get("title"), "company": j.get("company"),
        "description": desc or None,
        "posted_at": parse_iso(j.get("postedAt")),
        "location_raw": j.get("location"),
        "location_city": normalize_city(j.get("location")) or normalize_city(j.get("city")),
        "country": normalize_country(j.get("country")),
        "is_remote": None if not wp else wp == "Remote",
        "employment_type": types[0] if types else None,
        "salary_min": sal.get("min"), "salary_max": sal.get("max"),
        "salary_period": sal.get("period"),
        "apply_link": j.get("url"), "publisher": "Wuzzuf",
        "source_skills": j.get("skills") or None,
        "career_level": j.get("careerLevel"), "experience_years_min": exp.get("min"),
    }


SOURCES = [  # (raw folder, how to get the job list from a file, normalizer)
    ("jsearch", lambda d: d["response"]["data"]["jobs"], normalize_jsearch),
    ("apify", lambda d: d["items"] if isinstance(d, dict) else d, normalize_apify),
    ("linkedin", lambda d: d, normalize_linkedin),
    ("bayt", lambda d: d, normalize_bayt),
]


def read_raw():
    rows = []
    for folder, getter, fn in SOURCES:
        for f in sorted(glob.glob(f"data/raw/{folder}/*.json")):
            d = json.load(open(f))
            ref = (parse_iso(d.get("fetched_at")) if isinstance(d, dict) else None) \
                or datetime.fromtimestamp(os.path.getmtime(f), tz=timezone.utc)
            for i, j in enumerate(getter(d)):
                out = fn(j, ref) if folder == "jsearch" else fn(j)
                row = {k: clean(v) for k, v in out.items()}
                row["raw_ref"] = f"{f}#{i}"
                rows.append(row)
    return rows


def connect():
    return psycopg2.connect(host="localhost", port=5433,
        user=os.environ["POSTGRES_USER"], password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"])


def internal_id(source, source_job_id):
    return "j_" + hashlib.sha1(f"{source}:{source_job_id}".encode()).hexdigest()[:16]


def dedupe_by_source_id(rows):
    # same source + same source_job_id = same ad. Richer copy wins, later raw file wins ties.
    best, rejected = {}, Counter()
    for r in rows:
        if not r["job_id"]:
            rejected["missing source_job_id"] += 1
            continue
        if not r["title"]:
            rejected["missing title"] += 1
            continue
        key = (r["source"], r["job_id"])
        size = len(r["description"] or "")
        if key not in best or size >= best[key][0]:
            best[key] = (size, r)
    kept = [r for _, r in best.values()]
    stats = {"ingested": len(rows), "stored": len(kept),
             "exact_duplicates": len(rows) - sum(rejected.values()) - len(kept),
             "rejected": dict(rejected)}
    return kept, stats


DB_COLS = ["job_id", "source_job_id", "raw_ref"] + COLUMNS[1:]


def load_all():
    kept, stats = dedupe_by_source_id(read_raw())
    final = [(internal_id(r["source"], r["job_id"]), r["job_id"], r.get("raw_ref"),
              *[r[c] for c in COLUMNS[1:]]) for r in kept]
    sets = ", ".join(f"{c}=EXCLUDED.{c}" for c in DB_COLS[1:])
    conn = connect()
    with conn, conn.cursor() as cur:
        execute_values(cur, f"INSERT INTO jobs ({', '.join(DB_COLS)}) VALUES %s "
                            f"ON CONFLICT (job_id) DO UPDATE SET {sets}", final)
    stats["by_source"] = dict(Counter(r["source"] for r in kept))
    print(stats)
    return stats


if __name__ == "__main__":
    load_all()
