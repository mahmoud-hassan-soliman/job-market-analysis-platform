import sys, pathlib
from datetime import datetime, timezone
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from processing.load import make_job_key


def r(country, company, city, d, source, sid):
    return {"country": country, "company": company, "location_city": city, "source": source,
            "job_id": sid, "posted_at": datetime(*d, tzinfo=timezone.utc) if d else None}


def test_the_three_agreed_examples():
    assert make_job_key(r("EG", "Valeo", "Cairo", (2026, 10, 9), "linkedin", "4449647695")) == "EG_valeo_cairo_20261009_In_4449647695"
    assert make_job_key(r("EG", "Acme", "Alexandria", (2026, 10, 11), "apify_wuzzuf", "98765")) == "EG_acme_alexandria_20261011_WZ_98765"
    assert make_job_key(r("SA", "Example Tech", "Riyadh", (2026, 11, 17), "bayt", "24680")) == "SA_exampletech_riyadh_20261117_BY_24680"


def test_missing_parts_are_marked():
    assert make_job_key(r("EG", "Acme", None, None, "linkedin", "1")) == "EG_acme_unknown_nodate_In_1"


def test_same_company_city_date_different_ids_differ():
    a = make_job_key(r("EG", "Acme", "Cairo", (2026, 10, 9), "linkedin", "1"))
    b = make_job_key(r("EG", "Acme", "Cairo", (2026, 10, 9), "linkedin", "2"))
    assert a != b


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
    print("all ok")
