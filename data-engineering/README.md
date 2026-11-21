# Job Market Analysis Platform: Data Pipeline

Collects job postings for Egypt, Saudi Arabia and the UAE through Apify actors (LinkedIn, Wuzzuf, Bayt), cleans and checks them, and stores them in PostgreSQL.

    Apify actors -> raw JSON (data/raw/, never edited) -> load -> dedup flags -> quality -> classify -> PostgreSQL `jobs`

JSearch was evaluated and dropped (small monthly quota, mostly duplicate results, no salary data). Its raw files are archived and not loaded.

## Structure
- `ingestion/`: Apify collectors (`run_scale.py`, `run_country.py` with a budget guard and spend ledger).
- `processing/`: `clean.py` and `extra_sources.py` (normalizers), `load.py` (read raw, dedupe by source id, assign ids, upsert), `dedup.py` (flags similar ads), `quality.py` (missing-data rates, validity), `categorize.py` (search keyword only), `classify.py` (role and tech from title and description).
- `db/schema.sql`, `docker-compose.yml`: PostgreSQL 16 on port 5433.
- `run_pipeline.py`: the whole flow in one command. `tests/`: unit tests. `logs/`: run logs.

## Setup
    cp .env.example .env        # fill in the database values; add APIFY_TOKEN only if you will collect
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    docker compose up -d        # wait ~8 seconds

## Run
    python run_pipeline.py                  # dry run: plan and maximum cost. No token, no spend.
    python run_pipeline.py --skip-collect   # rebuild the DB from saved raw files and run every step. No token.
    python run_pipeline.py --go             # collect from Apify (needs APIFY_TOKEN, spends credit), then every step

Order of steps: collect (only with `--go`) -> load -> dedup -> quality -> categorize -> classify -> checks -> report.
Apify responses are cached in `data/raw/` per actor, input and ISO week, so repeating a search in the same week costs nothing.

## What the end-of-run report shows
ingested (raw records read), stored jobs, exact duplicates (same source and source id), review candidates (similar ads, flagged and kept), rejected at load (with reason), invalid for analysis (with reasons), and tech / non_tech / unknown counts.

## Identity and duplicates
- `job_id`: internal and stable, `j_` + first 16 hex of `sha1(source:source_job_id)`. Loading the same data again gives the same ids.
- `source`, `source_job_id`: where the ad came from and its own id there.
- `raw_ref`: `data/raw/<folder>/<file>.json#<index>`: the raw record behind the row.
- Within one source, the same `source_job_id` is one ad (the richer copy is kept).
- Similar ads (same company and country, close titles, same city or unknown city, guard on seniority words and numbers) are only flagged: `review_candidate_of`, `review_reason` (`cross_source` or `same_source_similar`). Nothing is deleted or merged. Different cities are never flagged as the same ad.

To find the row of a raw record:

    SELECT * FROM jobs WHERE raw_ref = 'data/raw/linkedin/<file>.json#12';

## Classification
`role`, `is_tech` (`tech`, `non_tech`, `unknown`) and `class_basis` come from the job title and description. The search keyword is kept separately in `search_role` / `search_category`. Rule-based and not yet validated against a labeled sample. `class_basis = description_no_tech_terms` is the weakest rule.

## Limits
- Cities are compared as written after normalization (Giza and Cairo count as different).
- Country comes from the location text, with the search country as fallback.
- Review flags are candidates, not confirmed duplicates.
- Data is scraped; check each source's terms and do not publish it. `data/` is not in git.

## Tests
    python -m pytest tests -q

## Export for the team
    python -m processing.export_data    # data/export/<date>/: jobs_clean.csv/json, raw_sample.json, sample_mapping.csv, counts.json
`sample_mapping.csv` links each raw sample record (`sample_index` in `raw_sample.json`) to its row: `job_id`, `source_job_id`, `raw_ref`. `jobs_clean` holds every stored row with its flags; filter `is_valid_for_analysis` for analysis. Legacy: `ingestion/jsearch_client.py`, `run_plan.py` and `queries.py` are the dropped JSearch collector and are not part of the pipeline.
