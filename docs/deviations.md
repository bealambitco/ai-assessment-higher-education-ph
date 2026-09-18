# Deviations and post-freeze amendments

This page reproduces the Post-Freeze Analysis Addendum, version 2 (prepared 17 September 2026, updated 18 September 2026; applied at the score lock on 18 September 2026, 13:09 +08:00). It lists every amendment D1–D31 with the problem, the change and the researcher's adoption decision (Section D). The text is unchanged except that document-layout directives were removed and headings were shifted down one level.

The addendum was written for the working packages. Their names map to this repository as follows:

| Name used in the addendum | Where it is in this repository |
|---|---|
| Primary package, "21", frozen files | [`benchmark/`](../benchmark/) and [`code/frozen_2026-09-15/`](../code/frozen_2026-09-15/) |
| Package 22 `06_code/` scripts | [`code/supplement/`](../code/supplement/) and [`code/tests/`](../code/tests/) |
| Package 23 (AI judge, primary answers) | [`extensions/ai-judge-primary/`](../extensions/ai-judge-primary/) |
| Package 24 (document-evidence extension) | [`extensions/document-evidence/`](../extensions/document-evidence/) |
| Package 25 (matched Claude answers, masked forms) | Not published; its identity key is private. Aggregates are in [`results/aggregate/claude_extension_ai_judge.csv`](../results/aggregate/claude_extension_ai_judge.csv) |
| Package 26 (AI judge, Claude answers) | [`extensions/ai-judge-claude/`](../extensions/ai-judge-claude/) |
| `private/`, `scoring/`, `reviewers/returned/`, `analysis/` | Not published (masking keys, per-answer scores, reviewer returns). Aggregate outputs are in [`results/aggregate/`](../results/aggregate/) |
| R001–R144 | Masked answer IDs. The mapping from masked ID to model, repetition and pathway is withheld |
| "R-" codes such as R-31a | Placeholder IDs used while drafting the paper |

Source file SHA-256 (addendum as copied): `7798a0030ae77bdf44683dda0dd6bb342601979b973f3e666e5683e1377762ca`

---

## A. Why this addendum exists

The primary package was frozen on 15 September 2026 at 21:42 Philippine time. All 96 answers were collected, and the 24 timed handling items were completed on 16–17 September. When this addendum was prepared on the afternoon of 17 September, one of 96 scoring forms had been started. No score had been locked or joined to a model or pathway, and no analysis output existed. This addendum was written from the frozen code, protocol and aggregate status files without opening identity keys, pathway decisions or assignments.

A read-only audit of the frozen analysis code found problems that would silently distort several reported results if left unaddressed. They are explained below. None requires regeneration or changes to cases, references or controls. The frozen files remain unchanged. Each amendment adds reporting rules, and where necessary a supplementary computation, that is openly labelled as post-freeze and pre-unmasking. The primary definitions in the frozen `metrics()` function stay authoritative. The supplementary script imports that function, and its tests confirm it reproduces the frozen counts.

Analysis choices made after data collection should be disclosed with their timing and rationale rather than presented as prespecified. The addendum changes reporting and, in D1, D2 and D11, the scoring procedure; it is post-freeze and was written before any score was locked or joined, but it is not blind in a strict sense, because the researcher saw all 96 answers during collection, handled 24 of them and saw 12 control decisions during timing. It was drafted with AI assistance (Claude Opus 5) and takes effect only when adopted by the researcher.

## B. Amendments

### D1. Scoring completeness, stopping rule and order

**Problem.** On the afternoon of 17 September, 95 of 96 answers were unscored. At roughly 5–6 minutes each, completion needs about 8–10 focused hours. The frozen lock requires an explicit status for every scheduled answer.

