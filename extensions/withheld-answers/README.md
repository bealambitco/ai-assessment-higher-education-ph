# The answers the checks withheld

Sixteen of the 96 answers in the primary comparison never reached a user: the frozen checks blocked three
and routed thirteen to a person. Ten of those sixteen were never read by anyone. That is the gap this work
closes, and it is the reason the reading was ordered the way it was: a hold on an answer nobody read is
neither a catch nor a false alarm. Until the answer is read, every statement about what the checks bought is
conditional on it.

All sixteen have now been read against the same answer keys, criteria and severity definitions as the rest
of the study.

## What it found

**Sixteen of sixteen were acceptable.** No answer the checks withheld contained a serious error. Three were
blocked, thirteen routed; none was a catch.

| | Blocked | Routed | Total | Serious | Acceptable |
|---|---|---|---|---|---|
| Astra | 2 | 5 | 7 | 0 | 7 |
| Luna | 3 | 6 | 9 | 0 | 9 |
| **Both** | **5** | **11** | **16** | **0** | **16** |

**What fired, and why.** Eleven answers were routed because the model labelled its own next step as a
consequential action — recording a grade, granting an approval. Routing delays an answer rather than losing
it, and referral can be the right institutional step; but on these cases it fired only on answers that were
sound. Two answers were blocked because a correct number carried a unit label the arithmetic check did not
recognise. Three were blocked by the quotation check, on one case, for a reason worth stating precisely:

> Case W1-01 asks whether a syllabus states an adequate AI-use policy. The prompt supplies the syllabus in
> the scenario and the institution's guidance as the policy excerpt. Three answers quoted the syllabus —
> the document they were asked to assess — and the check searches the policy excerpt only, so it could not
> find those quotations and blocked the answers. A fourth answer on the same case quoted only the guidance
> and was released. All four were acceptable.

Across all 96 answers the models offered 419 quotations. Every one of them was present in what the model had
been given: 398 in the policy excerpt and 21 elsewhere in the prompt. Not one was absent
(`quotation_scope.json`, and D2-09 in [extension-deviations.md](../../docs/extension-deviations.md), which
records that this diagnostic was chosen after the blocks were known).

**The revised checks release two of the sixteen.** The unit-label blocks are recovered by the normalisation
in [revised-checks](../revised-checks/SPECIFICATION.md); the eleven routings and the three quotation blocks
are not, because neither revision changed what the routing check reads or where the quotation check looks.

## What it does not show

That the checks cannot catch an error. No serious error occurred in the answers read, so nothing here
measures containment. The two confirmed arithmetic errors observed anywhere in this study were released by
the same checks, not stopped by them ([revised-checks/FINDINGS.md](../revised-checks/FINDINGS.md)).

That the 36 answers still unread are sound. They stay in every denominator, and the bounding sensitivities
resolve them both ways. One consequence is worth stating: every unread answer was released by the checks, so
if any of them is seriously wrong, the checks did not contain it.

## Files

| File | What it holds |
|---|---|
| `answers_scored.csv` | One row per primary answer: case, configuration, repetition, check decision, whether it was read, and the outcome. No masked identifier |
| `scoring_results.json` | Coverage, the per-condition tables, the withheld-answer audit, per-workflow results, repetition consistency, comparison policies, reading effort and the clarified timing figures |

Aggregate tables for the whole study, recomputed over every answer read, are in
[results/aggregate](../../results/aggregate). The judgments themselves, which carry the model identity of
each answer, stay in the local package.

## How it was produced

```bash
python3 -B code/extensions/review/analyze_scoring.py \
    --join "<21_...>/analysis/locked_score_gate_join.json" \
    --scores "<extension package>/scores/extension_scores.json" \
    --checks "<extension package>/analysis/checks_v2_per_answer.csv" \
    --timing "<21_...>/analysis/supplement/supplement_results.json" \
    --out-private "<extension package>/analysis" --out-public extensions/withheld-answers \
    --compare "<21_...>/analysis/supplement/supplement_results_with_extension.json"
```

The same judgments are overlaid a second time, by a different route, in
`code/supplement/analyze_supplement.py --extension-scores`, which recomputes every condition table,
sensitivity and bound from the study's own files. `--compare` requires the two routes to agree before either
result is written. Neither route touches the locked score file: an answer the study scored is never revised,
and the overlay refuses to run if it is asked to.

Order, cutoff and the early stop: [scoring-plan.md](../../docs/scoring-plan.md). Failure classes:
[failure-classes.md](../../docs/failure-classes.md).
