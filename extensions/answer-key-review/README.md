# Answer-key review

**Status, 21 September 2026: prepared and held.** The packets, instructions and intake are ready, and the
four-packet split covers all 24 cases, but they have not been sent. Independent reviewer effort in this round
goes to scoring model answers instead. Until these are sent and returned, the study continues to state, as it
does now, that the answer keys were drafted with AI assistance and settled by one person, with no independent
expert validation.

Extension ("v2") work, prepared September 20, 2026. Nothing here has been sent or returned yet.

## Why this exists

The 24 cases in [`benchmark/cases/`](../../benchmark/cases/) each have an answer key in
[`benchmark/answer-keys/`](../../benchmark/answer-keys/): a reference answer and a numbered list of
scoring criteria, each with a locator pointing into the quoted rule. The 24 keys carry 90 criteria.

The keys were drafted with AI assistance, revised by the researcher against the sources, and challenged by a
supplementary AI audit. One person settled every disagreement. Independent expert review of the keys was
planned and did not happen before the freeze
([`docs/method.md`](../../docs/method.md), [`docs/deviations.md`](../../docs/deviations.md) D12, D25).
Every correctness number in the primary study rests on those keys. This is the study's largest stated limitation.

This folder prepares the review that was missed. Two independent Philippine higher-education experts read
the keys and say, criterion by criterion, whether each one states the quoted rule correctly and whether its
locator points at text that supports it.

## What this can and cannot establish

It can establish:

- Whether each criterion is a correct reading of the rule that was quoted to the model.
- Whether each locator points at text that supports its criterion.
- Whether a registrar or faculty member would accept each reference answer under the quoted rule.
- Where two independent readers disagree about a key, and on what.

It cannot establish:

- That any AI answer was scored correctly. Reviewers never see a model answer, a model name or a score.
  A validated key does not validate a scoring decision made against it.
- That the keys are right about the current rule. Reviewers judge the key against the excerpt the study
  supplied. A rule that has since changed is recorded as a concern, not as a key error.
- That the keys are representative of Philippine higher education. Two reviewers are two readings.
- Inter-rater reliability in any strong sense. Two returns support a description of agreement and a list of
  disputed criteria. They do not support a reliability claim across the benchmark.

Reviewers are chosen for their background, not sampled. This is purposive allocation, the same limit that
applies to the primary-study response reviewers.

## Generating packets

Python 3.12, plus `python-docx` from [`code/requirements.txt`](../../code/requirements.txt). No network
calls. Run from the repository root.

```bash
# named cases
python3 -B code/extensions/review/key_review_packets.py \
    --cases W1-01,W2-03,W3-01 --out ../key-review-out --packet-label A,B

# a reproducible sample, drawn with a fixed seed and printed in the run summary
python3 -B code/extensions/review/key_review_packets.py \
    --sample 6 --out ../key-review-out --packet-label A,B

# every case
python3 -B code/extensions/review/key_review_packets.py \
    --all --out ../key-review-out --packet-label A,B
```

One `.docx` is written per label, so `--packet-label A,B` gives two reviewers the same cases independently.
Each packet opens with a cover and a short guide, then gives each case two pages-worth of sections: a
reading section and a review form.

The reading section holds the case id and workflow group, the scenario, the task, the supplied policy
excerpt reproduced verbatim in a shaded inset, the full answer key, and the source document's title, link
and SHA-256 from [`literature/institutional-sources.csv`](../../literature/institutional-sources.csv)
together with the frozen case-file hash from
[`benchmark/protocol/source_trace.json`](../../benchmark/protocol/source_trace.json). The review form
that follows carries the numbered criteria with their locators and the yellow answer fields.

The packets contain no model answers, no model names, no scores and no reviewer names. The reviewer types
their own name on the cover.

### Packet design

The packets use the same document design as the primary-study reviewer packets that were sent to the independent
scorers, so a reviewer who has seen one of those recognises this one. Concretely:

- A4, 0.68 in side margins, Arial 11 pt body on a dark ink colour, headings at 23 / 16 / 12 / 10.5 pt.
- A white-on-blue running band at the top of every page. The cover band names the study and the packet; each
  case's band names the packet, the case position and the case id.
- Pale blue section labels ("Read the scenario", "Your judgments") instead of unshaded sub-headings.
- Policy excerpts and the reference answer set in Georgia 10 pt in a shaded inset; the excerpt inset also
  carries a left rule. Grading tables inside an excerpt are rendered as real tables, without changing the
  stored wording.
