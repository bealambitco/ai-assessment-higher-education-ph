# Arm F: a second timer

The primary study measured the cost of checking an AI answer with one stopwatch held by the person who wrote
the cases, the prompts and the answer keys. The paper states this as a limitation. Arm F asks one
colleague, who has not seen the cases, to time ten of the same answers under the same interface and
the same instructions.

Written September 20, 2026, before the session. Round-1 records are not changed by anything here.

## What this arm can establish

- A second, less familiar observer's record of how long it takes to read one AI answer against a
  quoted institutional rule, decide what to do with it, and produce something usable.
- Whether the primary-study times look like an artefact of the author's familiarity with her own cases.
  If the colleague's times are far shorter or far longer, that is worth reporting.
- How a reader who did not write the keys uses the automatic check result: whether they accept a
  withheld answer's routing, or open it.

## What this arm cannot establish

- **Not a time saving.** No one is timed writing these answers without an assistant. There is no
  unassisted baseline in the primary study or round 2. The numbers describe the cost of checking, not time
  saved, and no sentence in the paper may turn them into one.
- **Not a representative sample of teachers.** One person is one person. They are not sampled from
  Philippine higher-education faculty, they are not randomly chosen, and ten items are not a
  workload. Nothing here supports a claim about what teachers in general would take.
- **Not a reliability estimate.** Two timers on different items give no inter-rater statistic. Even
  on shared items, n = 1 against n = 1 would not support one.
- **Not unfamiliarity with the domain.** The colleague is unfamiliar with these cases, not with
  Philippine higher education. That is the point, and it is also a limit.
- **Not a check on the answer keys.** The colleague's decisions are not scores. Arm E reviews the
  keys; arm B scores answers. Arm F records time and handling, nothing else.
- **Not a fix for the single-researcher limitation.** It reduces it on one measure. The study is
  still designed, run and scored by one person.

## How the ten items were chosen

Fixed before the session, in `code/extensions/review/timing_session.py`, and reproducible with:

    python3 -B code/extensions/review/timing_session.py --print-selection

The frame is every (answer, pathway) row of the primary collection: 24 cases x 2 configurations
x 2 repetitions x 2 pathways = 192 rows, read from the public
`benchmark/protocol/primary_generation_order.csv`. Rows are ordered by SHA-256 of a fixed seed
(`round2-armF-second-timer/2026-09-20`) and the row's own identity, and the first ordering that
meets every quota is taken by exhaustive search. The quotas, all fixed before selection:

| Constraint | Value |
|---|---|
| Items | 10 |
| Distinct cases | 10 (no case is seen twice) |
| Configurations | 5 Astra, 5 Luna |
| Pathways | 5 direct, 5 checked |
| Cells | Astra/direct 3, Astra/checked 2, Luna/direct 2, Luna/checked 3 |
| Case bands | W1 3, W2 3, W3 4 |
| Repetitions | 5 first, 5 second |

Ten items cannot split four cells evenly. The two cells that carry the third item, and the band
that carries the fourth, were written into the code before the selection was run and are not
chosen to suit any result.

The selection depends only on the seed and the quotas. It does not read any answer, any check
result, any score or any primary-study timing record, so it could not have been steered toward easy or
hard items. Because the primary-study assignment lives in a private directory that was not opened,
overlap between these ten items and the author's 24 is unknown and is not claimed either way.

**The ten items** (SHA-256 of the selection
`7b8991c93eb39c54c0836cb08178b5fda5429fb7de81642e3d1afa7c63e8b26e`):

| Item | Case | Pathway |
|---|---|---|
| R2-01 | W1-07 | direct |
| R2-02 | W3-08 | checked |
| R2-03 | W3-05 | direct |
| R2-04 | W2-01 | direct |
| R2-05 | W2-03 | checked |
| R2-06 | W1-03 | checked |
| R2-07 | W3-06 | checked |
| R2-08 | W3-07 | checked |
| R2-09 | W1-02 | direct |
| R2-10 | W2-08 | direct |

Which configuration produced each answer is deliberately not printed here, so that this page cannot
be read next to the session. It is fixed by the same seed and is printed by
`--print-selection --show-model` when the record is analysed. The balance is 5 and 5 either way.

