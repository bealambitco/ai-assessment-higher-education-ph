# How to score the remaining answers

Arm B of [the extension protocol](extension-protocol.md). You are scoring 144 answers: the 48 primary answers the primary study left
unscored, then the 96 Claude answers. Everything runs on your machine. Nothing is sent anywhere and nothing
costs money.

There are two ways to do it, and they are the same instrument: **a browser page on this computer**
(`bash run.sh score-web`, described under [Scoring in a browser](#scoring-in-a-browser)) or the terminal
prompts (`bash run.sh score`). Same order, same questions, same rules, same score file; you can switch
between them whenever you like, even part-way through the queue. The browser page is easier for long
quotations and it is the only one that lets you go back and edit an answer you have already scored, so it
is the one to use unless you have a reason not to.

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

## The clock

Scoring uses the same instrument as the timed exercise. A clock starts when an answer appears and stops when
you save it. **Press Pause on the page, or enter `p` at any terminal prompt**; you will be asked why, and that interval is excluded
from the clean figure and kept in the record with your reason. If more than five minutes pass between
entries without a pause, the gap is recorded and flagged, never subtracted. Each sitting also records when
you opened and closed the tool.

What this measures is how long scoring took, under the same rules as the timed exercise. It is not the
verification-burden measure: scoring against an answer key is a different task from deciding whether to
accept an answer, and the paper's verification times come from the timed exercise alone.

## Pasting a quotation

In the browser every box is an ordinary text box: paste a quotation of any length, line breaks and all, and
it is saved exactly as you pasted it.

In the terminal, evidence, reasons and comments accept several lines. Paste as much as you like, then press
Enter on an empty line to finish. A single line still works the same way: type it, then Enter, then Enter.
The terminal joins the lines into one continuous text; the browser keeps them.

## Scoring in a browser

```
bash run.sh score-web
```

It prints an address like `http://127.0.0.1:8767`. Open that in any browser **on this computer** and leave
the terminal window alone; Ctrl-C there stops the tool. Nothing is served to the network, no page loads
anything from the internet, and the score file is the same file the terminal tool writes. Add a port number
(`bash run.sh score-web 8790`) if something else is already using 8767.

The first page is progress: how many answers each part holds, how many are scored, how many are left, the
order signature and where the score file is. **All answers** lists every answer with its status. **Score the
next answer** opens the next one in the queue.

An answer's page shows, in this order: which answer it is and which part, the case, the scenario, the task,
the policy excerpt, the answer under review in a box of its own, then the answer key with its criteria, its
accepted variants and its "not this" examples. Below that is the form: for each criterion a judgment, an
evidence box, a reason box and the failure-class checkboxes; then severity, the acceptability rule and your
Yes/No, a reference-concern box and a comments box. The buttons are **Save and next**, **Skip for now**,
**Pause** and **Finish this sitting**.

The clock is shown at the top of every answer page: when it started, how long it has counted, any paused
time, and any gap it has flagged. Pause asks for a reason and refuses to pause without one. Refreshing the
page does not restart it.

If something is inconsistent, the page comes back with the problem named at the top **and everything you
typed still in the boxes**. Nothing is written to the score file until the record is one the tool would
accept, and nothing you typed is ever thrown away by a refusal.

## If you leave an answer part-finished

Whatever you have typed is kept as a draft on that answer, saved as soon as you press any button. If you
press Finish while an answer has entries, the page refuses once and tells you: press Save and next to record
it, or press Finish again to end the sitting and keep the entries as a draft. Reopening the answer puts them
back in the boxes, with a note saying when they were left.

## Changing an answer you have already scored

Two ways, both on the **All answers** page, and both keep the version they replace in that answer's
`supersedes` list with the time it was replaced. Nothing is overwritten silently, and a locked record is
refused either way.

* **Edit** re-opens the answer with every box already filled with what you saved, so you can fix one
  criterion's evidence without retyping the rest. The time first measured for that answer is left exactly
  as it was recorded; the time you spend on the revision is kept separately, in an `edits` list, so the
  scoring-time figures stay honest.
* **Score again from blank** empties the form and starts the answer over. This is the same thing as
  `bash run.sh rescore S001` in the terminal.

## Scoring an answer again, from the terminal

If an entry went in wrong and you are not in the browser, re-open that one answer:

```
bash run.sh rescore S001
```

The earlier record is kept inside the answer's `supersedes` list with the time it was replaced, so nothing is
lost and the change is visible. A locked record is refused.

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

**Score in the browser (the same queue and the same file):**

```
python3 -B code/extensions/review/score_answers_web.py \
    --collection "$COLLECTION" --round1-scores "$ROUND1" --out "$SCORES"
```

**Check the browser tool works, on invented data:**

```
python3 -B code/extensions/review/score_answers_web.py --self-test
```

**Score, or carry on where you stopped, in the terminal:**

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

The same questions in both tools. One answer per screen, under a scoring ID like `S017`. You see the
scenario, the task, the policy excerpt, the answer and the answer key. You do not see which model wrote it,
and neither does anything printed to the terminal or drawn on the page.

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

In the terminal, type `q` at any prompt to stop; everything already entered is saved. Type `s` at a
criterion's judgment prompt to skip the whole answer and come back to it later. In the browser those are the
**Finish this sitting** and **Skip for now** buttons.

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

1. Run `--lock` in the terminal. There is no lock button on the page: locking happens once, deliberately,
   at the cutoff. Every finished record is marked locked and the file records the time. Locked records are
   not revised, by you or by anything else.
2. Run `--status` once more and keep the output; it is the coverage statement for the paper.

Then send back, for analysis:

* the locked score file (`$SCORES`), as it is — do not edit it by hand;
* the `--status` output from step 2;
* anything you wrote in a reference or key concern that you think needs a decision before analysis.

Send it the way you send the other private files. It is not committed to the repository, not published, and
not pasted into a chat. The aggregates derived from it are what appear in the paper.