- Centred tables with a repeating blue header row, banded rows and hairline borders.
- Each case is its own Word section with its own running header, and each case heading carries a `case_N`
  bookmark that the "Jump to a case" links on the cover point to.
- Answers are yellow Word content controls sitting inline after a bold question, one per line. The cover
  collects the reviewer's name, role, institution, date, approximate minutes, free notes and acknowledgement
  consent. Dropdowns hold the listed options; comment boxes are multi-line text.

If the dropdowns do not work in a reviewer's copy of Word, the packet tells them to type the option beside
the field, and intake reads what they typed.

Output is deterministic. The same cases and labels produce byte-identical files, and the run prints the
SHA-256 of each one. Record those hashes before sending, so a returned file can be compared with what was
issued. Two stored excerpts (W3-02, W3-05) hold a page-break character from the original document; it is
rendered as a line break and the packet says so on the page.

**Generated `.docx` files are not kept in this repository.** Write them outside the repo tree, or to a
`private/` folder, and publish only the hashes and the aggregate results.

## Returning and intake

Reviewers save their own copy, fill the yellow fields in Word and send the file back. Put the returned files
in one directory, then:

```bash
python3 -B code/extensions/review/key_review_intake.py \
    --packets ../key-review-returned --out ../key-review-returned/intake
```

That writes two files and prints a summary:

| File | Contents |
|---|---|
| `key_review_responses.csv` | One row per judgment: packet, case, criterion, judgment, locator judgment, comment. Overall acceptance and rule-version concerns are rows with `criterion` set to `overall` and `rule_version_concern`. |
| `key_review_disagreements.csv` | One row per point where returns differ, where a criterion was challenged, or where a locator was doubted. |

The intake script reads the answer fields with `python-docx`, keyed on each field's tag
(`<case>_C<n>_JUDGMENT`, `_LOCATOR`, `_COMMENT`, and `<case>_ACCEPT`, `_ACCEPT_WHY`, `_RULE_VERSION`) rather
than on the wording printed beside them, so the packet layout can change without breaking intake. If a
reviewer's Word could not drive a dropdown and they typed the option beside the field instead, the typed
text in the same paragraph is read. Cover fields are recognised and deliberately skipped.

It does not adjudicate, correct or fill anything. A blank field stays blank and is counted as not answered.
A missing file, an unreadable file, a packet with no answer fields, an unexpected field tag, and an answer
typed in wording that is not on the list are each reported as a named problem and do not stop the run. An
answer that is not one of the listed options is kept verbatim in the CSV and flagged.

Each packet is identified by its file name. The reviewer's typed name is **not** copied into the CSV.

## How disagreements will be handled and reported

1. Every challenged criterion is recorded. A criterion marked anything other than "Correct", a locator
   marked anything other than "Yes", an overall answer other than "Yes", and every free-text comment go into
   the CSV and into the report, whether or not the key changes.
2. The two returns are preserved as returned, before any discussion between reviewers or with the
   researcher. The original files are kept; the CSV is derived from them.
3. Disagreement between the two reviewers is reported as a count and a list, not resolved by the researcher
   picking a side. Where they disagree, both readings are stated.
4. **No silent edits.** A key is changed only by an explicit dated note in
   [`docs/deviations.md`](../../docs/deviations.md) that names the case, the criterion, the reviewer
   concern, the change and the reason. A key changed after the fact is a new version with its own hash; the
   frozen primary-study files are not edited, so the freeze record stays verifiable.
5. Any change to a key that would move a primary-study score is reported as a sensitivity, separately from the
   locked primary-study results. Round-1 scores are not rewritten in place.
6. Reviewers who consent are named in the acknowledgements. Consent is recorded on the packet cover. No name
   and no identifiable comment is published without it.

## Files

| Path | What it is |
|---|---|
| [`REVIEWER_INSTRUCTIONS.md`](REVIEWER_INSTRUCTIONS.md) | The text sent to reviewers |
| [`../../code/extensions/review/key_review_packets.py`](../../code/extensions/review/key_review_packets.py) | Builds the packets |
| [`../../code/extensions/review/key_review_intake.py`](../../code/extensions/review/key_review_intake.py) | Reads the returns, writes the CSVs |

## Status

No packet has been generated for sending, no reviewer has been approached, and no return exists. When that
changes, record the date, the case list, the packet hashes and the actual coverage here, and add a dated
entry to [`docs/deviations.md`](../../docs/deviations.md).
