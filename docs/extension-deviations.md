# Round-2 deviations

Every departure from [PROTOCOL.md](extension-protocol.md) or from a primary-study procedure, dated, with what was done and
what it costs the reader. Entries are appended, never edited.

## D2-01. Output token cap raised after the first collection run (20 September 2026)

**What happened.** The extension runner was written with a 4,000-token output cap. In the whole-document arm,
six of Gemini 3.1 Pro Preview's 24 replies stopped at the cap (`finish_reason: length`), and one of eight in
the rule-discovery arm did the same. A reply cut off mid-JSON cannot be parsed, so the parse step recorded
them as format failures.

**Why it matters.** Those are failures of my collection setting, not of the model's ability to return the
required format. Counting them as format failures would misstate a result the paper reports.

**What was done.** The runner gained `--redo-unusable`, which re-sends only runs whose saved reply is
missing, empty, truncated at the cap or unparseable, and the affected runs were re-sent with a 16,000-token
cap. The superseded reply is kept beside the new one as
`<run_id>_raw_superseded_<timestamp>.txt`, and both run records are retained, so the truncation is still
visible in the record rather than erased.

**How it is reported.** The results tables count the re-sent reply. The count of truncated first attempts is
reported alongside, and the paper states that the cap, not the model, produced them. No answer is replaced
because of what it said; only because it was cut off, empty or never arrived.

## D2-02. Kimi K3 replies with no visible content (20 September 2026)

**What happened.** In the whole-document arm, Kimi K3 returned replies with no visible content on several
cases, three attempts each, while still being billed. The billing export shows why: no call returned zero
completion tokens, and 14 of the 20 superseded Kimi calls spent their whole output allowance on reasoning
tokens, leaving nothing for the answer. It is exhaustion of the output allowance, not an empty response from
the provider. The primary study recorded the same behaviour on its longest document run (paper, Appendix H) and
described it as an empty reply; this entry is the better description.

**What was done.** The empty replies are recorded as such, with their cost, and the affected runs are
included in `--redo-unusable`. A case that stays empty after the redo is reported as no reply, never as a
failure of the checks and never as an answer.

**How it is reported.** Counts of empty replies, their cost, and the number of cases with no reply at all
are reported per configuration. Kimi's coverage is therefore stated as answers received over answers
scheduled, not as a rate over answers received.

## D2-03. Quotation check applied against the evidence actually supplied (20 September 2026)

**What happened.** The first parse of the whole-document and rule-discovery arms compared every quotation
with the short policy excerpt used in the primary comparison. In those arms the model is given an entire
document, so a passage quoted from elsewhere in that document was being counted as an unmatched quotation,
and answers were blocked for it.

**What was done.** The parser now applies the checks against the evidence the model was actually given: the
excerpt in the low-resource arm, the attached document or bundle in the other two. Both counts are kept per
run, so the effect of the change is visible. Re-parsing is free and used no new answers.

**How it is reported.** Quotation counts are reported against the evidence supplied and are not compared
across arms, because the retained document text and the transcribed excerpt differ in places.

## D2-04. One whole-document reply is cut off, not missing (20 September 2026)

Kimi K3's reply for one of the 24 whole-document cases (W1-01) arrived and was saved: 9,043 characters,
stopped at the raised 16,000-token cap, of which 13,912 tokens went to reasoning. A reply cut off mid-JSON
cannot be parsed, so it counts as a format failure, not as a missing answer.

An earlier version of the parse counted any unparseable reply as "not received", and the first write-up
repeated that as "no reply". Both are corrected: the tables now report replies received, replies cut off at
the cap, and replies parsed as three separate counts. Kimi K3's coverage is 24 replies of 24 scheduled, 1
cut off, 23 parsed.

The case can be re-sent with a larger output allowance; until it is, it is reported as a format failure with
its cause named.

## D2-05. The low-resource arm was run in two prompt conditions (21 September 2026)

**What happened.** The prompt written for the extension arms is about 77 percent similar to the one the
primary configurations received: the same case, excerpt and schema, but its own wording and an added
instruction to answer only from the evidence given. A format comparison with the primary configurations
would therefore have confounded the model with the wording.

**What was done.** The same 24 cases were sent again to the same three open-weight models with the study's
frozen prompt, byte for byte unchanged, at a cost of about two US cents. Nothing else differed, and no answer
from the first condition was discarded.

**How it is reported.** Both conditions are published side by side, with the counts for each. The difference
between them is reported as a result about prompt sensitivity, and no claim rests on one configuration's
count in one condition.

## D2-06. The four flagged timing items were clarified on the record (21 September 2026)

**What happened.** Four of the 24 timed items carried unexplained intervals and were left out of the main
timing figures: an unrecorded 53 minutes (T02), an unrecorded 12 minutes (T16), an unknown prior-exposure
answer (T04), and a pause whose start was never established (T24).