Two properties of these ten are consequences of the choice, not criteria for it: all ten answers
were received and parsed, and exactly one item (R2-08) is withheld by the primary-study checks, so the
Inspect rule is exercised once. The check decisions were recomputed from the frozen primary-study gate
over public materials; no private file was opened.

The colleague is shown the timing ID only. Configuration, pathway label, repetition, answer key and
the author's own times and decisions are never on screen.

## Conditions, and what the extension adds

Same as the primary study: two clocks (decision time until accept/edit/refer; correction time for active
work), the same six decisions (`accept`, `minor_edit`, `major_edit`, `reject`, `escalate`,
`accept_gate`), explicit pauses with a reason, and the rule that an answer withheld by the checks
stays hidden unless the timer presses Inspect, which is logged.

The primary study produced four problems that the paper had to handle after the fact (deviations D10). The
extension tool prevents each one rather than reporting it later:

| Round-1 problem | Guard in `timing_session.py` |
|---|---|
| T02: 53 minutes between the decision and the start of Clock 2, untimed | Any gap over 5 minutes between recorded actions stops the interface, warns, and requires a written reason before anything is recorded. The gap is stored with its reason and its seconds. Time is never added or subtracted. |
| T24: an interruption that may have begun before Pause was pressed | Resuming requires an explicit answer to "did the interruption begin before you pressed Pause?". A yes flags the item. |
| T04: prior exposure recorded as UNKNOWN | The prior-exposure question is asked before the answer is shown and accepts only Yes or No. There is no unknown option. |
| Clock values had to be recomputed afterwards | Both clocks are recomputed from the stored timestamps at completion, stored in a `clean_time` block with the flags, and a mismatch with the recorded value is itself a validation failure. |
| Decisions recorded without a usable reason | The interface refuses a decision with no reason, a pause with no reason, and a completion with no final product or disposition. |
| A crash mid-item presented as uninterrupted | Reopening an item that was mid-clock records a restart interruption and opens a pause. The item can never be reported as clean. |

An item is a **clean record** only if it has no long gap, no restart interruption, no pause of
uncertain onset, and prior exposure recorded as No. Flagged items are reported, never silently
dropped and never adjusted.

## Running it

    python3 -B code/extensions/review/timing_session.py --self-test
    python3 -B code/extensions/review/timing_session.py \
        --answers "<staging>/collection/primary" \
        --out "<staging>/30_ROUND2/timing_arm_f/second_timer_record.json"

The tool is local only: it serves `127.0.0.1`, makes no network call and no model call, costs
nothing, and reads no directory named `private/`. The record file must be outside this repository
and the tool refuses to write inside it. The record is saved after every action and the session is
resumable: reopening the same file continues at the first unfinished item. Raw answers stay local,
as in the primary study; only aggregates are published.

Afterwards:

    python3 -B code/extensions/review/timing_session.py --validate "<record file>"

## How results will be reported

- **Beside the author's times, never pooled.** Two rows, two columns, two n's. No combined median,
  no combined range, no "reviewers took on average".
- Decision time as median (range; n) over clean records; correction time as the count of items
  needing correction out of n, with the median among those items. The same form as the primary study, so the
  two rows are readable together.
- All recorded times, flags included, as a sensitivity beside the clean-record summary.
- Decision counts, and the Inspect press if it happens, reported as counts.
- The case confound is restated: the ten items are ten different cases, so any difference between
  conditions is confounded with case difficulty, exactly as in the primary study.
- If the session is not completed, arm F is reported as not completed. Partial items are reported
  as partial. No other arm depends on it.
- The colleague is acknowledged only with their written permission, and never named in a data file.
  The record file holds no name, and no name is committed to this repository.
- Nothing in this arm is a time-saving claim. If a draft sentence reads as one, it is wrong.

## Files

| File | What it is |
|---|---|
| `README.md` | this page |
| `TIMER_INSTRUCTIONS.md` | the single sheet the colleague reads |
| `SESSION_CHECKLIST.md` | what the researcher does before, during and after |
| `../../code/extensions/review/timing_session.py` | the tool |
| `../../code/tests/test_timing_session.py` | its tests |
