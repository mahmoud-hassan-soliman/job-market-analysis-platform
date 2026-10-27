# Schema mapping: as-built `jobs` table (v1) vs draft unified schema

Status: Sprint 1 delivered v1. The draft in `docs/unified-schema.md` is not yet agreed; conformance is to be decided with Mahmoud and David.

| Draft field | v1 column | Status |
|---|---|---|
| job_id (stable internal) | `dedup_key` (PK, normalized title+company); `job_id` is the source's own ID and is not stable across searches (JSearch) | Gap |
| source_records | none; one row per job, `source` is the winning source only | Gap |
| title / description | `title`, `description` (Wuzzuf: description + requirements; Bayt: short summary only) | Match |
| company_name | `company` (normalized form exists only inside the dedup key) | Partial |
| country / city | `country`, `location_city` (governorate level), `location_raw`; country set to EG when missing | Match |
| work_mode | `is_remote` (boolean, mostly NULL) | Partial |
| employment_type / seniority | `employment_type`, `career_level` (no common enum yet) | Match |
| posted_at | `posted_at` (JSearch and Bayt derived from relative text, about 1 day precision) | Match |
| expires_at | none | Gap |
| salary min / max / period | `salary_min`, `salary_max`, `salary_period` (no currency or original text; LinkedIn and Bayt salary text not parsed) | Partial |
| language | none | Gap |
| quality_flags | none (inferred country and estimated dates are not flagged) | Gap |
| duplicate_cluster_id | none (exact title+company key, no evidence link) | Gap |
| created_at / updated_at / schema_version | `ingested_at` only | Partial |

Proposed follow-up (not implemented, needs team agreement): stable `job_uid`, a `source_records` table, and columns for language, salary currency and original text, quality flags, expires_at and schema_version.
