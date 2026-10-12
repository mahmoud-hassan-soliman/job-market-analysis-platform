# Architecture proposal

Status: draft, to be reviewed in the architecture issue.

Source adapters → staging and provenance → validation → cross-source deduplication → canonical PostgreSQL jobs → LLM extraction → normalized skills → analytics API → website.

Youssef owns ingestion and canonical data quality. David consumes the agreed job contract and produces versioned extraction results. Mahmoud owns the shared contract, integration and product requirements.

Keep raw source records in restricted external storage, retaining a reference and hash in the canonical record. Collection runs and extraction runs need explicit identifiers, metrics, retries and cost accounting.

Decide together: collection method per source, storage retention, update frequency, database access, LLM provider/model, deployment budget, analytics definitions and dashboard audience. No provider, framework, schedule or budget has been selected.

Integrate a small reviewed sample first. Expand collection only after source feasibility, deduplication and cost estimates are accepted.
