# Changelog

## Unreleased

Every answer the release checks withheld has now been read, and the paper, slides, aggregate tables and
workbooks report all 60 answers that have been read rather than the 48 locked on September 18.

- **The answers the checks withheld** (`extensions/withheld-answers/`): the 10 that nobody had read were
  read in an order fixed and published beforehand, together with the 2 that complete their cases. All 16
  answers the checks withheld across the 96 are acceptable; the checks stopped no error. Reading stopped on
  September 22, 2026 by the researcher's decision, recorded as deviation D2-07.
- **A third independent reviewer** returned a Core packet. Agreement is now 49 of 53 criterion judgments,
  15 of 15 on serious error and on acceptability. The packet arrived with its Word form controls flattened;
  a fallback reader recovers the answers from the document text and is required to reproduce the controls
  exactly on every return that still has them (D2-08).
- **Aggregate tables and workbooks regenerated** over every answer read, with the same definitions,
  denominators and bootstrap seed. The tables as they stood at the first lock are kept in
  `results/aggregate/superseded_2026-09-18/`.
- **Quotation membership measured across all 96 answers**: 419 quotations offered, none absent from what the
  model was given. Reported as a post-hoc diagnosis of why three sound answers were blocked (D2-09).
- **Timing** recomputed with the three flagged items the researcher explained on September 21 (D2-06, D2-10);
  both sets of figures are published.
- Revised release checks, specified and hashed before use, re-run over the 192 answers already collected.
- Three further collections through OpenRouter: open-weight models in the 8B-30B range on the same 24 cases,
  whole documents on all 24 cases, and eight cases where no passage is pre-selected.
- Tooling for the remaining human work, a dated protocol, a deviations log and a billing reconciliation.

The locked judgments were not revised, and the overlay refuses to run if asked to revise one. Correctness for
the new collections is not established until those answers are read. Nothing in the benchmark or the frozen
code changed.

## 1.0.1 (2026-09-19)

Slides updated to the version presented on September 19, 2026: slides reordered (see [presentation/README.md](presentation/README.md)), with the same numbers and claims as the paper. No changes to the benchmark, code, results or paper.

## 1.0.0 (2026-09-18)

First public release of the benchmark, code, aggregate results, exploratory extensions, paper and presentation for the AI for Asia Fellowship 2026 capstone.