**Amendment.**
- Record a cutoff in Section D before continuing (recommended: 18 September 2026, 12:00 Asia/Manila). Every answer not scored by then receives Status MISSING with the reason "not scored by the submission cutoff". It stays in the scheduled denominator.
- Report scoring coverage (R-00) and both bounding sensitivities (D6) whenever coverage is below 96.
- **Order option A (recommended when full coverage is unlikely): case-grouped order.** Score all four answers for one case consecutively, taking cases in an order shuffled with the frozen scoring seed 2026091701 and interleaved by workflow (W1, W2, W3, W1, ...), with the four answers within each case also shuffled. Interleaving matters: an alphabetical order would lose the W3 calculation cases first if scoring stops early, and those hold four of the five arithmetic checks central to RQ2. The command `check_scoring_forms.py --case-order` prints this order using case IDs and masked IDs only. This departs from the seeded answer-level order and must be recorded as such.
  - Reasons: the reference is read once per case, which is materially faster, and any partial coverage leaves whole cases complete. The frozen analysis pairs pathways and models within cases, so complete cases keep those comparisons balanced.
  - Risk: seeing answers side by side can create contrast effects. Mitigation: judge each answer against the reference and criteria, not against the other answers, and record the order used.
- **Option B: continue in the index order.** It keeps the prepared order, but a partial stop can leave cases with only some of their four answers.

**Report.** Order used, cutoff, coverage by workflow, and that the order change (if adopted) was decided before any score was joined.

### D2. "Cannot judge" handling

**Problem.** The forms offer "Cannot judge" for Severity and Acceptable. The frozen lock rejects that under Status SCORED. It also rejects Acceptable = Yes when any criterion is "Cannot judge" or severity is Major or Critical.

**Amendment.**
- If an overall judgment is unresolved, set Status to CANNOT_JUDGE and leave a reason.
- A single unresolved criterion may stay "Cannot judge". The answer is then Acceptable = No, with severity recorded as judged. Such answers are counted separately ("other unacceptable") and are treated as unresolved in both bounding sensitivities (D6).
- A form with Status CANNOT_JUDGE needs only a reason; the checker and sync script accept it without severity or acceptability labels.

### D3. Completion timestamps

**Problem.** The repeat-interval and agreement code parses timestamps as ISO 8601. Free-text times such as "September 17, 12:55 PM - 1:01 PM" fail.

**Amendment.** Enter times as `2026-09-17T13:01+08:00`, or let synchronization convert free text using the end of the stated range in Asia/Manila time. Log every conversion. The read-only checker flags each form that needs this.

### D4. Failure-class matching cannot be computed

**Problem.** The frozen join compares the failure class of each check that fired with `failure_classes` in the scores. The scoring forms never collect failure classes, so the field stays empty and `matched_catch` is always false. The frozen sensitivity "unmatched serious catches treated as released" would therefore reverse every serious catch. It would be reported as if it were informative.

**Amendment.**
- Do not interpret that frozen sensitivity. Report it only with this explanation, or omit it with a note.
- Replace it with a check-type table: for controlled answers, which checks fired on serious, acceptable and other answers (supplement S4).
- After unmasking pathway decisions, inspect every serious answer that the controls withheld. Record whether the check that fired corresponds to the scored error: matched, partial or unrelated.
- A withheld serious answer whose check fired for an unrelated reason is reported as a coincidental catch, not as evidence that the check detects that error type.

### D5. Routed acceptable answers

**Problem.** Every routed answer is treated as withheld. A correct answer that declares a consequential action is therefore counted as unnecessary withholding, even though human review of such actions is the purpose of routing.

**Amendment.** Keep the frozen definition as primary. Always report its composition: acceptable answers withheld by routing versus by blocking (supplement S3). Interpret routed-acceptable answers as review workload, and blocked-acceptable answers as lost assistance.

### D6. Bounding sensitivities

**Problem.** The frozen "not scorable as unacceptable" sensitivity sets severity to None, so it cannot increase serious released failures. A single "treat unresolved as serious" rule is also not neutral: it favors the controls, because every unresolved answer they withheld would become a serious answer withheld.

**Amendment.** Report two bounding sensitivities beside Table 1 whenever coverage is incomplete (supplement S6a, S6b). S6a, least favorable to controls: unresolved answers withheld by controls are treated as acceptable, and those released as serious. S6b, least favorable to direct release: all unresolved answers are treated as serious. "Unresolved" covers unscored answers and answers that are unacceptable without a Major or Critical error. Interpret only serious released failures and useful releases under these sensitivities.

