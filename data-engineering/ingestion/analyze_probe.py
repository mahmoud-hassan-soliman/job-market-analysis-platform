import sys, json, collections
MAP = {  # source: (description, date, salary, location, company)
 "linkedin": ("descriptionText", "postedAt", "salary", "location", "companyName"),
 "bayt":     ("listingSummary", "postedAtRelative", "salary", "location", "company"),
}
for f in sys.argv[1:]:
    name = f.split("/")[-1].split(".")[0]
    kind = "linkedin" if name.startswith("linkedin") else "bayt"
    d, dt, s, loc, co = MAP[kind]
    items = json.load(open(f)); n = len(items)
    pct = lambda k: round(100 * sum(1 for i in items if i.get(k)) / n)
    avg = sum(len(str(i.get(d) or "")) for i in items) // n
    keys = {(i.get("title") or "").lower() + "|" + str(i.get(co) or "").lower() for i in items}
    print(f"\n== {name}: {n} jobs, {len(keys)} unique title|company")
    print(f"description {pct(d)}% (avg {avg} chars) | date {pct(dt)}% | salary {pct(s)}% | location {pct(loc)}%")
    print("top locations:", collections.Counter(str(i.get(loc)) for i in items).most_common(5))
