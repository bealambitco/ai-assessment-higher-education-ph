# Timing: clarifications of the four flagged items

Recorded 21 September 2026. Four of the 24 timed items were flagged when the timing record was completed on
17 September 2026, and were left out of the main timing figures because the record could not say what the
unrecorded intervals were. The researcher has now stated, on the record, what happened in each. Nothing in
the original timing file is edited: the flags, the raw timestamps and the recorded clock values stay as they
were, and this file is the dated addition that resolves them.

Recalling an interval four days after the event is weaker evidence than a clock, and the paper says so
wherever these items are used.

| Item | What the record showed | What the researcher states | Effect |
|---|---|---|---|
| T02 | 8m33s to decide, 13m19s recorded correcting, but 66m33s of wall-clock passed: about 53 minutes unaccounted | She was away from the task during that interval and was not working on the answer | The recorded clocks measure the work. The item rejoins the main figures, flagged as clarified after the fact |
| T16 | 2m02s to decide, accepted with no corrections, 11m54s before saving | She was away from the task after deciding | The decision time stands. The item rejoins the main figures, flagged as clarified after the fact |
| T04 | Prior exposure recorded as UNKNOWN | She had not read that answer before the timed exercise | Exposure recorded as none. The item rejoins the main figures |
| T24 | A 1m12s pause during the correction, and a report at the time that about a further minute belonged to the interruption | The interruption began roughly a minute before she pressed Pause | The pause understates the interruption by about a minute. The item stays out of the point estimates and is reported as a range: its correction time is between the recorded value and that value less about 60 seconds |

## How this is reported

* The main timing figures are recomputed with T02, T16 and T04 included and T24 excluded, and are reported
  beside the earlier figures, which excluded all four. Both are published; neither is presented as a
  correction of the other, because they answer different questions: what the clocks recorded, and what the
  clocks recorded once the researcher stated what the gaps were.
* Every item that rejoins carries a flag saying its gap was explained after the fact, not at the time.
* T24 is reported as a range wherever its correction time appears.
* No recorded time is edited, added to or subtracted from. The recomputation changes which items are counted,
  not what any clock says.
* Timing remains exploratory. One researcher, who wrote the cases, timed all 24 items; a second observer's
  ten items are reported separately when that session takes place.

## The figures

Decision time is the clock that ran until the answer was accepted, edited or referred. Both sets are
published; neither supersedes the other.

| Condition | As published, all four items left out | With the explained items included |
|---|---|---|
| Astra, direct release | 98 s (55 to 263; 5) | 114 s (55 to 513; 6), T02 rejoins |
| Astra, under the checks | 158 s (91 to 355; 5) | 193 s (91 to 355; 6), T04 rejoins |
| Luna, direct release | 122 s (78 to 215; 5) | 122 s (78 to 215; 6), T16 rejoins |
| Luna, under the checks | 120 s (61 to 301; 5) | 120 s (61 to 301; 5), T24 stays out |

Items needing correction: 7 of 20 as published, 8 of 23 with the explained items included. T24's correction
time is reported as a range wherever it appears.

The full table, including correction times, is in
[results/aggregate/timing_summary.csv](../results/aggregate/timing_summary.csv).

## Recomputing

The recomputation did not need the private assignment file. Each flagged item is already published against
its own condition in the study's supplementary results, so including the three explained items and excluding
the fourth is a matter of reading the figures already computed for each condition; that is how the table
above was produced, and how `code/supplement/export_public_tables.py` writes it
([extension-deviations.md](extension-deviations.md), D2-10).

To re-derive the same figures from the item-level record instead:

```bash
python3 -B code/extensions/review/recompute_timing.py \
    --session "<21_EXPERIMENT_EXECUTION_PACKAGE>/timing/completion_2026-09-17/session_as_completed.json" \
    --assignment "<21_EXPERIMENT_EXECUTION_PACKAGE>/private/timing_assignment.json" \
    --out "<extension package>/analysis/timing_recomputed.json"
```

The assignment file maps each timed item to its configuration and pathway. It is private and stays local;
the script reads it, writes aggregates only, and prints no item-to-configuration mapping.
