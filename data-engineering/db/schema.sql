CREATE TABLE IF NOT EXISTS jobs (
    job_id        TEXT PRIMARY KEY,          -- internal, stable: j_ + sha1(source:source_job_id)
    source        TEXT NOT NULL,
    source_job_id TEXT NOT NULL,             -- the ad's own ID at the source
    raw_ref       TEXT,                      -- raw file path#index the row came from
    job_key       TEXT,                      -- Country_Company_City_PostDate_SourceCode_SourceJobID
    title         TEXT NOT NULL,
    company       TEXT,
    description   TEXT,
    posted_at     TIMESTAMPTZ,
    location_raw  TEXT,
    location_city TEXT,
    country       TEXT,
    is_remote     BOOLEAN,
    employment_type TEXT,
    salary_min    NUMERIC,
    salary_max    NUMERIC,
    salary_period TEXT,
    apply_link    TEXT,
    publisher     TEXT,
    source_skills TEXT[],
    career_level  TEXT,
    experience_years_min INT,
    ingested_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source, source_job_id)
);
CREATE INDEX IF NOT EXISTS idx_jobs_posted_at ON jobs (posted_at);