### D7. Single-condition intervals

**Problem.** The frozen code computes no interval for single-condition rates.

**Amendment.** Add case-cluster percentile bootstrap intervals for each condition's rates, using the frozen seed 2026091801 and 10,000 resamples (supplement S2). Describe them as sensitivity to benchmark composition, not population bounds. Where resampling is degenerate, report "not estimable". With 24 cases, bootstrap and other large-sample intervals can be too narrow (Bowyer, Aitchison and Ivanova, 2025, ICML). Treat them as approximate, and report beside every paired comparison the number of cases in which controls withheld only serious answers, only acceptable answers, both or neither (supplement S10b). Single-metric better/worse counts (S10) are one-sided by construction, because controls can only withhold, and are not interpreted alone.

### D8. Results by workflow

**Problem.** The paper reports W1–W3 results, but the frozen script does not compute them.

**Amendment.** Supplement S5 computes them with n = 16 per condition. Treat them as descriptive only; no between-workflow inference.

### D9. Repetition consistency

**Amendment.** For each model, report how many cases received the same acceptability label in both repetitions (supplement S7). This describes run-to-run variation under manual collection. The frozen repetition-1 and repetition-2 sensitivities remain.

### D10. Timing records

**Findings from the completed session record:**
- T02: 53 minutes 14 seconds between committing the handling decision and starting Clock 2. Any work in that interval was not timed.
- T16: 11 minutes 54 seconds between the decision and the explicit zero-work completion.
- The session spanned an overnight break after T03.
- The handling interface actually used was the amended `timing/interface_v2` version, not the frozen `code/timed_review.py`.

- T04: prior exposure recorded as UNKNOWN (and 3 minutes 46 seconds before its zero-work record).
- 15 of 24 items needed no correction, so a median correction time including zeros is uninformative.
- Each condition's six items are different cases, so timing differences are confounded with case difficulty.

**Amendment (follows the pre-run plan, which made clean records primary).**
- Primary summaries exclude flagged items: more than five minutes between the decision and the next recorded action (T02, T16), an unresolved interruption (T24) or prior exposure not recorded as NO (T04). All recorded times are a sensitivity.
- Report decision time as median (range; n) and correction time as items needing correction out of n, with the median among those items.
- Report decision and override counts, and state the case confound and the interface amendment.
- Do not subtract or add estimated time.

### D11. Repeat self-scoring

**Problem.** The frozen preparation script stops if any of the 20 items is under 24 hours old. The frozen agreement code counts only pairs at least 24 hours apart. Given the deadline, few or no repeats can meet 24 hours before submission.

**Amendment.**
- Keep 24 hours as the primary rule.
- If the researcher adopts the contingency in Section D, repeats completed 12–24 hours after the first score are reported separately as a short-interval exploratory check, with each interval listed. They are prepared manually from the same masked materials without showing first scores.
- With 20 or fewer pairs, report raw agreement and the two-by-two counts. Report kappa only alongside them, because kappa is unstable at this size.
- If no repeat is completed, report "not completed by submission" and keep the plan for the extension.

### D12. Independent reviewers

**Status (updated 18 September).** Two reviewers returned three packets (A1-Core, D1-Core, D1-Optional): 16 responses, 14 distinct answers, all complete; both consented to acknowledgment. See D25.

**Amendment.** Report the actual coverage at submission. Do not describe the capstone as independently scored. Continue reviewer collection after submission for the journal version, before those reviewers see any results.

### D13. Extension collections

**Status.** Fable (48 answers) and Haiku (48 answers) were collected and parse-checked but not scored. The folder labelled "opus" contains Haiku copies; Opus was not collected. No extension freeze exists.

**Amendment.** Report the extensions as collected but not analysed. Correct the Opus label in the extension record. Any later extension analysis needs its own dated plan before scoring.

### D14. Cost

