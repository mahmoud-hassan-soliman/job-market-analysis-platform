from datetime import datetime, timezone
from processing.clean import *

REF = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)

def test_city():
    assert normalize_city("Qesm El Maadi, Cairo, Egypt") == "Cairo"
    assert normalize_city("New Cairo, Cairo, Egypt") == "Cairo"
    assert normalize_city("Giza, Al Jizah, Egypt") == "Giza"
    assert normalize_city("6th of October, Egypt") == "Giza"
    assert normalize_city("Giza, Cairo, Egypt") == "Giza"
    assert normalize_city("القاهرة • عبر LinkedIn") == "Cairo"
    assert normalize_city("Alexandria, Egypt") == "Alexandria"
    assert normalize_city("Egypt") is None
    assert normalize_city("") is None

def test_country():
    assert normalize_country("") == "EG"
    assert normalize_country("Egypt") == "EG"

def test_dates():
    assert parse_relative_date("4 hours ago", REF).hour == 8
    assert parse_relative_date("2 days ago", REF).day == 24
    assert parse_relative_date("30+ days ago", REF).month == 9
    assert parse_relative_date("a week ago", REF).day == 19
    assert parse_relative_date("yesterday", REF).day == 25
    assert parse_relative_date("garbage", REF) is None
    assert parse_iso("2026-10-26T10:00:00Z").hour == 10
    assert from_unix(1792000000).year == 2026

def test_arabic_dates():
    assert parse_arabic_relative("قبل ٤ أيام", REF).day == 22
    assert parse_arabic_relative("قبل ٤ أياماً", REF).day == 22
    assert parse_arabic_relative("قبل يومين", REF).day == 24
    assert parse_arabic_relative("قبل ساعة", REF).hour == 11
    assert parse_arabic_relative("قبل ٣ أسابيع", REF).day == 5
    assert parse_arabic_relative("قبل شهر", REF).month == 9
    assert parse_arabic_relative("???", REF) is None
