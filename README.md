# Job Market Analysis Platform

Graduation project for analyzing Egyptian job demand and extracting normalized skills from job descriptions.

## Team workstreams

| Owner | Workstream | Deliverables |
| --- | --- | --- |
| Youssef | Data engineering | Source feasibility, collection, quality, deduplication, PostgreSQL, volume and cost estimates |
| David | LLM pipeline | Skill extraction, taxonomy, normalization, evaluation and cost estimates |
| Mahmoud | Architecture and integration | Unified schema, integration, reviews, analytics and website planning |

Named owners are planning responsibilities. GitHub assignments and collaborator invitations wait for verified handles.

## Repository layout

- `data-engineering/`: collection, validation, deduplication and database work.
- `llm-pipeline/`: extraction, normalization and evaluation.
- `backend/`: future integration and API implementation.
- `frontend/`: future dashboard and website implementation.
- `docs/`: architecture, contracts, task plan and decisions.

This is a planning scaffold; collectors, an LLM service and the website are not implemented yet.

## Collaboration

Create short-lived branches from current `main`: `feature/<issue-number>-<description>`.
Initial workstream branches: `feature/data-engineering`, `feature/llm-pipeline`, `feature/architecture`.
Submit a pull request linked to its issue. Mahmoud reviews integration and contracts; changes by Mahmoud should get peer review.
Merge reviewed pull requests into `main`; use squash merges and avoid direct pushes.

Board states: **To Do → In Progress → In Review → Done**.
Move to In Review when a PR or reviewable deliverable is ready; Done requires accepted evidence and completed criteria.
Deadlines and implementation targets must be agreed by the team; none are invented here.

## Data and credentials

Keep raw datasets and large exports in restricted external storage such as Google Drive. Record access instructions and checksums, not credentials, in documentation.
Commit only small synthetic or approved anonymized fixtures. Use `.env.example` for variable names and `.env` for local secrets.
Assess source access and allowed collection methods before building each collector. Do not assume any source can deliver 10,000 unique jobs.

Start with [the task plan](docs/work-plan.md), [the draft data contract](docs/unified-schema.md) and [the architecture](docs/architecture.md).
