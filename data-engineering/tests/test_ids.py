import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from processing.load import dedupe_by_source_id, internal_id


def row(sid, title, city, source="linkedin", raw="f#0"):
    return {"job_id": sid, "source": source, "title": title, "company": "Acme",
            "country": "EG", "location_city": city, "description": "x" * 150, "raw_ref": raw}


def test_same_ad_twice_is_stored_once():
    kept, s = dedupe_by_source_id([row("1", "Data Engineer", "Cairo"),
                                   row("1", "Data Engineer", "Cairo", raw="f#1")])
    assert len(kept) == 1 and s["exact_duplicates"] == 1


def test_cairo_and_alexandria_stay_separate():
    kept, _ = dedupe_by_source_id([row("1", "Data Engineer", "Cairo"),
                                   row("2", "Data Engineer", "Alexandria")])
    assert len(kept) == 2


def test_backend_and_mobile_stay_separate():
    kept, _ = dedupe_by_source_id([row("1", "Software Engineer (Backend)", "Cairo"),
                                   row("2", "Software Engineer (Mobile)", "Cairo")])
    assert len(kept) == 2


def test_internal_id_is_stable_and_source_scoped():
    assert internal_id("linkedin", "1") == internal_id("linkedin", "1")
    assert internal_id("linkedin", "1") != internal_id("bayt", "1")


def test_rejects_are_counted_with_reason():
    _, s = dedupe_by_source_id([row(None, "X", "Cairo"), row("3", None, "Cairo")])
    assert s["rejected"] == {"missing source_job_id": 1, "missing title": 1}


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
    print("all ok")
