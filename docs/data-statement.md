# Data statement

## What is published

| Material | Where | Notes |
|---|---|---|
| 24 cases, 24 answer keys, 24 prompts, check profiles, output schema and protocol files, all frozen September 15, 2026 | [../benchmark/](../benchmark/) | The files are byte-identical to the freeze. The scenarios are constructed; there are no real students or student records. |
| Frozen code and the post-freeze analysis code | [../code/](../code/) | |
| Aggregate results | [../results/aggregate/](../results/aggregate/) | Counts and summaries only |
| AI-judge prompts, raw replies and parsed judgments (96 primary answers, 48 Claude answers) | [../extensions/](../extensions/) | These records contain the original model answers, keyed by judge alias IDs |
| Document-evidence prompts, evidence **excerpts**, raw replies and run records | [../extensions/document-evidence/](../extensions/document-evidence/) | The full documents are withheld (see below) |
| Case-development records: construction, revision, human review and AI audit | [provenance/case-development/](provenance/case-development/) | Absolute local paths were replaced (see [path-mapping.md](path-mapping.md)) |
| The researcher's own timing records (24 items) | [provenance/timing_2026-09-17/](provenance/timing_2026-09-17/) | These carry no model or pathway labels |
| Source registers | [../literature/](../literature/) | Links and hashes, no full texts |

## What is withheld, and why

| Material | Reason | Plan |
|---|---|---|
| Masking keys: masked ID to model, repetition and pathway; judge ID to masked ID; timing and repeat assignments; the four private files in the freeze record | The release retains privacy and masking boundaries; repeat scoring was not completed by the cutoff | Any later release requires a separate privacy and reconciliation decision, recorded in [../CHANGELOG.md](../CHANGELOG.md) |
| Per-answer human scores and scoring forms | These can be joined with the masking keys only after release. The results folder is aggregate only. | Subject to a later release decision; not promised |
| Returned reviewer packets and extracted reviewer files | They contain the reviewers' names; the reviewers are identified publicly only as Reviewer 1 and Reviewer 2 | Not planned |
| Full institutional documents, including the full-text renderings used in the document-evidence extension | Redistribution rights were not verified. The source register notes "cite; do not redistribute in full". Some HTML snapshots contain institutional contact emails. | Links, access dates and SHA-256 values are in [../literature/institutional-sources.csv](../literature/institutional-sources.csv) |
| OpenRouter activity exports | They contain API key labels | Only aggregate costs are published |
| Chat archives, working drafts and staging workbooks | Internal working material | Not planned |

## Collection facts

- **Scores.** Primary answers were collected by hand through a subscription interface after the September 15, 2026 freeze. Scores were locked on September 18, 2026 at 13:09 +08:00, with a scoring cutoff of 12:50.
- **Languages.** The cases and answers are in English. The source excerpts are quoted in their original wording.
- **Personal data.** There is no student personal data. The one person whose handling times appear is the researcher. The reviewers are not named in this repository.
- **Source currency.** Institutional rules were retrieved between August 30 and September 2, 2026, and some were rechecked on September 10–13. They may have changed since.
