# Work plan

Named owners are planning responsibilities; GitHub assignments await confirmed handles. All new tasks start in To Do. Deadlines and budgets are to be agreed.

## 1. Agree architecture and milestone dependencies

Owner: Mahmoud · Workstream: architecture

Deliverable: Reviewed architecture diagram and decision log

Dependencies: None

Acceptance criteria:

- [ ] Document end-to-end boundaries and owners
- [ ] Agree source-to-database-to-LLM-to-analytics interfaces
- [ ] Record open decisions, budget constraints and proposed milestone sequence

## 2. Define and review the unified job and skill schema

Owner: Mahmoud · Workstream: architecture

Deliverable: Versioned JSON Schema, PostgreSQL mapping and representative fixtures

Dependencies: Architecture proposal

Acceptance criteria:

- [ ] Review required/nullable fields, timestamps and IDs with Youssef and David
- [ ] Validate Arabic, English, mixed-language and incomplete records
- [ ] Define extraction output, taxonomy versions and migration policy

## 3. Assess Wuzzuf, Forasna, LinkedIn and Bayt access feasibility

Owner: Youssef · Workstream: data-engineering

Deliverable: Source feasibility matrix with evidence and collection recommendations

Dependencies: None

Acceptance criteria:

- [ ] Assess each source for Egyptian coverage, access method and allowed use
- [ ] Record observed limitations, permitted rate limits, available fields and effort
- [ ] Recommend feasible sources and fallbacks without bypassing access controls

## 4. Build pilot Egyptian job collection adapters

Owner: Youssef · Workstream: data-engineering

Deliverable: Reproducible pilot collector and externally stored sample

Dependencies: Source assessment and unified schema

Acceptance criteria:

- [ ] Implement only approved feasible sources from the source assessment
- [ ] Preserve provenance, collection timestamps and source IDs/URLs
- [ ] Record per-source counts, failures, retries and missing-field rates

## 5. Implement validation and data quality reporting

Owner: Youssef · Workstream: data-engineering

Deliverable: Validation rules and per-source quality report

Dependencies: Pilot collection and unified schema

Acceptance criteria:

- [ ] Check schema validity, language, required fields and location coverage
- [ ] Quarantine invalid rows with reason codes
- [ ] Report missingness and pass rates with reviewed examples

## 6. Implement and evaluate cross-source deduplication

Owner: Youssef · Workstream: data-engineering

Deliverable: Deduplication pipeline and labeled duplicate/nonduplicate examples

Dependencies: Pilot collection and quality checks

Acceptance criteria:

- [ ] Combine exact identifiers with evaluated normalized or fuzzy matching
- [ ] Preserve all source provenance and avoid silently merging distinct jobs
- [ ] Report duplicate rate, precision/recall on reviewed examples and error cases

## 7. Design PostgreSQL storage and reproducible loading

Owner: Youssef · Workstream: data-engineering

Deliverable: Migrations, loader and setup instructions

Dependencies: Unified schema and deduplication decisions

Acceptance criteria:

- [ ] Match accepted job and skill contract with keys and indexes
- [ ] Demonstrate idempotent upserts and repeatable load on a small fixture
- [ ] Document access configuration, backup plan and secrets handling

## 8. Measure collection costs and 10,000 unique jobs feasibility

Owner: Youssef · Workstream: data-engineering

Deliverable: Evidence-based volume forecast and cost report

Dependencies: Pilot collection, quality and deduplication evidence

Acceptance criteria:

- [ ] Separate raw listings from unique Egyptian jobs after deduplication
- [ ] Estimate yield per source, overlap, throughput and freshness window
- [ ] Report observed pilot costs and projected cost/time for 10,000 unique jobs
- [ ] State confidence, constraints and go/no-go alternatives; do not guarantee the target

## 9. Prototype structured LLM skill extraction

Owner: David · Workstream: llm-pipeline

Deliverable: Versioned prompt, extraction pipeline and sample outputs

Dependencies: Unified schema and approved representative sample

Acceptance criteria:

- [ ] Consume the accepted job contract and validate structured output
- [ ] Extract skills with source-text evidence on Arabic/English/mixed records
- [ ] Handle retries, malformed output and unsupported inferences explicitly

## 10. Build skill taxonomy and normalization mapping

Owner: David · Workstream: llm-pipeline

Deliverable: Versioned taxonomy, alias mappings and normalization rules

Dependencies: Unified schema; coordinated with extraction prototype

Acceptance criteria:

- [ ] Map synonyms, abbreviations and Arabic/English variants to stable IDs
- [ ] Separate technical skills, soft skills and other agreed categories
- [ ] Preserve raw mentions and unresolved mappings for human review

## 11. Create labeled evaluation set and extraction metrics

Owner: David · Workstream: llm-pipeline

Deliverable: Annotation guide, reviewed dataset and evaluation report

Dependencies: Extraction prototype and taxonomy

Acceptance criteria:

- [ ] Use a representative held-out set with source/language diversity
- [ ] Define annotation and disagreement resolution with Mahmoud
- [ ] Measure extraction precision/recall/F1 and normalization accuracy
- [ ] Document false positives, false negatives and evidence quality; agree thresholds before release

## 12. Benchmark LLM quality, latency and cost

Owner: David · Workstream: llm-pipeline

Deliverable: Measured comparison and recommendation

Dependencies: Evaluation set and extraction prototype

Acceptance criteria:

- [ ] Record model/provider and prompt versions, token use, retries and latency
- [ ] Calculate observed cost per job and projected cost for 10,000 jobs
- [ ] Compare quality against the same evaluation set and document tradeoffs
- [ ] Recommend caching/batching and budget controls based on evidence

## 13. Integrate ingestion, PostgreSQL and skill extraction

Owner: Mahmoud · Workstream: integration

Deliverable: Small end-to-end integration demo and interface documentation

Dependencies: PostgreSQL loader, accepted contract and evaluated extraction

Acceptance criteria:

- [ ] Run a reviewed sample through canonical storage and extraction
- [ ] Verify stable job IDs, provenance and versioned outputs
- [ ] Demonstrate retry/idempotency and clear failure reporting
- [ ] Document configuration and reproducible demo steps

## 14. Establish review checklist and acceptance process

Owner: Mahmoud · Workstream: review

Deliverable: Agreed PR review policy and deliverable checklist

Dependencies: None

Acceptance criteria:

- [ ] Agree evidence required for data, LLM and integration changes
- [ ] Confirm reviewers and issue-to-PR-to-board workflow
- [ ] Record available branch protection and any enforcement limitations

## 15. Define analytics questions and metric specifications

Owner: Mahmoud · Workstream: analytics

Deliverable: Prioritized analytics requirements and metric definitions

Dependencies: Source feasibility and unified schema

Acceptance criteria:

- [ ] Define skill demand, role/location/seniority trends and audience
- [ ] Specify denominators, deduplication, missing-data handling and freshness
- [ ] Label sample/coverage limitations and avoid unsupported market-wide claims
- [ ] Agree filters and API data needs with both workstreams

## 16. Plan website, API and graduation demo

Owner: Mahmoud · Workstream: frontend

Deliverable: Website wireframes, API contract proposal and demo plan

Dependencies: Analytics definitions and integration architecture

Acceptance criteria:

- [ ] Prioritize pages, filters, charts and acceptance criteria
- [ ] Define API responses aligned with approved analytics metrics
- [ ] Estimate implementation, hosting cost and deployment dependencies
- [ ] Agree demo scenario and accessibility/responsive requirements

