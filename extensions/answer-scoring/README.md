# Independent review of the extension-arm answers

The primary comparison had its AI answers judged by independent reviewers, using Core and Optional
Word packets built by `21_EXPERIMENT_EXECUTION_PACKAGE/reviewers/split_v2`. The extension arms —
the same cases answered by smaller open-weight models, the same cases answered with the whole
governing document attached, and the eight cases answered with no passage selected at all — have
no such review. Nobody outside the study has read those answers. Every number reported for them so
far is coverage, format, quotation membership, release decision, time and cost, and
[findings-by-arm.md](../findings-by-arm.md) says so explicitly.

This folder is the arm that closes that gap. It describes the reviewer packets built by
[`code/extensions/review/extension_reviewer_packets.py`](../../code/extensions/review/extension_reviewer_packets.py)
and read back by
[`code/extensions/review/extension_reviewer_intake.py`](../../code/extensions/review/extension_reviewer_intake.py).

The generated `.docx` packets are **not** in this repository. They quote model answers and
institutional policy text, so they live with the collected answers in the local extension package,
under `30_ROUND2_EXTENSION/reviewer-packets/`.

## What a reviewer is asked to do

Exactly what the primary-study reviewers were asked to do, and in the same document design: read a
scenario, the task, the policy evidence and one AI response; then judge each criterion of the
answer key as **Correct / Incorrect / Incomplete / Cannot judge**, choose one overall severity from
**None / Minor / Major / Critical / Cannot judge**, record any source or reference concern, and
write a comment. Four packet options exist, A to D, each a Core file of six answers and an Optional
file of four.

Two things are new, and both exist because of the evidence problem described below: a page that
explains what evidence each AI was given, and, for the answers that were given whole documents, one
extra question per answer asking whether the evidence printed in the packet was enough to judge it.

## The selection rule, fixed before anything was generated

The rule is in the docstring of `allocate()` and is enforced by `check()`, which refuses to write a
packet that breaks it. In full:

1. **Eligible answers.** An answer is eligible when its case is one of the twelve the primary study
   scored (W1-02, W1-03, W1-05, W1-06, W2-03, W2-05, W2-07, W2-08, W3-02, W3-04, W3-05, W3-08), the
   reply parsed into one answer object, and that object is valid against the required schema. The
   case restriction is the point of the arm: a reviewer's judgment can then be set beside a
   judgment the researcher has already made on the same case. Of the 136 answers the three arms'
   per-run tables list, 65 are eligible; 66 fall outside the twelve cases and 5 failed the
   schema.
2. **Shape.** Ten answers per reviewer: a Core file of six and an Optional file of four, as in
   round one.
3. **Anchors.** Two answers appear in the Core file of *every* packet, so reviewer-to-reviewer
   agreement can be measured. One of them was answered from the supplied excerpt and one from a
   whole document, so agreement is measured in both evidence conditions rather than only the easy
   one. Anchors are drawn from cases the rule-discovery arm did not cover, because that arm has
   only nine eligible answers and an anchor would otherwise take a case out of its reach.
4. **Arm coverage.** Every packet covers all three arms: four answers from each of the two larger
   arms and two from the smallest, counting the anchors.
5. **Configuration balance.** Within a packet, no configuration supplies more than two of the ten
   answers, and no model supplies more than three across arms. The packet never names a
   configuration, an arm or a model.
6. **Core is self-sufficient.** Core carries both anchors, both of the smallest arm's answers and
   one from each larger arm, so a reviewer who completes only the Core file has still seen all
   three evidence conditions.
7. **No repeats.** No answer appears twice in a packet, no case appears twice in a packet, and no
   answer is used in two packets except the two anchors. Four packets therefore cover 34 distinct
   answers.

The selection is deterministic given the seed. The private crosswalk from masked response id to
arm, configuration and run is written beside the packets as `assignments_private.json` and is not
published. Responses carry masked ids (`E001`…) drawn in a seeded shuffle of the whole eligible
pool, so neighbouring ids say nothing about which configuration produced them.

## The whole-document evidence decision

**The problem.** In the whole-document and rule-discovery arms the model was given entire policy
documents, not the short excerpt the primary study supplied. A quotation may therefore come
legitimately from a part of the document the excerpt never showed. A reviewer handed only the
excerpt would mark such a quotation unsupported, and would be wrong. But a packet cannot carry the
document. Among the answers selected here a single attached document runs from about 6,000 to
about 369,000 characters, and a rule-discovery bundle of two or three documents from about 54,000
to about 742,000; and the institutions' register entries allow the study to cite and link these
documents, not to redistribute them in full.

**What was decided.** For every answer in those two conditions the packet prints:

- a plain statement, at the top of the item, of what the AI was given, and that the document itself
  is not reproduced and why;
