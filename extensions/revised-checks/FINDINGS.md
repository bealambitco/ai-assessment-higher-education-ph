# Arm A: what the revised checks change

Run on September 20, 2026 over answers collected in the primary study. No new answers, no paid calls. The rules were
fixed in [SPECIFICATION.md](SPECIFICATION.md) and hashed in [the extension protocol](../../docs/extension-protocol.md) before
this run; the reading below is the one stated in the specification beforehand. Human scores are the primary-study
scores, unchanged.

Command and run record: [run-record.json](run-record.json). Per-answer tables stay local
and unpublished; the CSVs here are aggregates.

## Decisions, all 192 answers re-run

| Configuration | v1 released / routed / blocked | v2 released / routed / blocked |
|---|---|---|
| Astra (OpenAI Codex) | 41 / 5 / 2 | 41 / 5 / 2 |
| Luna (OpenAI Codex) | 39 / 6 / 3 | 41 / 6 / 1 |
| Fable 5.1 (Claude) | 38 / 3 / 7 | 42 / 4 / 2 |
| Haiku 4.5 (Claude) | 37 / 1 / 10 | 40 / 1 / 7 |

Re-running the frozen rules reproduced every decision recorded at the September 18 score lock, 96 of 96, so
the comparison is like for like.

## Effect on the answers with human scores

Sixty answers have now been read, including every answer the checks withheld
([withheld-answers](../withheld-answers/README.md)). The table below is over those sixty.

| Rules | Acceptable answers | Withheld under v1 | Withheld under v2 | Released by the new rules | Withheld by the new rules |
|---|---|---|---|---|---|
| v2 | 60 | 16 | 14 | 2 | 0 |
| v2b | 60 | 16 | 14 | 2 | 0 |

| Rules | Confirmed errors | Withheld under v1 | Withheld under v2 |
|---|---|---|---|
| v2 | 2 | 0 | 2 |
| v2b | 2 | 0 | 2 |

**Pre-specified reading: an improvement on this evidence.** Checks v2 recovered at least one acceptable
answer that v1 withheld (two), contained at least one confirmed error that v1 released (both), and
introduced no new withholding of an answer scored acceptable. The reading is unchanged now that every
withheld answer has been read, and the size of what is left undone is clearer: fourteen of the sixteen
answers withheld from a user are still withheld under the revised rules, and all sixteen were sound.

## What actually moved, and why

* **The two unit-label blocks are gone.** Luna's correct attendance answer (W2-07, 12 class hours, 22.22
  percent, 10.8 threshold hours) and its correct module-conversion answer (W3-04, course grade 1.25 in
  "course-grade points") are released under v2. R1 was written for exactly this.
* **Both confirmed Haiku errors are now contained.** In W3-02, Haiku reported 85 percent as `course_grade`
  while `weighted_score`, correctly 84.6, was absent. Several percent-denominated quantities were present,
  so no single candidate could be matched, and R2b failed closed. Under v2b the same answers are blocked
  through prose extraction instead. Either way, an error v1 released is withheld.
* **The routed answers did not move,** as intended: routing a declared grade or approval to a person is a
  policy choice, not a defect, and v2 leaves it alone.
* **Typographic normalization mattered, contrary to the specification's expectation.** R3 was expected to
  recover nothing. It recovered several blocked Claude answers where the model wrote straight quotation
  marks and the source document uses curly ones. The specification's prediction was wrong and is left as
  written; this paragraph records the outcome.
* **Fail-closed cost nothing here, but only because the numeric cases were answered in the expected form.**
  Every acceptable answer in the five numeric cases reported the expected quantity by name or with one
  unit-compatible alternative. A model that omits the quantity entirely would now be blocked. On a wider
  sample this rule would show a cost; on this sample it did not.

## Unscored answers

Of the 130 answers in the four configurations that nobody has read, v1 withheld 21 and v2 withholds 12; nine
that v1 blocked are released under v2, mostly on the typographic rule. Because nobody has read them, they
are counted neither as recovered help nor as contained error. They are all in the Claude configurations:
every answer the checks withheld in the primary comparison has now been read.

## What this does not show

* Nothing here shows how a model would answer if it knew the checks were more tolerant; the answers were
  collected under v1 conditions.
* Two confirmed errors is a thin basis for the containment claim. The paper should continue to report the
  count, not a rate.
* Neither revision touches the two causes that account for fourteen of the sixteen unnecessary holds: what
  the routing check reads, which is the model's own label, and where the quotation check looks, which is one
  field of the prompt rather than everything the model was given. Those causes are described in
  [withheld-answers](../withheld-answers/README.md); the second was identified after the blocks were known,
  and a check revised in its light would have to be tested on answers it has not seen.
* The rules were written after the author had seen the v1 results. Each rule follows the recommendation
  published in Section 6.3 on September 18, before this arm existed, and the hashes above fix what was
  claimed before the data was touched, but the risk of hindsight cannot be removed by assertion.
