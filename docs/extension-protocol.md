# Extension protocol

Written September 20, 2026, before any extension collection, scoring or analysis. The primary study (release v1.0.1) is
closed: its cases, checks, answers, scores and results are unchanged by anything here. Extension adds arms and
re-analyses answers already collected, so that the study can be submitted to a journal with its main
limitations addressed rather than only stated.

Nothing in this protocol changes the title, the research questions or the frozen primary-study materials.

## Why a second round

The paper names five limits (Section 5, Appendices C and E). Four of them can be reduced in weeks rather
than months:

| Round-1 limit | What the extension does about it |
|---|---|
| The answer keys were drafted with AI help and adjudicated by the author alone | Independent review of the keys by two Philippine higher-education experts (arm E) |
| Only 48 of 96 answers were scored; failure classes were never coded, so RQ2 was answered indirectly | Score the remaining answers and code failure classes while scoring (arm B) |
| The checks reacted to labels rather than errors, and Section 6.3 recommends a fix that was never tested | Re-run revised checks over every answer already collected (arm A) |
| The rule was always supplied, and only excerpt-sized | Whole documents over all 24 cases (arm C) and a rule-discovery arm (arm D) |
| Timing came from one person who wrote the cases | A second timer on a subset (arm F) |

The fifth limit, that one researcher designed, ran and scored the study, is reduced by arms E and F but not
removed. Extension does not claim to remove it.

## Arms

Each arm is independent. An arm that is not completed is reported as not completed; no result depends on
another arm finishing.

### A. Checks v2 on existing answers (no new collection)

Specification: [CHECKS_V2_SPEC.md](../extensions/revised-checks/SPECIFICATION.md), fixed before the first run. The revised checks are
applied to the 96 primary answers (Astra, Luna) and the 96 Claude answers (Fable, Haiku) already collected.
Human scores are the ones locked on September 18, 2026 and are not revised. The pre-specified reading of the
result is in the specification and is not changed afterwards.

### B. Scoring the remaining answers, with failure classes

The 48 unscored primary answers are scored first, in the order fixed in
[scoring/ORDER.md](scoring-plan.md), followed by the 96 Claude answers. Every answer scored in the extension also
receives failure-class codes from the fixed list in [scoring/FAILURE_CLASSES.md](failure-classes.md),
which answers RQ2 as written rather than by inference. Round-1 scores are never revised; where a extension
score would contradict one, the disagreement is recorded, not resolved by overwriting.

Masking is partial, as in the primary study: the scorer saw the answers during collection. Model identity is hidden at
scoring time; the limitation stands and is restated in the paper.

### C. Whole documents over all 24 cases

The primary study gave two models (Gemini 3.1 Pro Preview, Kimi K3) whole documents for six cases, and no person scored
those answers. Extension covers all 24 cases with one answer per condition, and the answers are scored by the
researcher under the same keys and criteria. Runner:
[../code/extensions/collection/run_openrouter.py](../code/extensions/collection/run_openrouter.py).

### D. Rule discovery

The hardest question the paper raises is whether an assistant can find the governing rule itself. In this
arm the prompt contains the scenario and the task, and a bundle of that institution's retained documents,
without pointing at the passage. Coverage is eight cases, chosen in advance and listed in
[rule-discovery/CASES.md](../extensions/rule-discovery/README.md); the answer key and checks are unchanged. Reported
separately from the main comparison: the design differs, so it is not pooled with primary-study results.

### E. Answer-key review

Independent Philippine higher-education experts review the keys, judging each criterion and each locator.
Four packets of six cases each cover all 24 cases with no overlap, split into Core and Optional files of
three cases, so a reviewer can commit to about twenty pages ([key-review/PACKETS.md](../extensions/answer-key-review/PACKETS.md)). Packets, instructions and intake are in [key-review/](../extensions/answer-key-review/). What
this arm can establish: whether a qualified reader accepts each reference answer under the quoted rule. What
it cannot: whether the model answers were scored correctly, which is arm B's question. Every challenged
criterion is recorded; a key changes only by a dated note, never silently, and any change triggers a re-score
of the affected answers under both the old and new key, with both results reported.

### F. Second timer

One colleague, not the case author, times ten answers under the primary-study interface and instructions, so the
verification burden has a second, less familiar observer. Their times are reported beside the author's, not
pooled with them. Scope, the fixed ten-item selection, the session materials and the reporting rule are in
[second-timer/](../extensions/second-timer/); the tool is
[../code/extensions/review/timing_session.py](../code/extensions/review/timing_session.py), with tests in
[../code/tests/test_timing_session.py](../code/tests/test_timing_session.py). The selection is fixed by a
published seed and quotas and reads no answer, score or check result; its SHA-256 is recorded in that README.
The arm adds guards for the four primary-study timing problems (D10) but changes no primary-study record.