**Amendment.** Collection used subscription interfaces without attributable usage records. Report attributable model cost as not measured (R-31a, R-31c) rather than estimating per-answer API prices. Generation cost and the review burden remain separate topics.

### D15. Registration wording and record inconsistencies

**Findings.**
- The machine-readable registration lists parameters but not outcomes or decision rules. Those are in the protocol prose and the analysis plan.
- The interpretation-sensitive omission (W1-04, W1-08) exists only in code.
- `protocol/config.json` still records `frozen: false`.
- `qa/QA_REPORT.md` and `qa/RESEARCHER_ACCESS_CONFIRMATION.json` still mention the superseded ChatGPT web plan.

**Amendment.**
- Describe the design as a locally hashed pre-collection protocol, not public preregistration.
- Name the code-defined sensitivity as code-defined.
- Add an erratum note in the release record rather than editing frozen files.

### D16. Collection-order verification

**Finding.** The 96 raw text files have file-system modification times between 11:01 and 11:45 on 16 September. File times show when files were saved, not when answers were generated, so they cannot confirm or refute the prepared interleaved order.

**Amendment.** Report that generation order and isolation are researcher-reported and not independently verifiable. Retain the repetition sensitivity.

### D17. Unmasking and publication

**Amendment.** The joined analysis files contain model labels. Keep `analysis/` private until initial scores are locked and results are final. Publish aggregates and case-level tables only after the timed and repeat scoring stages that depend on masking are finished.

### D18. Exposure sensitivity

**Problem.** The 24 answers handled in the timing exercise are later scored by the same person, and for the 12 controlled items the release decision and check results were visible. Scores for these answers are therefore not blind to control results. The `prior_timing_exposure` field exists in the score file but was unused.

**Amendment.** Report Table 1 counts excluding all 24 timed answers, and separately excluding only the 12 controlled timed answers (supplement S14).

### D19. Inappropriate delegation

**Problem.** The main research question names inappropriate delegation, but no field or computation measured it.

**Amendment.** Following the pre-run definition, inappropriate delegation is reported as answers rated Critical (an unsupported consequential action recommended as actionable), per model over scored answers, within W2, and released under controls (supplement S15). Over-referral was not recorded; report only instances documented in scoring reasons, labeled as incomplete ascertainment.

### D20. Handling decision versus locked score

**Amendment.** Cross-tabulate the handling decision in the timing exercise (accept, minor edit, other) against the locked score class (serious, other unacceptable, acceptable, unscored), by release condition (supplement S13). For each serious answer accepted, inspect the saved final product to record whether the edit removed the error. This shows whether the person in the loop caught what the checks missed, bounded to one familiar researcher.

### D21. Check applicability and block causes

**Amendment.** Report how often each check ran (NOT_APPLICABLE means it did not), and classify blocked answers by cause, including formatting causes (unit label, rounding finer than displayed, duplicate entries, fraction versus percent) and value mismatches (supplement S11). Report withheld answers partitioned by the first failing check (supplement S4), because several checks can fire on one answer.

### D22. Reference rules and interpretation

**Amendment.** The frozen "routing-only" comparator routes every answer in the 19 judgment-dominant cases and releases the five calculation cases; describe it that way. The always-release comparator equals direct release and is not reported separately. A rule is described as better only if it releases no more serious answers and no fewer useful answers; otherwise the trade-off is reported without a verdict. Each sensitivity is reported in full, and the text notes any in which a paired count changes direction.

### D23. Scoring started before adoption

**Finding.** Form R001 was started before this addendum was adopted.

**Amendment.** Record whether any other form was completed before adoption, and report R001's position in the order used.

### D24. W2-07 arithmetic profile

**Finding.** The frozen W2-07 profile records `approved_meetings: 2`, but the recomputation ignores it. If the source counts approved absences toward the limit, correct answers could be blocked; both readings exceed the 20% limit, so only release outcomes, not the case conclusion, could change.

