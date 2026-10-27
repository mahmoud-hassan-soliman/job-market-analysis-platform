import re
from processing.clean import (normalize_city, normalize_country, parse_iso,
                              parse_relative_date)

def _first_int(s):
    m = re.search(r"\d+", str(s or ""))
    return int(m.group()) if m else None

def _date(value, ref):
    return parse_iso(value) or parse_relative_date(value, ref)

def normalize_linkedin(r):
    ref = parse_iso(r.get("scrapedAt"))
    return {
        "job_id": str(r.get("id") or ""),
        "source": "linkedin",
        "title": r.get("title"),
        "company": r.get("companyName"),
        "description": r.get("descriptionText"),
        "posted_at": _date(r.get("postedAt"), ref),
        "location_raw": r.get("location"),
        "location_city": normalize_city(r.get("location")),
        "country": normalize_country(None),
        "is_remote": None,
        "employment_type": r.get("employmentType"),
        "salary_min": None, "salary_max": None, "salary_period": None,
        "apply_link": r.get("applyUrl") or r.get("link"),
        "publisher": "LinkedIn",
        "source_skills": None,
        "career_level": r.get("seniorityLevel"),
        "experience_years_min": None,
    }

def normalize_bayt(r):
    ref = parse_iso(r.get("scrapedAt"))
    return {
        "job_id": str(r.get("jobId") or ""),
        "source": "bayt",
        "title": r.get("title"),
        "company": r.get("company"),
        "description": r.get("listingSummary"),
        "posted_at": parse_relative_date(r.get("postedAtRelative"), ref),
        "location_raw": r.get("location"),
        "location_city": normalize_city(r.get("location")),
        "country": normalize_country(None),
        "is_remote": None,
        "employment_type": r.get("jobType"),
        "salary_min": None, "salary_max": None, "salary_period": None,
        "apply_link": r.get("listingUrl") or r.get("url"),
        "publisher": "Bayt",
        "source_skills": None,
        "career_level": r.get("careerLevel"),
        "experience_years_min": _first_int(r.get("experience")),
    }