- the identity of each attached document — file name, character count and SHA-256 — with the case's
  public source title, link and retrieval date, so the reviewer can open the original if they wish;
- the study's own excerpt, labelled as context and explicitly **not** as the evidence this AI was
  given;
- and, beside every quotation the answer offers, the passage **located in the document text the AI
  was actually given**, printed with a bounded window of the surrounding text. Matching ignores
  whitespace only, so a located passage is present word for word. A quotation that cannot be found
  is printed as *not located*, with no further inference attached to it.

There is a ceiling on that last part, because the windows accumulate. A packet may print
surrounding context from any one document up to 15 percent of that document or 6,000 characters,
whichever is smaller. Past the ceiling the located passage is still printed — it is the model's own
quotation, already on the page as a citation, so it is not new material — but the text around it is
replaced by a line saying the packet has shown as much of that document as the study may reproduce.
In the four packets as generated, that ceiling binds five times out of 94 printings.

**What the reviewer is asked to judge**, stated on the reviewer's own page and repeated on every
affected item:

- Whether each criterion is met, using the reference summary, the criteria, the excerpt and the
  located passages.
- Whether a located quotation, read in its printed context, supports what the answer uses it for.
- For the rule-discovery condition, whether the answer used a document that plausibly governs the
  case.

**What the reviewer is asked not to judge:** whether a better or more authoritative passage sits
somewhere else in the document that the answer missed. The packet cannot show the rest of the
document, so that question cannot be answered fairly from it. Reviewers are told to select
*Cannot judge* where a criterion turns on it and to say why.

**And the limitation is measured, not hidden.** Each of those answers carries one extra field,
"Was the evidence printed here enough to judge this answer?", with *Yes*, *No, some criteria needed
the full document*, and *Cannot tell*. A run of *No* is a real result about the design of this
review, and the intake script counts it.

Across the 21 document-condition answers selected, the answers offer 83 quotations; 79 are located
and 4 are not. Measured independently from the generated files rather than from the builder — by
checking which 50-character stretches of each retained document appear anywhere in a packet — the
largest share of any one document that a single reviewer packet reproduces is 16.3 percent, and
that figure includes the study's own excerpt, which comes from the same document. Most documents
sit between 3 and 9 percent. Nothing is reproduced continuously.

## What this arm can and cannot establish

It can show whether independent readers, given the same keys and criteria the study uses, judge
these answers acceptable; where they disagree with each other; where they challenge the answer key
rather than the answer; and, from the anchors, how far two readers of the same answer agree at all.
For the whole-document conditions it can show whether the located-passage evidence was sufficient.

It cannot establish correctness in any final sense. Four reviewers and thirty-four answers is a
small, purposive sample restricted to twelve cases, not a representative one; the 5 schema-invalid
answers are excluded, so the pool is slightly cleaner than the arms as a whole; and the two anchors
support a limited comparison between reviewers, not a reliability estimate for the corpus. It
cannot compare arms against each other, because the arms differ in more than one way at a time and
each packet holds only a few answers from each. And it cannot say anything about the cases outside
the scored twelve.

## How returns are handled

Returned files are kept unread until the researcher's own scoring of these answers is locked, the
same rule the primary study used. Reading a reviewer's judgment first would contaminate the
researcher's, and the comparison between them is the reason for collecting both.

When the scoring is locked:

```
python3 -B code/extensions/review/extension_reviewer_intake.py \
    --packets <returned .docx files or a directory> --out <directory>
```

writes `extension_review_responses.csv`, one row per response and criterion, and
`extension_review_disagreements.csv`, one row per point where the returns differ or a response was
challenged. Answers are read from the Word content controls by tag, with the typed-beside-the-field
fallback the packets tell reviewers to use. Nothing is adjudicated or rewritten; blanks stay blank.
**Reviewer names are never written into the CSV** — packets are identified by file name and
responses by masked id — and no model is named anywhere in the output.

`REVIEWER_DISPATCH_LOG.csv`, beside the packets, carries the same columns as the round-one log and
is left empty for the researcher to fill in as packets are sent and returned.

## Rebuilding the packets

```
python3 -B code/extensions/review/extension_reviewer_packets.py \
    --packets A,B,C,D --out <the extension package>/reviewer-packets
```

The build is deterministic: the same inputs and seed produce byte-identical files and the same
SHA-256. The design layer is not reimplemented — `ExtensionBuilder` subclasses the `Builder` in
[`key_review_packets.py`](../../code/extensions/review/key_review_packets.py), which already carries
the primary-study packet design. QA evidence for the generated set is in
`reviewer-packets/qa/QA_REPORT.md` beside the packets.

Send only the `.docx` files. `assignments_private.json`, `packet_manifest.json`, the dispatch log
and the QA folder are working files and must not go to a reviewer.
