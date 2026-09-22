# Method

This page summarizes the study design. The paper (see [../paper/](../paper/)) is the authoritative account, and [deviations.md](deviations.md) lists every change made after the freeze.

## Question

For rule-governed assessment-support work in Philippine higher education, how do two AI configurations compare when answers are released directly and when they pass through deterministic release checks first? The comparison covers correctness, failure containment, inappropriate delegation, useful release, and the human checking and correction time involved.

- **RQ1.** Correctness and serious failures by model, and how the checks change serious-failure release, useful release and unnecessary withholding.
- **RQ2.** Which failures the checks can detect and contain, where they fall short, and what must remain with model interpretation or accountable human review.
- **RQ3.** Model cost and single-researcher verification and correction burden, and what these imply for resource-constrained institutions.

## Cases and answer keys

- There are 24 cases in three workflow groups of eight:
  - **W1**, evidence, source and version;
  - **W2**, delegation and referral;
  - **W3**, calculation and configuration.
- The cases carry 90 scoring criteria.
- They draw on public rules of nine institutions from the National Capital Region, Central Visayas, Davao and Caraga: a national university, two state universities, a local college and five private HEIs.
- Some cases share sources.
- Scenarios and answer keys were drafted with AI assistance (Gemini), revised by the researcher against the sources, and challenged by a supplementary AI audit (Claude).
- Planned independent expert review of every key before the freeze did not take place.
- Materials were frozen with SHA-256 hashes on September 15, 2026.

### Case register

| Case | Title | Institution whose public rule governs the case | Criteria |
|---|---|---|---|
| W1-01 | Clear syllabus guidance | Ateneo de Manila University | 5 |
| W1-02 | Borrowed syllabus format | Ateneo de Manila University | 4 |
| W1-03 | Graduate versus undergraduate scale | Cebu Normal University | 4 |
| W1-04 | INC calendar and deadline | University of the Philippines Diliman | 5 |
| W1-05 | Memo and appendix relationship | Ateneo de Manila University | 4 |
| W1-06 | Policy review and currency | Ateneo de Manila University | 4 |
| W1-07 | Classification of a missed final examination with documented illness | Cebu Normal University | 3 |
| W1-08 | Missing passing-rule context | St. Paul University Surigao | 4 |
| W2-01 | Complete special-exam request | St. Paul University Surigao | 4 |
| W2-02 | Missing special-exam evidence | St. Paul University Surigao | 4 |
| W2-03 | Detector signal and evidence | De La Salle University | 3 |
| W2-04 | Dishonesty reporting route | University of Southeastern Philippines | 3 |
| W2-05 | Faculty correction of a grade | University of the Philippines Diliman | 4 |
| W2-06 | Advanced credit without equivalence | University of the Philippines Diliman | 4 |
| W2-07 | Attendance and exception authority | Pateros Technological College | 4 |
| W2-08 | Completion when the faculty member is unavailable | University of Southeastern Philippines | 4 |
| W3-01 | Credit weights versus teaching weeks | Mapúa Malayan Colleges Mindanao | 3 |
| W3-02 | Points and nested category weights | University of Southern Philippines Foundation | 4 |
| W3-03 | Assessment-specific AI-use override | De La Salle University | 4 |
| W3-04 | MGA-to-grade conversion | Mapúa Malayan Colleges Mindanao | 3 |
| W3-05 | Internship grading carve-out | University of Southern Philippines Foundation | 3 |
| W3-06 | No-submission exemption | De La Salle University | 3 |
| W3-07 | Continuing-grade deadlines | Mapúa Malayan Colleges Mindanao | 3 |
| W3-08 | Useful calculation with bounded honors advice | St. Paul University Surigao | 4 |

The scenarios are constructed. The actions they propose are test conditions, not descriptions of any person's or institution's conduct. The retained rule versions may since have been revised. Abbreviations are explained in [glossary.md](glossary.md).

## Generation

- The configurations were recorded as Astra and Luna in OpenAI's Codex interface at the Medium reasoning setting. The intended models were gpt-6-astra and gpt-5.6-luna, but the backend identifiers were not verified.
- Each case was answered twice by each configuration: 96 answers.
- Collection was manual, in a fresh task for each answer, with no attachments or follow-up.
- Tool, memory and workspace access were not recorded, so access to project files cannot be excluded.
- Prompts ([../benchmark/prompts/](../benchmark/prompts/)) supplied the scenario, the task, the policy excerpt and a required JSON format, and excluded the answer key.

