# Results

This folder holds **aggregate tables only**: counts, rates and summaries by model, pathway, workflow group or packet. It contains no per-answer scores, model-to-answer mapping or reviewer identities. The CSV tables also contain no masked answer IDs. The workbook names only the three Claude answers that were confirmation-scored (R117, R120, R130), with their case, as amendment D30 does, and without model labels. The tables were written by [../code/supplement/export_public_tables.py](../code/supplement/export_public_tables.py) from the analysis over every answer that has been read: the 48 locked on September 18, 2026 at 13:09 +08:00, and the 12 read afterwards in the order fixed in [../docs/scoring-plan.md](../docs/scoring-plan.md). The locked judgments were not revised.

The primary conditions are `astra` or `luna` × `direct` or `controlled`. Each condition has 48 scheduled answers, of which 30 have been read. Answers nobody has read stay in the denominator, so a useful release of 30/48 means that all 30 answers read were acceptable and released.

## Workbook

[Analysis_Workbook_FINAL.xlsx](Analysis_Workbook_FINAL.xlsx) presents all of these results in one spreadsheet: a dashboard, primary outcomes, workflows, checks, sensitivity, timing, agreement, the Claude and document extensions, costs and time, source cross-checks, and a data dictionary. It was built from the same locked outputs. In the public copy, the four timing-item IDs in the *Timing* sheet's "Flagged item excluded" column were replaced with "1 (ID withheld)", because they would reveal which condition those masked items belonged to. Nothing else was changed.

[Analysis_Workbook_Supplement_v2.xlsx](Analysis_Workbook_Supplement_v2.xlsx) adds two exploratory analyses: a dated project timeline from design to score lock (calendar spans, not hours worked), and the AI judge's ratings of the 24 document-evidence answers (all acceptable, no serious error; see [../extensions/ai-judge-documents/](../extensions/ai-judge-documents/)).

## Extension

[Analysis_Workbook_Extension.xlsx](Analysis_Workbook_Extension.xlsx) presents the extension collections and the
revised release checks: a dashboard, the before-and-after comparison of the checks, the low-resource,
whole-document and rule-discovery arms, costs reconciled against the provider's billing export, and a data
dictionary. Correctness for the new arms is not established until the answers are scored; every sheet says so.

## Primary study

| File | Contents |
|---|---|
| [aggregate/coverage.csv](aggregate/coverage.csv) | 96 scheduled, 60 read, 0 cannot judge, 36 unread; 12 of the 60 were read after the first cutoff; 4 reference challenges recorded |
| [aggregate/primary_outcomes.csv](aggregate/primary_outcomes.csv) | Paper Table 1: acceptable, serious released, useful release (with an approximate case-resampled 95% interval), acceptable answers withheld (routed or blocked), and release decisions per condition |
| [aggregate/outcomes_by_workflow.csv](aggregate/outcomes_by_workflow.csv) | The same measures for W1, W2 and W3 |
| [aggregate/paired_case_summary.csv](aggregate/paired_case_summary.csv) | Direction of the direct-versus-controlled comparison, case by case; repetition consistency; inappropriate delegation (Critical); criterion correctness |
| [aggregate/check_status.csv](aggregate/check_status.csv) | How each check ended over all 96 answers (pass, fail, not applicable, triggered) |
| [aggregate/checks_by_outcome.csv](aggregate/checks_by_outcome.csv) | Which check fired and which one withheld each scored answer, by score class |
| [aggregate/block_causes.csv](aggregate/block_causes.csv) | Why answers were blocked. The four unit-label rows come from two acceptable answers; one answer can fail several quantities |
| [aggregate/sensitivity_analyses.csv](aggregate/sensitivity_analyses.csv) | Sensitivities and comparison policies over every answer read, including leaving out each institution and each repetition, the two bounding analyses for unread answers and the exposure sensitivities |
| [aggregate/timing_summary.csv](aggregate/timing_summary.csv) | Paper Table G2: decision time (median and range), the number of items needing correction and their correction time. The first columns exclude one flagged item per condition; the clarified columns include the three items the researcher later explained |
| [aggregate/handling_vs_score.csv](aggregate/handling_vs_score.csv) | The researcher's handling decision during timing, set against the later locked score class |
| [aggregate/metered_costs.csv](aggregate/metered_costs.csv) | Metered API costs of the kept extension runs. Billed totals, including replaced or failed attempts, are in the workbook's *Costs and time* sheet. The primary model cost was not measured |

## Consistency checks

| File | Contents |
|---|---|
| [aggregate/reviewer_agreement.csv](aggregate/reviewer_agreement.csv) | Agreement between the independent reviewers and the researcher: criterion 49/53, serious error 15/15, acceptability 15/15, exact severity 11/15, each with its two-by-two counts |
| [aggregate/reviewer_agreement_by_packet.csv](aggregate/reviewer_agreement_by_packet.csv) | Coverage per packet. There are 2 reviewers and 3 packets; Reviewer 2 returned two packets |
| [aggregate/ai_judge_primary_agreement.csv](aggregate/ai_judge_primary_agreement.csv) | AI judge against the researcher on the 60 answers read: acceptability 60/60, serious error 60/60, exact severity 54/60, criterion judgments 219 of 224 |
| [aggregate/ai_judge_primary_distribution.csv](aggregate/ai_judge_primary_distribution.csv) | AI-judge labels over all 96 answers (96 valid) |

## Exploratory extensions

| File | Contents |
|---|---|
| [aggregate/claude_extension_checks.csv](aggregate/claude_extension_checks.csv) | The frozen checks applied to the 48 matched answers per model: released 41 (Astra), 39 (Luna), 38 (Fable), 37 (Haiku). Also a sensitivity that uses the desktop interface only |
| [aggregate/claude_extension_ai_judge.csv](aggregate/claude_extension_ai_judge.csv) | AI judge on the 48 Claude answers: Fable 24/24 acceptable, Haiku 21/24. The researcher's confirmation scoring (not blind) confirmed 2 of the 3 flagged answers as serious |
| [aggregate/document_extension_runs.csv](aggregate/document_extension_runs.csv) | One row per run for Gemini 3.1 Pro Preview and Kimi K3 (excerpt or full document): provider, latency, tokens, OpenRouter-reported cost, and quotations found word for word (43/43 and 80/80) |

## Notes

- Intervals are case-resampled percentile bootstraps. They describe sensitivity to which cases were included, not uncertainty about a population.
- The per-item timing records (researcher's own, no model or pathway labels) are in [../docs/provenance/timing_2026-09-17/](../docs/provenance/timing_2026-09-17/).
- Per-answer scores and masking keys will be released after reviewer reconciliation and the planned repeat scoring (see [../docs/data-statement.md](../docs/data-statement.md)).

## Files kept for the record

`aggregate/superseded_2026-09-18/` holds the tables exactly as they stood when the first 48 answers were
locked. They are superseded by the tables above, which cover every answer read; both are kept so the change
is visible rather than silent.
