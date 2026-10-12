# Unified schema proposal

Status: draft. Mahmoud leads review with Youssef and David before implementation.

| Field | Proposed meaning |
| --- | --- |
| job_id | Stable internal ID of a canonical job |
| source_records | Source name, source job ID if available, URL, collected_at, raw reference/hash |
| title / description | Original text preserved without inventing missing values |
| company_name | Nullable; retain original and normalized form if available |
| country / city / work_mode | Nullable normalized location and work arrangement |
| employment_type / seniority | Nullable categories with documented mappings |
| posted_at / expires_at | Nullable source timestamps; UTC when timezone is known |
| salary_min / salary_max / currency / period | Nullable structured salary with original text; no inferred salary |
| language | Description language, including mixed Arabic/English |
| quality_flags | Missing fields, invalid values and quality decisions |
| duplicate_cluster_id | Link to evidence for merging source records |
| created_at / updated_at / schema_version | Lifecycle timestamps and contract version |

Missing, unknown and not applicable must be distinguished consistently. Dates use ISO 8601; timestamps use UTC where conversion is supported by evidence. Agree required fields, identifier strategy and enum values before implementation.

## Skill extraction output

`job_id`, `run_id`, `schema_version`, `taxonomy_version`, `model`, `prompt_version`, `skills`, `input_tokens`, `output_tokens`, `cost`, `latency_ms`, `status`, `error`.

Each skill includes `raw_mention`, `evidence_span`, `normalized_skill_id`, `normalized_label`, `category`, and nullable confidence with documented meaning. Unmapped mentions are retained for review. Store evidence so reviewers can distinguish explicit requirements from unsupported inferences.

## Contract acceptance

Review Arabic, English, mixed-language, missing-salary and multi-source duplicate examples. Agree JSON Schema and PostgreSQL mappings, validate fixtures, document versioning and migration policy.
