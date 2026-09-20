# Round 2

Work prepared after the capstone release (v1.0.1) to address the paper's own limitations before journal
submission. Round 1 is closed and unchanged; everything here is additional.

Start with [PROTOCOL.md](PROTOCOL.md), which fixes what each arm does before it is run, and
[RUN_COMMANDS.md](RUN_COMMANDS.md), which lists the exact commands.

## Arms and status

| Arm | What it does | Status on 20 September 2026 |
|---|---|---|
| A. Revised checks | The revised checks, run over every answer collected for the primary comparison | **Done.** [Findings](results/CHECKS_V2_FINDINGS.md) |
| B. Scoring and failure classes | Score the 48 unscored primary answers, the 96 Claude answers and the extension answers; code failure classes | Tools ready and verified; scoring under way |
| C. Whole documents | All 24 cases with the governing document attached | **Collected.** 24 answers from Gemini 3.1 Pro Preview, 23 of 24 from Kimi K3. [Findings](results/EXTENSION_ARMS_FINDINGS.md) |
| D. Rule discovery | Eight cases with the institution's documents and no passage selected | **Collected.** 8 answers from each of two configurations |
| E. Answer-key review | Philippine higher-education experts validate the keys | Four packets of six cases each, Core and Optional, ready to send |
| F. Second timer | A colleague times ten answers | Tool and instructions ready; session to be scheduled |
| G. Low-resource models | Open-weight 8B–30B models on the same 24 cases | **Collected.** 24 answers from each of three configurations |

Correctness for arms C, D and G is not established until the answers are scored; the findings above report
coverage, format, quotation membership, release decisions, time and cost only.

## What arm A found

The revised checks recovered the two acceptable answers that round 1 blocked over unit wording, and
contained both confirmed Claude Haiku errors that round 1 released, without withholding any answer scored
acceptable. Under the reading fixed before the run, that is an improvement on this evidence. The details,
including what the rules did not change and what the comparison cannot show, are in
[results/CHECKS_V2_FINDINGS.md](results/CHECKS_V2_FINDINGS.md).

## Where the work lives

The working copy is the local package `30_ROUND2_EXTENSION`, beside packages 21 to 29, which also holds the
prompts, raw replies, per-answer tables, reviewer packets and score file. This folder is the published
subset. `code/extensions/round2/sync_local_and_repo.py` keeps the two in step and records every hash it
copied.

## What is published here and what is not

Published: the protocol, the specifications, the code, the document map (names and hashes), aggregate
results and the reviewer materials. Not published: raw model answers, per-answer scores, masked identifiers,
reviewer names and document text, exactly as in round 1.

## Folders

| Path | Contents |
|---|---|
| [CHECKS_V2_SPEC.md](CHECKS_V2_SPEC.md) | The revised check rules, fixed and hashed before use |
| [DEVIATIONS.md](DEVIATIONS.md) | Every departure from the protocol, dated and appended |
| [results/](results/) | Aggregate CSVs, the revised-checks findings and the extension-arm findings |
| [scoring/](scoring/) | Scoring order, failure classes and instructions for arm B |
| [documents/](documents/) | Which document governs which case, with hashes |
| [rule-discovery/](rule-discovery/) | The eight cases for arm D and why they were chosen |
| [access-arm/](access-arm/) | The low-resource models and what the arm can claim |
| [key-review/](key-review/) | Packets, reviewer instructions and intake for arm E |
| [second-timer/](second-timer/) | Tool, instructions and session checklist for arm F |
| [confirmed_errors.json](confirmed_errors.json) | Answers confirmed wrong by hand in round 1, used by arm A |

Code for all of it is in [../../code/extensions/round2/](../../code/extensions/round2/), with tests in
[../../code/tests/](../../code/tests/).