**Resolution.** Checked on September 17, 2026 against the supplied W2-07 excerpt, which states that an approved absence excuses a student from being marked absent. The frozen recomputation (7 illness meetings plus 1 absence from 3 tardies, times 1.5 hours = 12 hours, 22.2% of 54 hours) is therefore correct. No erratum is needed; record Adopt to confirm.

### D25. Independent reviewer returns

**Status (September 17, 2026, evening).** The first return (packet A1-Core, 6 responses, 23 criteria) arrived complete: every criterion, severity, reference-concern and comment field was filled with valid values. Its judgments were not read in preparing this addendum; only field completeness was checked. The file is saved under the reviewer's name in the staging root.

**Amendment.**
- Copy (do not move) each return into `21/reviewers/returned/` unchanged and record the packet, date sent, date returned, responses completed and consent for acknowledgment in `REVIEWER_DISPATCH_LOG.csv`. Keep names out of public files.
- Keep returns unread by the researcher until initial scores are locked.
- After the lock, run `reviewer_agreement.py`. It refuses to run before the lock, extracts each return verbatim with the frozen `scoring.extract_docx`, replaces names with neutral labels (key kept in `private/`), and reports per reviewer and pooled: responses returned and complete; exact criterion agreement; serious-versus-not and acceptable-versus-not agreement with two-by-two counts (kappa only alongside them); reference concerns; and agreement between reviewers on shared anchor responses.
- Report coverage and agreement for the reviewed subset only (R-E1). Do not change locked author scores in light of reviewer judgments; report disagreements, and where a reviewer challenges an answer key, record the challenge and any resulting sensitivity separately.

### D26. Exploratory Claude extension and scoring order C

**Claude extension.** Fable 5.1 (48 answers) and Haiku 4.5 with extended thinking (48 answers, in place of the planned Opus) were collected before any extension freeze. After the primary lock, `extension_controls.py` applies the frozen checks unchanged to all 96 Claude answers. It reports format compliance and block, route, and release counts beside Astra and Luna, plus a desktop-matched sensitivity that drops the two OpenRouter/OpenCode answers from every model. If time allows, `prepare_extension_scoring.py` prepares masked forms for an outcome-independent sample: repetition 1 of one Claude model per case, alternated by seed 2026091702 (12 Fable, 12 Haiku). These are scored and locked separately. Correctness is reported only for that subset, beside Astra and Luna answers to the same cases. Everything is labeled exploratory.

**Scoring order C.** To allow repeat self-scoring at 24 hours or more before the deadline, the unscored answers in the prespecified repeat set are placed within the first 30 answers, mixed with 10 other answers in a seeded random order. The remaining 65 answers follow in case-grouped, workflow-interleaved order. The researcher is not told which answers are in the repeat set. This departs from the seeded answer-level order and is recorded as such.

### D27. Scoring order and cutoff actually used

**Record.** Scoring followed the balanced first-48 order (`scoring/SCORING_INDEX_FALLBACK_48.md`, seed 2026091703), authorized by the researcher on 17 September at 22:05 and fixed before any score was joined: 12 complete cases, four per workflow, all nine institutions. Order C (D26) was not used. The 48th form was completed at 12:50 +08:00 on 18 September, after the recommended noon cutoff; the actual cutoff is recorded as 12:50, and the other 48 answers were marked MISSING ("not scored by the submission cutoff"). Forms R001–R003 were scored after an AI-assisted clarification of the scoring procedure. The R028 form date read 28 September; the synced record was corrected to 18 September and logged (`scoring/SYNC_CORRECTIONS_LOG.md`), and the researcher later corrected the form. Scores were locked at 13:09.

### D28. Repeat self-scoring not completed

**Record.** The frozen repeat procedure requires every prespecified repeat answer to have a first score at least 24 hours old. With half of the answers unscored at the cutoff, it could not run before submission. The paper reports the repeat as not completed; reviewer and AI-judge agreement are reported as consistency checks instead.

### D29. AI judge for the primary answers