### G. Low-resource models (access arm)

Open-weight models in the 8B–30B range, which a school could legally self-host, answer the same 24 cases
through a hosted aggregator (OpenRouter). Models and settings are fixed in
[access-arm/MODELS.md](../extensions/low-resource-models/README.md). This arm tests model capability under a constrained budget. It
is not an offline deployment: prompts still leave the country and touch third-party infrastructure, the
provider serves higher precision than a school running a quantized copy would, and no latency, privacy or
hardware claim follows. Reported as an upper bound on what a self-hosting school could achieve, with an
optional local spot-check on two cases to bound the gap.

## What is fixed before collection

* **Materials.** Cases, answer keys, prompts, control profiles and the primary-study checks stay as frozen on
  September 15, 2026. Extension adds files; it changes none of them.
* **Checks v2.** Specification and implementation hashed below before the first run.
* **Scoring order and cutoff.** Fixed in `scoring/ORDER.md`; the cutoff is a date, not a result.
* **Failure classes.** Fixed list; a class may be added only with a dated note, and answers already scored
  are then re-read for that class.
* **Reading of arm A.** Stated in the specification before the first run.
* **What counts as a changed conclusion.** A primary-study conclusion is treated as changed if, on the full 96
  answers, any serious released failure appears in the primary comparison, or if the direction of the
  direct-versus-checked comparison reverses for a configuration. Anything else is a refinement and is
  reported as such.

## What stays true regardless of results

* No answer, score or check output is deleted or overwritten. Round-2 outputs live beside primary-study outputs.
* Unscored answers stay in every denominator.
* Costs are recorded per run from the provider's own billing export, kept and billed separately.
* Raw model answers are not published; aggregates are.
* No student data, no real institutional decisions, no deployment. Scenarios remain constructed.
* AI assistance in the extension is disclosed in the same way as the primary study, in the paper's declarations.

## Freeze record

SHA-256 of the extension materials fixed before the first run of arm A.

| File | SHA-256 |
|---|---|
| `extensions/revised-checks/SPECIFICATION.md` | `2e2a4c2a5f049291ffaf79e23c7839039b3883de35ca28dc3e5b20a0f591a8cd` |
| `code/extensions/revised_checks/checks.py` | `64b4817e453a0d3aa667cb2c4e3b95f59bfadff7a08d1eb3f553b2f81d08ec2e` |
| `code/tests/test_revised_checks.py` | `63c80b7d028b5d22433b6821894e8b7801a7419ce4d4bf5dc855e73ca5939c4c` |
| `code/extensions/revised_checks/rerun.py` | `6199969627e851a3f9e9cdd07e6aed5dd4826a38effea2db6d081b0403111ffb` |
| `extensions/revised-checks/confirmed-errors.json` | `bd99a106b1f486040fc1259e6a99bb88f28de82b006e937b803d1658706e0454` |

A second correction, also on September 20, 2026, after the first run of arm A: `rerun.py` recorded the absolute path of the answers directory in its run record, which would have published a personal path. It now records only the model names. The rules are untouched and arm A was not re-run for it; the superseded hash was `513a42351d3e…`.

### Renaming for publication, 21 September 2026

The files below were renamed and moved so the repository reads as one project rather than as a versioned
add-on: the specification, code and records now sit beside the study's other extensions and documents. Paths,
output file names and one link inside the specification changed; no rule, threshold or result changed, and
re-running the comparison reproduced every decision, including the pre-specified reading. The table below
supersedes the one above, which is kept as the record of what was frozen before the first run.

| `extensions/revised-checks/SPECIFICATION.md` | `f3a82d0e3b39594aaa014fdc50df4ed1f352a248447f8e6fee131c798c691ac6` |
| `code/extensions/revised_checks/checks.py` | `fe70366084c076c480a0e105e7d4fbb333d127b93f9eb15f4d7d8745de13e0f9` |
| `code/tests/test_revised_checks.py` | `3dffa1401863f5f3ffba86361f1f0a5e8ebbe652338ebc582ea693389f82920f` |
| `code/extensions/revised_checks/rerun.py` | `33d479806404564828d730a9486dcc1e2f8a294e49911005dd49e38801e038df` |
| `extensions/revised-checks/confirmed-errors.json` | `7a730b38ca49fc1700f6cf0b00e2a4f215b44ba8ab2253b322242033c3c392d1` |

Recomputed by `python3 -B code/extensions/revised_checks/freeze.py --verify`. If a file changes, the change
is a new dated row here, with the reason; rows are never edited in place.

## Roles

The researcher scores answers, runs every paid call with her own key, corresponds with reviewers and the
second timer, and commits and pushes every change. AI assistance (Claude) prepares code, prompts, packets,
documents and analysis, and runs nothing that costs money. This division is recorded in the paper's
declarations, as in the primary study.
