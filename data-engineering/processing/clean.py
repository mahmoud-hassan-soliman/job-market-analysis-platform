import re
from datetime import datetime, timedelta, timezone

# Governorate-level cities. Order matters: first match wins.
CITY_KEYWORDS = [
    ("Alexandria", ["alexandria", "الإسكندرية", "الاسكندرية"]),
    ("Giza", ["giza", "al jizah", "الجيزة", "october", "أكتوبر", "sheikh zayed", "zayed",
              "الشيخ زايد", "dokki", "mohandessin", "smart village"]),
    ("Cairo", ["cairo", "القاهرة", "nasr city", "heliopolis", "maadi", "tagamoa",
               "settlement", "obour", "shorouk", "badr", "new capital", "مدينة نصر"]),
]
OTHER_CITIES = ["mansoura", "port said", "suez", "tanta", "ismailia", "hurghada",
                "sharm", "assiut", "damietta", "fayoum", "luxor", "aswan", "zagazig"]


def normalize_city(raw):
    """'Qesm El Maadi, Cairo, Egypt' -> 'Cairo'; 'Egypt' or empty -> None."""
    if not raw:
        return None
    low = re.split(r"[•|]", str(raw))[0].strip().lower()  # drop '• via LinkedIn' parts
    for city, words in CITY_KEYWORDS:
        if any(w in low for w in words):
            return city
    for w in OTHER_CITIES:
        if w in low:
            return w.title()
    first = low.split(",")[0].strip()
    if first in ("", "egypt", "eg", "مصر"):
        return None
    return first.title()


def normalize_country(raw):
    """All queries used country=Egypt, so empty -> 'EG'. Disclose this in the report."""
    low = str(raw or "").strip().lower()
    if low in ("", "egypt", "eg", "مصر"):
        return "EG"
    return str(raw).strip().upper()


def parse_iso(s):
    """ISO string -> aware UTC datetime, or None."""
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def from_unix(ts):
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return None


_UNITS = {"minute": "minutes", "hour": "hours", "day": "days", "week": "weeks"}
_REL = re.compile(r"(\d+|an?)\+?\s*(minute|hour|day|week|month)s?\s+ago", re.I)


def parse_relative_date(text, ref):
    """'4 hours ago' + scrape time -> datetime; None if not understood."""
    if not text or ref is None:
        return None
    t = str(text).strip().lower()
    if t in ("today", "just now", "posted today") or "just" in t:
        return ref
    if "yesterday" in t:
        return ref - timedelta(days=1)
    m = _REL.search(t)
    if not m:
        return None
    n = 1 if m.group(1).startswith("a") else int(m.group(1))
    unit = m.group(2).lower()
    if unit == "month":
        return ref - timedelta(days=30 * n)
    return ref - timedelta(**{_UNITS[unit]: n})


_AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
# (unit, timedelta-days-or-None, stems, dual word)
_AR_UNITS = [
    ("minutes", ("دقيق", "دقائق"), "دقيقتين"),
    ("hours", ("ساع",), "ساعتين"),
    ("days", ("يوم", "أيام", "ايام"), "يومين"),
    ("weeks", ("أسبوع", "اسبوع", "أسابيع", "اسابيع"), "أسبوعين"),
    ("months", ("شهر", "أشهر", "اشهر", "شهور"), "شهرين"),
]


def parse_arabic_relative(text, ref):
    """'قبل ٤ أيام' + fetch time -> datetime (about 1 day precision); None if not understood."""
    if not text or ref is None:
        return None
    t = str(text).translate(_AR_DIGITS).strip()
    if "اليوم" in t or "الآن" in t or "الان" in t:
        return ref
    if "أمس" in t or "امس" in t:
        return ref - timedelta(days=1)
    m = re.search(r"\d+", t)
    for unit, stems, dual in _AR_UNITS:
        if dual in t:
            n = 2
        elif any(s in t for s in stems):
            n = int(m.group()) if m else 1
        else:
            continue
        if unit == "months":
            return ref - timedelta(days=30 * n)
        return ref - timedelta(**{unit: n})
    return None
