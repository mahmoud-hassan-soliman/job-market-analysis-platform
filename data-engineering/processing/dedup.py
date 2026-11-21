"""Second-pass near-duplicate detection on the jobs table. Flags, never deletes."""
import collections, csv, hashlib, re
from pathlib import Path
from rapidfuzz import fuzz
from processing.load import connect

DROP = {"llc", "ltd", "limited", "inc", "co", "company", "corp", "corporation", "fze", "fzco", "fz",
        "pjsc", "plc", "group", "holding", "holdings", "the", "for", "and", "of", "ksa", "uae",
        "egypt", "saudi", "arabia", "emirates", "international", "intl"}
RANK = {"apify_wuzzuf": 4, "linkedin": 3, "jsearch": 2, "bayt": 1}


def cnorm(s):
    w = [x for x in re.sub(r"[^a-z0-9\u0600-\u06ff ]", " ", (s or "").lower()).split() if x not in DROP]
    return " ".join(w) or (s or "").lower().strip()


def tnorm(s):
    s = (s or "").lower()
    s = re.sub(r"\b(m ?/ ?f|f ?/ ?m|remote|hybrid|urgent|hiring|immediate|onsite|on site)\b", " ", s)
    return " ".join(re.sub(r"[^a-z0-9\u0600-\u06ff ]", " ", s).split())


def fp(d):
    t = re.sub(r"[^a-z0-9]", "", (d or "").lower())[:600]
    return hashlib.md5(t.encode()).hexdigest() if len(t) >= 200 else None


LEVEL = {"junior", "senior", "lead", "principal", "intern", "internship", "head", "manager",
         "director", "trainee", "associate", "staff", "entry"}


def seniority(t):
    return re.sub(r"\bjr\b", "junior", re.sub(r"\bsr\b", "senior", t))


def level(t):
    return frozenset(w for w in t.split() if w in LEVEL)


def digits(t):
    return tuple(re.findall(r"\d+", t))


def main():
    conn = connect()
    cur = conn.cursor()
    cur.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS review_candidate_of text")
    cur.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS review_reason text")
    cur.execute("SELECT job_id, source, title, company, description, location_city, country FROM jobs")
    cols = ("key", "source", "title", "company", "desc", "city", "country")
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    for r in rows:
        r["c"], r["t"], r["fp"] = cnorm(r["company"]), seniority(tnorm(r["title"])), fp(r["desc"])
    by_key = {r["key"]: r for r in rows}
    parent = {r["key"]: r["key"] for r in rows}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        parent[find(a["key"])] = find(b["key"])

    blocks = collections.defaultdict(list)
    for r in rows:
        blocks[(r["country"], r["c"])].append(r)
    for g in blocks.values():
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                a, b = g[i], g[j]
                if level(a["t"]) != level(b["t"]) or digits(a["t"]) != digits(b["t"]):
                    continue
                ts = fuzz.token_sort_ratio(a["t"], b["t"])
                same_city = a["city"] == b["city"] or not a["city"] or not b["city"]
                if (ts >= 92 and same_city) or (ts >= 80 and a["fp"] and a["fp"] == b["fp"]):
                    union(a, b)
    cross = collections.defaultdict(list)
    for r in rows:
        if r["fp"]:
            cross[(r["country"], r["c"], r["city"], r["t"], r["fp"])].append(r)
    for g in cross.values():
        for r in g[1:]:
            union(g[0], r)

    clusters = collections.defaultdict(list)
    for r in rows:
        clusters[find(r["key"])].append(r)
    flagged = []
    for g in clusters.values():
        if len(g) > 1:
            win = max(g, key=lambda r: (RANK.get(r["source"], 0), len(r["desc"] or "")))
            flagged += [(r, win) for r in g if r is not win]

    flagged = [(r, w) for r, w in flagged
       if not (r["city"] and w["city"] and r["city"] != w["city"])]
    cur.execute("UPDATE jobs SET review_candidate_of = NULL, review_reason = NULL")
    cur.executemany("UPDATE jobs SET review_candidate_of = %s, review_reason = %s WHERE job_id = %s",
                    [(w["key"], "cross_source" if w["source"] != r["source"] else "same_source_similar", r["key"])
                     for r, w in flagged])
    conn.commit()

    Path("data").mkdir(exist_ok=True)
    with open("data/dedup_flagged.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["country", "dup_source", "dup_title", "dup_company", "kept_source", "kept_title", "kept_company"])
        for r, k in flagged:
            w.writerow([r["country"], r["source"], r["title"], r["company"], k["source"], k["title"], k["company"]])
    print(f"rows={len(rows)} near_duplicates_flagged={len(flagged)} truly_unique={len(rows) - len(flagged)}")
    print("flagged by country:", dict(collections.Counter(r["country"] for r, _ in flagged)))
    print("flagged by source :", dict(collections.Counter(r["source"] for r, _ in flagged)))
    print("--- 8 sample pairs (dropped | kept) ---")
    for r, k in flagged[:8]:
        print(f"[{r['country']}] {r['title']} @ {r['company']}  |  {k['title']} @ {k['company']}")


if __name__ == "__main__":
    main()
