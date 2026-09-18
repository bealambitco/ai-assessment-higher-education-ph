# Provenance records

These are historical records of how the benchmark was built and handled. They are kept for transparency. They are **not** the final benchmark files; those are in [../../benchmark/](../../benchmark/).

| Folder or file | Contents |
|---|---|
| [case-development/](case-development/README.md) | For each of the 24 cases: construction prompt and response; the researcher's initial review; revision prompt and response (23 cases); second-review candidate, record and summary; and supplementary AI-audit prompt, raw and parsed reply, and receipt. The targets in these folders are historical, not the frozen cases. |
| [development-logs/](development-logs/README.md) | Second-review time log and AI-audit receipts (September 13, 2026). |
| [timing_2026-09-17/](timing_2026-09-17/READ_ME.md) | The researcher's 24 timed handling records, with decisions, reasons, final products, clocks and pauses, plus the completeness check and clarifications. Items are identified as T01–T24 only. Their assignment to model and pathway is withheld. |
| [artifact-manifest_2026-09-13.json](artifact-manifest_2026-09-13.json) | SHA-256 manifest from the September 13 copy. Its paths use the earlier repository layout, and it lists policy copies that are no longer published. |
| [frozen-snapshot-README_2026-09-17.md](frozen-snapshot-README_2026-09-17.md) | Note written when the frozen subset was first copied (September 17). It describes the state at that time. |

Raw records keep their original wording, internal labels and identifiers. The only exceptions:
- Absolute local paths were replaced by `<PROJECT_ROOT>/` in 30 raw prompt files.
- Links in 49 editorial summaries were repointed from policy copies to the source register.

Both changes are listed with before and after SHA-256 values in [../path-mapping.md](../path-mapping.md).
