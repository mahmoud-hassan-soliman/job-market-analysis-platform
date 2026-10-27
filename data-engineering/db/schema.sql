CREATE TABLE IF NOT EXISTS jobs (
    dedup_key       TEXT PRIMARY KEY,
    job_id          TEXT NOT NULL,
    source          TEXT NOT NULL DEFAULT 'jsearch',
    title           TEXT NOT NULL,
    company         TEXT,
    description     TEXT,
    posted_at       TIMESTAMPTZ,
    location_raw    TEXT,
    location_city   TEXT,
    country         TEXT,
    is_remote       BOOLEAN,
    employment_type TEXT,
    salary_min      NUMERIC,
    salary_max      NUMERIC,
    salary_period   TEXT,
    apply_link      TEXT,
    publisher       TEXT,
    source_skills   TEXT[],
    career_level    TEXT,
    experience_years_min INT,
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_jobs_posted_at ON jobs (posted_at);