**Record.** Package 23: DeepSeek V4 Pro (deepseek/deepseek-v4-pro-0813) through OpenCode and OpenRouter, reasoning High, one fresh session per answer, the same keys and criteria, no human scores, model labels or release decisions. All 96 replies were collected 04:10–04:56 on 18 September (a practice prompt ran at 04:08), before initial scoring was finished; the researcher reported copying them without reading (attestation recorded 11:21). 95 replies were valid at first; J024 was invalid JSON and was re-collected by the researcher on 18 September (first attempt preserved), so all 96 are valid. Agreement was computed only after the lock (`06_code/ai_judge.py --agree`). Metered cost US$0.79 (US$0.80 including the practice prompt).

### D30. AI judge for 48 matched Claude answers

**Record.** Package 26 reuses Package 23's instructions and per-case schema for the 48 Claude answers to the 12 scored cases (forms R097–R144 in Package 25; judge IDs K097–K144), run through the OpenRouter API with reasoning High on 18 September. The first four replies came from one provider (Sail Research); after it proved slow, the remainder were requested from Baidu (the provider of the primary judge run) with DeepSeek as the only fallback. Seven requests failed technically (five truncated at the 6,000-token output limit, one empty, one rate-limited); their first attempts are preserved in `raw_outputs_first_attempts`, and each was retried once with a 16,000-token limit. All 48 are valid. The researcher afterwards scored the two flagged W3-02 answers (R117, R120), knowing the judge's view, and confirmed both as unacceptable (rated Critical, where the judge said Major), and scored R130 (W3-04) acceptable, disagreeing with the judge. The judge's severity calls were not fully consistent with the primary run. Metered cost US$0.99 for the kept replies, about US$1.14 including replaced attempts.

### D31. Document-evidence extension through the API

**Record.** Package 24's 12 prompts per model were sent through the OpenRouter API (`code/run_api.py`) instead of manual chat, with each evidence file pasted into the request as delimited text because the API has no upload; this delivery is recorded in every run record. Gemini was requested as `~google/gemini-pro-latest`, which resolved to google/gemini-3.1-pro-preview; Kimi as moonshotai/kimi-k3. No browsing or tools. Gemini completed 12 of 12 (US$0.72). Kimi completed 12 of 12 (US$1.01): D06 (the longest document) returned empty three times at an 8,000-token limit and succeeded on one technical retry at 32,000 tokens (827 s). Quotations were checked automatically against the evidence files (Gemini 43 of 43, Kimi 80 of 80 found word for word); observations were drafted with AI assistance.

## C. Supplementary code in Package 22

`06_code/check_scoring_forms.py` is a read-only checker for the Markdown forms. It reports blank statuses, judgments, severities and acceptability, unreadable timestamps, and label combinations the frozen lock rejects. With `--case-order` it prints the seeded, workflow-interleaved case order for D1 option A.

`06_code/sync_scoring_forms.py` copies completed forms into `scoring/researcher_scores.json`. It runs as a dry run by default; with `--write` it keeps a timestamped backup and a sync log, converts free-text times to +08:00 with every conversion logged, refuses to run after the lock, and refuses to overwrite a previously synced row whose form is no longer complete. With `--mark-missing` it marks unstarted forms MISSING at the cutoff.

`06_code/analyze_supplement.py` runs only after `scoring/score_lock.json` exists. It verifies the freeze and lock hashes, imports the frozen `metrics()` definition, and writes `analysis/supplement/supplement_results.json` and `placeholder_values.json`. Its computations:
- S1: coverage.
- S2: condition rates with case-cluster intervals.
- S3: routed versus blocked split.
- S4: checks fired by outcome.
- S5: workflow tables.
- S7: repetition consistency.
- S8: timing.
- S9: paper placeholder values.
- S10 and S10b: case-level direction counts and trade-off classes.
- S11: check applicability and block causes.
- S12: criterion correctness, scheduled and scored-only.
- S13: handling decision versus locked score.
- S14: exposure sensitivity.
- S15: inappropriate delegation.
- S16: frozen diagnostics and sensitivities surfaced as counts.
- S6a and S6b: bounding sensitivities.

`06_code/reviewer_agreement.py` compares returned reviewer packets with locked author scores after the lock (D25).

