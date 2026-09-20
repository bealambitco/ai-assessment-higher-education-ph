# How to score the remaining answers

Arm B of [the extension protocol](extension-protocol.md). You are scoring 144 answers: the 48 primary answers the primary study left
unscored, then the 96 Claude answers. Everything runs on your machine. Nothing is sent anywhere and nothing
costs money.

## Before you start

Read [failure-classes.md](failure-classes.md) once, all of it. It is short, and it is the one thing you
cannot look up mid-answer without losing your place. [scoring-plan.md](scoring-plan.md) is the record of what is scored
in what order; you do not need it to score, and you are better off not reading its table.

Decide where your score file lives. It must be **outside this repository** — it holds the mapping from
scoring ID to model, which is never published. Somewhere like
`~/Documents/round2-scores/extension_scores.json` is fine. The tool refuses a path inside the repository.

Set two shell variables so the commands below fit on one line:

```
COLLECTION="<21_EXPERIMENT_EXECUTION_PACKAGE>/collection"
SCORES="$HOME/Documents/round2-scores/extension_scores.json"
ROUND1="<21_EXPERIMENT_EXECUTION_PACKAGE>/scoring/researcher_scores.json"
```

## The commands

Run them from the repository root.

**Check the tool works, on invented data, touching nothing real:**

```
python3 -B code/extensions/review/score_answers.py --self-test
```

**See what is queued (writes nothing):**

```
python3 -B code/extensions/review/score_answers.py --status \
    --collection "$COLLECTION" --round1-scores "$ROUND1"
```

Expect 96 primary answers found, 48 scored in the primary study, 48 left; 96 Claude answers; 144 queued.

**Score, or carry on where you stopped:**

```
python3 -B code/extensions/review/score_answers.py --resume \
    --collection "$COLLECTION" --round1-scores "$ROUND1" --out "$SCORES"
```

Add `--limit 12` to stop after twelve answers in one sitting.

**Lock what you have finished, at the cutoff:**

```
python3 -B code/extensions/review/score_answers.py --lock \
    --collection "$COLLECTION" --round1-scores "$ROUND1" --out "$SCORES"
```

## What each answer asks you

One answer per screen, under a scoring ID like `S017`. You see the scenario, the task, the policy excerpt,
the answer and the answer key. You do not see which model wrote it, and neither does anything printed to the
terminal.

For each criterion in turn:

1. **Judgment** — Correct, Incorrect, Incomplete or Cannot judge.
2. **Evidence** — a quoted phrase from the answer, or a one-line reason. Required, including for Correct.
3. **Failure class** — asked only after Incorrect or Incomplete. One or more codes from the fixed list.
   Codes go on the criterion that failed, not on the answer as a whole.

Then, once:

4. **Severity** — None, Minor, Major, Critical, Cannot judge.
5. **Acceptable** — the tool applies the primary-study rule. Major or Critical is never acceptable, so it records
   No without asking. An unresolved criterion or an unresolved severity is never Yes, so the tool records
   the answer `CANNOT_JUDGE` and asks you for the reason. Otherwise you choose Yes or No; the rule permits
   Yes, it does not require it.
6. **Reference or key concern** — if the answer key itself looks wrong, say so here instead of forcing the
   answer to agree with it. Blank if none.
7. **Other comments** — blank if none.

Type `q` at any prompt to stop. Everything already entered is saved. Type `s` at a criterion's judgment
prompt to skip the whole answer and come back to it later.

If an entry is inconsistent — Yes with a Critical severity, an Incorrect criterion with no failure class,
severity None with an error — the tool says what is wrong and asks for the answer again. It does not save
a record it would have to fix later.

## How long, and when to stop

The primary study's recorded completion times were a median of five minutes apart, mean ten. Those are gaps between
finishing one answer and finishing the next, not measured durations, but they are the best guide there is:
budget **five to fifteen minutes an answer**, and about two hours for a batch of twelve. Answers with four
criteria and a numeric case take longer than the three-criterion judgment cases.

Work in batches of twelve and stop when you stop being able to quote evidence for your own judgment. A
judgment you cannot evidence is a `Cannot judge`, and an answer you are too tired to evidence is one to skip
and return to, not one to push through.

Cases are scored in blocks of four, so a good place to stop is the end of a case block.

**The cutoff is 23:59 Asia/Manila on November 30, 2026**, whatever has been scored by then. Do not extend it
because the numbers look interesting, and do not stop early because they look settled. Unscored answers stay
in the denominator and are reported as unscored, the way the primary study reported its 48.

## Locking, and what to send back

At the cutoff — or when you finish, if that comes first:

1. Run `--lock`. Every finished record is marked locked and the file records the time. Locked records are
   not revised, by you or by anything else.
2. Run `--status` once more and keep the output; it is the coverage statement for the paper.

Then send back, for analysis:

* the locked score file (`$SCORES`), as it is — do not edit it by hand;
* the `--status` output from step 2;
* anything you wrote in a reference or key concern that you think needs a decision before analysis.

Send it the way you send the other private files. It is not committed to the repository, not published, and
not pasted into a chat. The aggregates derived from it are what appear in the paper.