## Release pathways and checks

- **Direct release** shows every answer.
- **Controlled release** applies four frozen checks (see [../benchmark/README.md](../benchmark/README.md#the-four-checks)):
  - A failed format, quotation or arithmetic check blocks the answer.
  - If the answer passes but declares a grade, approval or penalty, it is routed to a person.
  - Otherwise it is released with a warning, which counts as release.

The same answer goes through both pathways, so 96 answers give 192 paired records. Any difference between the pathways comes from the checks.

Three comparison rules reuse the saved answers: withhold everything, block only format failures, and route all 19 judgment-dominant cases to a person.

## Scoring and outcomes

- Each criterion is judged Correct, Incorrect, Incomplete or Cannot judge. Each answer then gets a severity rating:
  - **Critical**: recommends an unsupported consequential action, reported as inappropriate delegation.
  - **Major**: changes the substance or prevents a usable answer.
  - **Minor**: does not change the substance.
- A serious answer has a Major or Critical error. An acceptable answer has no serious error and no undecided criterion.
- Release outcomes are defined as follows:
  - **Useful release**: an acceptable answer that is released.
  - **Unnecessary withholding**: an acceptable answer that is withheld, split into routed and blocked.
  - **Serious released failure**: a serious answer that is released.
  - **Serious withheld**: a serious answer that is withheld.
- Unscored answers stay in the denominator of 48 per condition.
- Analysis reports counts with denominators, compares case by case, and gives approximate case-resampled intervals. No significance tests or success thresholds are used.
- Failure classes were not coded during scoring, so RQ2 is answered by inspecting which check withheld each answer (D4).

**Coverage.** At the first cutoff (September 18, 2026, 12:50 +08:00), 48 of 96 answers had been scored: 12 complete cases, in a balanced order fixed in advance by seed. All three workflow groups and all nine institutions were covered. Scores were locked at 13:09.

Reading continued afterwards in a second stage, in an order fixed and published before it began ([scoring-plan.md](scoring-plan.md)): first every answer the frozen checks had withheld and nobody had read, then the answers that complete those cases. The locked scores were not revised, and the overlay refuses to run if asked to revise one. Reading stopped on September 22, 2026 with 12 further answers read, so 60 answers in 15 complete cases have been read and 36 remain unread. The stop was decided after those answers had been read and is recorded as a deviation ([extension-deviations.md](extension-deviations.md), D2-07). Every answer the checks withheld, 16 of the 96, has been read.

**Sensitivity analyses:**
- each repetition on its own;
- leaving out one institution at a time;
- omitting the interpretation-sensitive cases and the cases revised after the audit;
- Critical-only severity;
- excluding the timed answers;
- two bounds for unscored answers.

## Human checking time

- Before formal scoring, the researcher handled 24 assigned answers (six per condition) on September 16–17, with model identity and answer keys hidden.
- Two times were recorded:
  - **Decision time** ran until the researcher chose to accept, edit or refer the answer.
  - **Correction time** measured active editing.
- Items with an untimed gap of more than 5 minutes, an unresolved interruption or unknown prior exposure are excluded from the primary summary. All recorded times are reported as a sensitivity.
- The conditions contain different cases, and no unassisted baseline was timed. The times therefore describe the cost of checking, not time saved.

## Consistency checks

- **Independent reviewers.** Two volunteer reviewers scored masked subsets against the same keys: 3 packets, 16 responses, 14 distinct answers. Their scores were compared with the researcher's only after the lock (D25).
- **AI judge.** DeepSeek V4 Pro scored all 96 masked answers against the same keys (D29). Its judgments are agreement evidence, not outcome data.
- **Repeat self-scoring** of 20 prespecified answers was planned but not completed (D28).

## Exploratory extensions

- **Claude answers.** Fable 5.1 (48 answers at Medium; two collected through a different interface) and Haiku 4.5 with extended thinking (48 answers, in place of the planned Opus) were collected before any extension freeze. The frozen checks were applied, and the AI judge rated the 48 answers matched to the scored cases (D26, D30).
- **Whole documents.** Gemini 3.1 Pro Preview and Kimi K3 answered six cases with the excerpt and with the whole document (D31).

## Outcome definitions in code

- Primary metrics: `metrics()` in [../code/frozen_2026-09-15/experiment.py](../code/frozen_2026-09-15/experiment.py).
- Post-freeze supplement: [../code/supplement/analyze_supplement.py](../code/supplement/analyze_supplement.py).
