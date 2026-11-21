"""Export cleaned jobs, a raw sample from the same batch, the mapping between them, and the counts."""
import csv, json, random, datetime, collections
from pathlib import Path
from processing.load import SOURCES, connect

GET = {s[0]: s[1] for s in SOURCES}
NORM = {s[0]: s[2] for s in SOURCES}
COLS = ["job_id", "source", "source_job_id", "raw_ref", "title", "company", "description", "posted_at",
        "location_raw", "location_city", "country", "is_remote", "employment_type", "salary_min", "salary_max",
        "salary_period", "apply_link", "publisher", "source_skills", "career_level", "experience_years_min",
        "role", "is_tech", "class_basis", "search_role", "search_category", "is_valid_for_analysis",
        "review_candidate_of", "review_reason"]


def raw_record(ref):
    path, idx = ref.rsplit("#", 1)
    folder = path.split("/")[2]
    return folder, list(GET[folder](json.load(open(path))))[int(idx)]


def main():
    out = Path("data/export") / datetime.date.today().isoformat()
    out.mkdir(parents=True, exist_ok=True)
    conn = connect(); cur = conn.cursor()
    cur.execute(f"SELECT {', '.join(COLS)} FROM jobs ORDER BY job_id")
    rows = [dict(zip(COLS, r)) for r in cur.fetchall()]
    conn.close()
    for r in rows:
        if r["posted_at"]:
            r["posted_at"] = r["posted_at"].isoformat()
        for k in ("salary_min", "salary_max"):
            if r[k] is not None:
                r[k] = float(r[k])
    json.dump(rows, open(out / "jobs_clean.json", "w"), ensure_ascii=False)
    with open(out / "jobs_clean.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v) for k, v in r.items()})

    random.seed(11); sample, mapping, ok = [], [], 0
    for src in sorted({r["source"] for r in rows}):
        pool = [r for r in rows if r["source"] == src and r["raw_ref"]]
        for r in random.sample(pool, min(10, len(pool))):
            folder, rec = raw_record(r["raw_ref"])
            assert NORM[folder](rec)["job_id"] == r["source_job_id"], r["raw_ref"]
            ok += 1
            sample.append(rec)
            mapping.append({"sample_index": len(sample) - 1, "job_id": r["job_id"], "source": src,
                            "source_job_id": r["source_job_id"], "raw_ref": r["raw_ref"]})
    json.dump(sample, open(out / "raw_sample.json", "w"), ensure_ascii=False)
    with open(out / "sample_mapping.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(mapping[0])); w.writeheader(); w.writerows(mapping)

    C = collections.Counter
    countries = sorted({r["country"] for r in rows if r["country"]})
    counts = {
        "total_jobs": len(rows),
        "valid_for_analysis": sum(1 for r in rows if r["is_valid_for_analysis"]),
        "review_candidates": sum(1 for r in rows if r["review_candidate_of"]),
        "by_source": dict(C(r["source"] for r in rows)),
        "is_tech": dict(C(r["is_tech"] for r in rows)),
        "is_tech_by_country": {c: dict(C(r["is_tech"] for r in rows if r["country"] == c)) for c in countries},
        "is_tech_by_basis": dict(C(f"{r['is_tech']}/{r['class_basis']}" for r in rows)),
    }
    json.dump(counts, open(out / "counts.json", "w"), indent=2)
    print(json.dumps(counts, indent=2))
    print(f"\nmapping verified: {ok}/{len(mapping)} raw sample records match their DB rows")
    print("written to", out)


if __name__ == "__main__":
    main()
