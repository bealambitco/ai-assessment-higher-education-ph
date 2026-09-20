# Round-2 scoring order and cutoff

Fixed on September 20, 2026, before the first extension score, as required by
[extension-protocol.md](extension-protocol.md) ("Scoring order and cutoff. Fixed in `scoring/ORDER.md`; the cutoff is a
date, not a result"). Nothing below depends on what any answer turns out to say.

## What is scored

| Set | Answers | Where |
|---|---|---|
| Primary answers the primary study left unscored | 48 | `collection/primary/{astra,luna}/rep_{1,2}` |
| Claude answers, none of them scored | 96 | `collection/extension/{fable,haiku}/rep_{1,2}` |
| **Total** | **144** | |

The primary study scored 48 of the 96 primary answers before the September 18, 2026 lock, and it scored them as
complete cases: twelve of the twenty-four cases have all four primary answers scored, twelve have none. The
48 that remain are therefore exactly the four primary answers of the other twelve cases, and the set can be
derived without opening any masked-identity file — a case whose primary-study records are all `SCORED` drops out,
a case whose primary-study records are all `MISSING` stays in. Round-1 scores are never revised.

Masked IDs (R001–R096) belong to the primary study and its private identity key. They are not used here and do not
appear in this repository. The list below is keyed by case, configuration and repetition.

## The order

Answers are scored in **case blocks**: every answer of one case is scored consecutively, so the policy
excerpt is read once per case rather than once per answer. This is the order option the researcher adopted
in the primary study (order option A in [deviations.md](deviations.md), and the
fallback-first index of September 17), kept for continuity.

Four parts, in this order:

* **Part A — the answers the checks withheld and nobody scored (10 answers).** These come first because
  they are the only answers that can say whether the holds were worth their cost. A hold on an answer that
  was never read is neither a catch nor a false alarm; it is an unpaid bill. Ten primary answers were
  blocked or routed by the frozen checks and left unscored — three blocked, seven routed. Until they are
  read, every statement in the paper about what the checks bought is conditional on them.
* **Part B — the remaining 38 unscored primary answers.** The two answers that complete the Part-A cases
  come first, so no case is left half-read; then the nine untouched cases.
* **Part C — the 21 Claude answers the checks withheld (17 blocked, 4 routed).** Same reason as Part A.
* **Part D — the remaining 75 Claude answers.**

Within a part, case blocks are ordered by interleaving the workflow groups (W1, W2, W3, W1, …) and, inside
each workflow, taking the case whose institution has been used least so far, ties broken by case ID. Cases
already opened in an earlier part are completed first. Interleaving matters for the same reason it did in
the primary study: an alphabetical order would lose the W3 calculation cases first if scoring stops early, and those
carry four of the five arithmetic checks that RQ2 turns on. Institution spreading matters because nine
institutions are unevenly represented, and a partial stop should not leave a single institution unread.

The rule is deterministic — no seed, no shuffle at the case level — so anyone with the repository and the
collection can regenerate this list and compare it with the table below:

```
python3 -B code/extensions/review/score_answers.py --print-order \
    --collection "<collection>" --round1-scores "<21_.../scoring/researcher_scores.json"
```

### Part A and Part B: the 48 remaining primary answers

| Block | Case | Workflow | Institution | Answers in the block (configuration, repetition) | Round-1 check |
|---|---|---|---|---|---|
| A1 | W1-01 | W1 | Ateneo de Manila University | Astra r1; Astra r2; Luna r1 | block |
| A2 | W3-07 | W3 | Mapúa Malayan Colleges Mindanao | Astra r1; Astra r2; Luna r1; Luna r2 | route |
| A3 | W1-07 | W1 | Cebu Normal University | Astra r1; Astra r2; Luna r2 | route |
| B1 | W1-01 | W1 | Ateneo de Manila University | Luna r2 | release with warning |
| B2 | W1-07 | W1 | Cebu Normal University | Luna r1 | release with warning |
| B3 | W1-04 | W1 | University of the Philippines Diliman | Astra r1; Astra r2; Luna r1; Luna r2 | release with warning |
| B4 | W2-01 | W2 | St. Paul University Surigao | Astra r1; Astra r2; Luna r1; Luna r2 | release with warning |
| B5 | W3-01 | W3 | Mapúa Malayan Colleges Mindanao | Astra r1; Astra r2; Luna r1; Luna r2 | release with warning |
| B6 | W1-08 | W1 | St. Paul University Surigao | Astra r1; Astra r2; Luna r1; Luna r2 | release with warning |
| B7 | W2-04 | W2 | University of Southeastern Philippines | Astra r1; Astra r2; Luna r1; Luna r2 | release with warning |
| B8 | W3-03 | W3 | De La Salle University | Astra r1; Astra r2; Luna r1; Luna r2 | release with warning |
| B9 | W2-06 | W2 | University of the Philippines Diliman | Astra r1; Astra r2; Luna r1; Luna r2 | release with warning |
| B10 | W3-06 | W3 | De La Salle University | Astra r1; Astra r2; Luna r1; Luna r2 | release with warning |
| B11 | W2-02 | W2 | St. Paul University Surigao | Astra r1; Astra r2; Luna r1; Luna r2 | release with warning |

Block order is the order above. **The order of the answers inside a block is not published here.** It is set
by a seeded shuffle (frozen scoring seed 2026091701, the primary-study seed, mixed with the case ID) that the
scoring tool reproduces, with any withheld answers placed first inside their block, blocked before routed.
The primary study shuffled within the case block for the same reason. The effect is that this document registers
completely which answers are scored and in which case order, without telling the scorer which screen belongs
to which configuration.

Two masking limits are stated plainly rather than engineered away. First, Part A membership is itself
informative: a reader of this document knows that three of the four W1-01 answers were blocked and which
configurations they came from. Second, and larger, the scorer collected these answers herself in the primary study and
has seen them before. Masking in this study is partial, as [extension-protocol.md](extension-protocol.md) says under arm
B, and the limitation is restated in the paper rather than claimed away.

### Part C and Part D: the 96 Claude answers

Part C covers the 21 Claude answers the frozen checks withheld, in case blocks:

W1-01 (3), W2-03 (2), W3-01 (3), W1-04 (2), W2-07 (2), W3-02 (2), W1-07 (1), W2-08 (1), W3-04 (3),
W1-02 (1), W3-07 (1).

Part D covers the remaining 75, completing those eleven cases first and then taking the remaining thirteen
cases under the same workflow and institution rule. The full 144-row list, with every configuration and
repetition, is printed by the `--print-order` command above and is not transcribed here; the two parts
together are all 96 Claude answers, and none of them was scored in the primary study.

## Cutoff

**Round-2 arm B scoring stops at 23:59 Asia/Manila on Monday, November 30, 2026.** Whatever has been scored
by then is what arm B reports.

Two interim dates are fixed with it, for planning only; missing one does not change the cutoff and does not
license extending it:

* **October 31, 2026** — Parts A and B, the 48 primary answers, so the primary comparison is complete on the
  full 96 for the first time.
* **November 30, 2026** — Parts C and D, as far as they get.

The cutoff is a date. It is not "when the results stabilise", not "when enough answers are scored to
separate the arms", and not "when the primary comparison is complete". Nothing about what the scores say may
move it. This is the same discipline the primary study used, and the reason for it is the same: a stopping rule that
reads the data is a stopping rule that can be steered by it.

What happens at the cutoff:

1. Scoring stops. Any answer in progress is finished or abandoned; a half-entered record is recorded
   `MISSING` with the reason, never guessed at.
2. Every finished record is locked (`--lock`). Locked records are not revised.
3. **Unscored answers stay in every denominator.** An answer not reached by November 30 is reported as
   unscored, in the same way the primary study reported its 48. Coverage is reported per part, so a reader can see
   that Part A was complete even if Part D was not.
4. The count scored per part, and the date scoring actually stopped, are reported whether or not they match
   this plan.

If scoring finishes early, it finishes early; the cutoff is a limit, not a schedule to fill.

## Changes to this document

Like the failure-class list, this order may be changed only by a dated note at the end of this file, stating
the date, what changed and why, with the rows above left as written. A change made after scoring has started
is reported in the paper as a deviation, in the same form as the primary-study deviations.

## Dated notes

*None yet.*
