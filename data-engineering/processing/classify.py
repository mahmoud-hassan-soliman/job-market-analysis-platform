"""Classify each job from its own title and description (never from the search keyword)."""
import csv, random, re, collections
from pathlib import Path
from processing.load import connect


def rx(words):
    return re.compile(r"(?<![a-z0-9])(?:" + "|".join(words) + r")(?![a-z0-9])", re.I)


TECH_RX = {k: rx(v) for k, v in {
    "data_ai": [r"data (?:engineer|scientist|analyst|architect)", r"machine learning", r"ml", r"ai",
                r"artificial intelligence", r"bi", r"business intelligence", r"analytics engineer", r"nlp", r"llm"],
    "devops_cloud": [r"devops", r"sre", r"site reliability", r"cloud", r"platform engineer", r"kubernetes",
                     r"aws", r"azure", r"gcp"],
    "security": [r"security (?:engineer|analyst|architect|specialist)", r"cyber\w*", r"soc analyst",
                 r"penetration", r"infosec"],
    "qa": [r"qa", r"quality assurance", r"test(?:er| engineer| automation)", r"sdet"],
    "software": [r"software", r"developer", r"programmer", r"full[- ]?stack", r"front[- ]?end", r"back[- ]?end",
                 r"android", r"ios", r"flutter", r"react", r"node(?:\.?js)?", r"java", r"javascript",
                 r"python", r"\.net", r"php", r"golang", r"web designer"],
    "it_infra": [r"help ?desk", r"it support", r"technical support", r"systems? (?:administrator|engineer|analyst)", r"sysadmin",
                 r"network (?:engineer|administrator|specialist)", r"desktop support",
                 r"it (?:specialist|technician|officer|manager|engineer|administrator)", r"infrastructure"],
    "tech_other": [r"solutions? architect", r"tech(?:nical)? lead", r"cto", r"erp", r"sap", r"dba", r"database"],
}.items()}

NON_RX = {k: rx(v) for k, v in {
    "finance_accounting": [r"account(?:ant|ing)", r"auditor", r"audit", r"financ\w*", r"treasury", r"tax",
                           r"controller", r"payroll"],
    "marketing_sales": [r"marketing", r"seo", r"social media", r"brand\w*", r"sales", r"business develop\w*",
                        r"account (?:manager|executive)", r"content (?:writer|creator)"],
    "hr_recruiting": [r"hr", r"human resources", r"recruit\w*", r"talent acquisition", r"people (?:partner|operations)", r"personnel", r"global mobility", r"people (?:&|and) culture", r"employee relations", r"compensation", r"talent", r"legal", r"lawyer", r"paralegal", r"compliance"],
    "other_nontech": [r"mechanical", r"civil", r"structur\w*", r"chemical", r"petroleum", r"electrical",
                      r"nurse", r"physician", r"doctor", r"pharmac\w*", r"teacher", r"driver", r"chef",
                      r"cashier", r"warehouse", r"logistics", r"supply chain", r"skin care", r"clinic\w*"],
}.items()}

DESC_RX = rx([r"python", r"sql", r"java", r"javascript", r"typescript", r"react(?:js|\.js| native)", r"angular", r"vue(?:js|\.js)?",
              r"node(?:\.?js)?", r"aws", r"azure", r"gcp", r"docker", r"kubernetes", r"terraform", r"linux",
              r"git", r"api", r"restful", r"c\+\+", r"c#", r"\.net", r"php", r"django", r"flask", r"spring boot",
              r"mongodb", r"postgres(?:ql)?", r"mysql", r"ci/cd", r"machine learning", r"tensorflow",
              r"pytorch", r"pyspark", r"apache spark", r"hadoop", r"airflow", r"kafka"])


DESC_NON = {k: rx(v) for k, v in {
    "finance_accounting": [r"accounting", r"financial statements", r"audit\w*", r"invoice\w*", r"budget\w*",
                           r"reconciliation", r"tax", r"ifrs", r"accounts (?:payable|receivable)"],
    "marketing_sales": [r"marketing", r"sales", r"campaign\w*", r"clients?", r"customers?", r"brand\w*",
                        r"lead generation", r"seo"],
    "hr_recruiting": [r"recruit\w*", r"payroll", r"employees?", r"onboarding", r"talent", r"hr"],
    "operations_admin": [r"operations?", r"logistics", r"procurement", r"administrative", r"coordinat\w*",
                         r"scheduling", r"supply chain", r"vendors?"],
    "legal_compliance": [r"legal", r"contracts?", r"compliance", r"regulat\w*"],
    "engineering_other": [r"mechanical", r"civil", r"electrical", r"construction", r"hvac", r"manufactur\w*"],
}.items()}


def classify(title, desc):
    t = title or ""
    tech = [k for k, p in TECH_RX.items() if p.search(t)]
    non = [k for k, p in NON_RX.items() if p.search(t)]
    if tech and non:
        return "ambiguous", "unknown", "title_conflict"
    if tech:
        return tech[0], "tech", "title"
    if non:
        return non[0], "non_tech", "title"
    hits = {m.group(0).lower() for m in DESC_RX.finditer(desc or "")}
    if len(hits) >= 4:
        return "tech_other", "tech", "description"
    if len(hits) <= 1 and len(desc or "") >= 150:
        score = {k: len({m.group(0).lower() for m in p.finditer(desc)}) for k, p in DESC_NON.items()}
        best = max(score, key=score.get)
        return (best if score[best] >= 2 else "general_non_tech"), "non_tech", "description_no_tech_terms"
    return "unknown", "unknown", "insufficient_info"


def main():
    conn = connect(); cur = conn.cursor()
    for c in ("role", "is_tech", "class_basis"):
        cur.execute(f"ALTER TABLE jobs ADD COLUMN IF NOT EXISTS {c} text")
    cur.execute("SELECT job_id, title, description, country FROM jobs")
    rows = cur.fetchall()
    out = [(*classify(t, d), j) for j, t, d, _ in rows]
    cur.executemany("UPDATE jobs SET role=%s, is_tech=%s, class_basis=%s WHERE job_id=%s", out)
    conn.commit()
    print("is_tech:", dict(collections.Counter(o[1] for o in out)))
    print("basis  :", dict(collections.Counter(o[2] for o in out)))
    print("by country:", {c: dict(collections.Counter(o[1] for o, r in zip(out, rows) if r[3] == c))
                          for c in sorted({r[3] for r in rows if r[3]})})
    # stratified sample for manual checking / the team
    random.seed(7)
    cur.execute("SELECT job_id, title, country, role, is_tech, class_basis, left(description, 200) FROM jobs")
    allr = cur.fetchall(); sample = []
    for key in ("tech", "non_tech", "unknown"):
        grp = [r for r in allr if r[4] == key]
        sample += random.sample(grp, min(20, len(grp)))
    Path("export").mkdir(exist_ok=True)
    with open("export/classification_sample.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["job_id", "title", "country", "role", "is_tech", "basis", "description_start", "my_label"])
        w.writerows([list(r) + [""] for r in sample])
    for r in sample[::4]:
        print(f"{r[4]:9} {r[3]:20} {r[5]:18} {r[1][:55]}")


if __name__ == "__main__":
    main()