**What was done.** The researcher stated on the record what each interval was: away from the task for T02 and
T16, no prior exposure for T04, and, for T24, an interruption that began about a minute before the pause was
pressed. The statements are dated and recorded in [timing-clarifications.md](timing-clarifications.md).
Nothing in the timing file was edited.

**How it is reported.** T02, T16 and T04 rejoin the main figures, flagged as explained after the fact; T24
stays out of the point estimates and its correction time is reported as a range. Both the earlier figures,
which excluded all four, and the recomputed ones are published. Recalling an interval days later is weaker
evidence than a clock, and the paper says so wherever these items are used.

## D2-07. Reading of the answers stopped on 22 September 2026, before the cutoff (22 September 2026)

**What happened.** [scoring-plan.md](scoring-plan.md) fixed a cutoff of 30 November 2026 and an order in four
parts. Reading stopped on 22 September 2026 with 12 of the 144 scheduled answers read: all 10 of Part A, the
answers the frozen checks had withheld and nobody had ever read, and the 2 answers of Part B that complete
those three cases. Parts C and D were not begun.

**Why it matters.** The stop was decided after 12 answers had been read, so it is not a rule fixed in
advance, and a reader is entitled to ask whether what those answers showed is why the reading stopped. The
decision was the researcher's, on the ground that the remaining 132 answers were some fourteen hours of work
against a fixed publication date, and it was taken knowing that Part A had come out uniformly one way. That
cannot be unknown, and it is not presented as an independent stopping rule.

**What protects the result.** Part A was not a sample of convenience. It was defined before any answer was
read, in a published order, as exactly the answers the checks withheld and the study never scored, on the
argument that a hold on an answer nobody read is neither a catch nor a false alarm but an unpaid bill. That
part is now complete: every answer the checks withheld across the 96 has been read, in both configurations,
in all three workflow groups. The question the part was written to settle is settled, and no further reading
could change which answers the checks withheld.

**How it is reported.** Coverage is reported per part, so a reader can see that the part bearing on the
checks is complete while the rest is not. The 36 answers still unread stay in every denominator, and the
bounding sensitivities resolve them both ways. The paper reports the stop, its date and the reason, with the
order of events stated plainly: the answers were read, then the reading stopped.

## D2-08. One returned reviewer packet had lost its form controls (22 September 2026)

**What happened.** A third independent reviewer returned a Core packet in which the Word content controls
had been flattened into ordinary text, most likely by saving through another editor. The frozen extractor
reads controls by tag and found none, so the return was recorded as six responses with nothing in them.

**What was done.** A fallback reader (`code/supplement/reviewer_flat_extract.py`) recovers the answers from
the document text in the packet's own fixed layout, verbatim, and produces the same fields the controls
would have produced. It is required to reproduce the controls exactly on every return that still carries
them; on the three such returns it agrees on all 121 fields, with no differences
(`code/tests/test_reviewer_flat_extract.py`). Which reader was used is recorded per return and published in
`results/aggregate/reviewer_agreement_by_packet.csv`.

**How it is reported.** The return is analysed with every other return, and the extraction route is stated
rather than hidden. Nothing in the returned file was edited.

## D2-09. A post-hoc diagnostic on the quotation check (22 September 2026)

**What happened.** Reading the withheld answers showed that three acceptable answers were blocked by the
quotation check on the same case. The diagnostic that followed — searching for each unmatched quotation in
the whole prompt rather than in the policy excerpt alone — was chosen after that result was known.

**What was done.** `code/extensions/revised_checks/quotation_scope.py` reports, for all 96 primary answers,
how many quotations were in the excerpt, elsewhere in the prompt, or nowhere. It changes no decision and is
not part of the revised checks.

**How it is reported.** As a diagnosis of a known result, labelled as post-hoc wherever it appears, and never
as a validated improvement. A check revised in the light of the answers it got wrong has to be tested on
answers it has not seen before anything can be claimed for it.

## D2-10. The clarified timing figures were derived from the published aggregates (22 September 2026)

**What happened.** [timing-clarifications.md](timing-clarifications.md) described recomputing the timing
figures from the private file that maps each timed item to its condition.

**What was done.** The recomputation did not need that file. Each of the four flagged items is already
published against its own condition in the study's supplementary results, so including the three explained
items and excluding the fourth is a matter of reading the figures already computed for each condition. The
recomputation was done that way, and `recompute_timing.py` remains in the repository for anyone who wants to
re-derive the same figures from the item-level record.

**How it is reported.** Both sets of figures appear side by side in
`results/aggregate/timing_summary.csv` and in the paper: the earlier ones, which left out all four items,
and the clarified ones, which include the three explained items and still leave out the fourth.
