# Job Market Analysis Platform: Data Pipeline (Sprint 1)

Collects Egyptian job postings from several sources, cleans and deduplicates them, and stores them in PostgreSQL.

    Sources (Apify actors, JSearch) -> raw JSON -> clean + dedup -> PostgreSQL `jobs` table

## Structure
- `ingestion/`: collectors (`run_scale.py` for LinkedIn/Wuzzuf/Bayt via Apify, `jsearch_client.py` + `run_plan.py` for JSearch, `probe_source.py` for source tests)
- `processing/`: `clean.py` (city, country, date cleaning), `extra_sources.py` (LinkedIn/Bayt normalizers), `load.py` (normalize, validate, dedup, upsert)
- `db/schema.sql`: the `jobs` table; `docker-compose.yml` runs PostgreSQL 16 on port 5433
- `tests/`: unit tests for the cleaning functions
- `run_pipeline.py`: collect -> load -> verify in one command
- `data/raw/`: raw API responses (not in git)

## Setup
    cp .env.example .env        # then fill in your own keys
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    docker compose up -d        # wait ~8 seconds for PostgreSQL

## Run
    python run_pipeline.py                      # dry run: shows plan and maximum cost
    python run_pipeline.py --go                 # collect (last 7 days), load, verify
    python run_pipeline.py --go --window month --cap 200   # larger backfill
    python -m processing.load                   # rebuild the table from data/raw only
    python -m pytest tests -q                   # unit tests

Every API response is cached in `data/raw/`, so re-running a search in the same week costs nothing. The database is always rebuilt from the raw files, so loading is repeatable.

## Notes
- Data comes from scrapers and APIs; check each source's terms of service. Do not publish the raw data.
- Country is set to EG when missing (all queries filter on Egypt).
- Deduplication is exact `title|company`; overlap across sources may be under-detected.
- Run all commands from the data-engineering/ folder (paths such as data/raw are relative to it).

## Sprint 2 additions
- Country per job (EG/SA/AE) from location text; the dedup key now includes country.
- `ingestion/run_country.py`: Saudi Arabia and UAE collection from LinkedIn (Apify) with a hard budget guard and a spend ledger.
- `processing/dedup.py`: second-pass near-duplicate detection (flags, never deletes; seniority and number guard).
- `processing/quality.py`: missing-data % per country and source, `is_valid_for_analysis` flag.
- Run logs in `logs/` (loading twice gives identical row counts).

Run: `python -m ingestion.run_country --countries sa,ae --cap 100` (dry run), add `--go` to spend; then `python -m processing.load && python -m processing.dedup && python -m processing.quality`.

## Update 2026-11-17
- `processing/categorize.py`: adds `search_role` and `role_category` (tech, cloud, it, business) from the `_search_role` tag in raw LinkedIn files. Older Egypt files and non-LinkedIn sources have no tag, so their category is empty.
- Logs for the 2026-11-17 collection (63 searches, estimated cost $1.83) and the category counts are in `logs/`.