`06_code/test_supplement.py` runs twelve tests on synthetic fixtures. They check agreement with the frozen metrics, expected counts, placeholder mapping, case-direction and trade-off classes, both bounding sensitivities, blocked-acceptable causes, unavailable answers, interval brackets, the timing flags and primary timing rule, handler-versus-score counts, the exposure and delegation outputs, form and sync rules, and that no cache files are written into the code folder. It uses no real data.

## D. Researcher adoption record

| Item | Adopt / Modify / Reject | Researcher note | Date and time (+08:00) |
|---|---|---|---|
| D1 cutoff (recommended 18 Sep 12:00) | Modify | Actual cutoff 12:50 (D27) | 18 Sep 13:09 |
| D1 order: A case-grouped or B index order | Modify | Balanced first-48 order, seed 2026091703 (D27) | 17 Sep 22:05 |
| D2 Cannot-judge handling | Adopt | Applied at the lock | 18 Sep 13:09 |
| D3 timestamps | Adopt | Applied at the lock | 18 Sep 13:09 |
| D4 failure-class replacement | Adopt | Applied at the lock | 18 Sep 13:09 |
| D5 routed/blocked split | Adopt | Applied at the lock | 18 Sep 13:09 |
| D6 bounding sensitivities (S6a, S6b) | Adopt | Applied at the lock | 18 Sep 13:09 |
| D7 case-cluster intervals | Adopt | Applied at the lock | 18 Sep 13:09 |
| D8 workflow tables | Adopt | Applied at the lock | 18 Sep 13:09 |
| D9 repetition consistency | Adopt | Applied at the lock | 18 Sep 13:09 |
| D10 timing reporting | Adopt | Applied at the lock | 18 Sep 13:09 |
| D11 12–24 hour repeat contingency | Not carried out | Repeat not completed (D28) | 18 Sep 13:09 |
| D12 reviewer coverage reporting | Adopt | Applied at the lock | 18 Sep 13:09 |
| D13 extensions not analysed; Opus label | Superseded | Check-level analysis and AI judge (D26, D30) | 18 Sep 13:09 |
| D14 cost not measured | Adopt | Applied at the lock | 18 Sep 13:09 |
| D15 registration wording and errata | Adopt | Applied at the lock | 18 Sep 13:09 |
| D16 collection-order disclosure | Adopt | Applied at the lock | 18 Sep 13:09 |
| D17 unmasking and publication | Adopt | Applied at the lock | 18 Sep 13:09 |
| D18 exposure sensitivity | Adopt | Applied at the lock | 18 Sep 13:09 |
| D19 inappropriate delegation | Adopt | Applied at the lock | 18 Sep 13:09 |
| D20 handling decision versus score | Adopt | Applied at the lock | 18 Sep 13:09 |
| D21 check applicability and block causes | Adopt | Applied at the lock | 18 Sep 13:09 |
| D22 reference rules and interpretation | Adopt | Applied at the lock | 18 Sep 13:09 |
| D23 scoring started before adoption | Adopt | Applied at the lock | 18 Sep 13:09 |
| D24 W2-07 profile confirmed (no erratum) | Adopt | Applied at the lock | 18 Sep 13:09 |
| D25 independent reviewer returns | Adopt | Applied at the lock | 18 Sep 13:09 |
| D26 Claude extension and order C | Modify | Order C not used; Claude answers AI-judged, not human-scored (D30) | 18 Sep 13:09 |

| D27–D31 records of what was done | Record | See sections D27–D31 | 18 Sep |

Compiled from the researcher's recorded actions.

## Known errata in frozen files

The following text errors are in hash-frozen benchmark files and are recorded here rather than edited, so that the freeze record stays verifiable. None affects scoring or the checks.

- `benchmark/answer-keys/W3-01.json`: a duplicated section number ("section 5.4 5.4") and repeated source locators ("Table 1, Section 2.1, Table 1").
- `benchmark/cases/W3-01.json` and `benchmark/answer-keys/W3-01.json`: Mapúa Malayan Colleges Mindanao is referred to as "the university"; it is a college.
