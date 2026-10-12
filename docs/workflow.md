# Team workflow

1. Pick an issue with a named owner and agreed dependencies; agree its target date.
2. Move it to In Progress and create a feature branch from current main.
3. Implement or document the deliverable and attach acceptance evidence.
4. Open a pull request, link the issue and move it to In Review.
5. Reviewer checks evidence, data handling, shared contracts and cost impact.
6. Merge after review; close the issue and move it to Done.

Main protection, when available, should require a pull request, one approval, stale-review dismissal and resolved conversations, with force pushes and deletions disabled. Do not require nonexistent CI checks.

If private repository protection is unavailable on the account plan, the same review policy is a team convention and is not technically enforced. The setup report records the actual API outcome.

Initial workstream branches are starting points. Prefer per-issue branches to keep reviews focused. GitHub usernames, collaborator access and due dates must be provided rather than inferred.
