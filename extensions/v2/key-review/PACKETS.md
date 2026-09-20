# The key-review packets: who gets what

Four packets, A to D, cover all 24 cases with no overlap: six cases each, split into a Core file of three
cases and an Optional file of three more, the way round 1 split its response-scoring packets. Send Core
first; offer Optional only if the reviewer has time. A Core file runs to about 20 pages, a full six-case
packet to about 38.

| Packet | Core cases | Optional cases | Workflow groups | Institutions |
|---|---|---|---|---|
| A | W1-01, W2-01, W3-01 | W1-05, W2-05, W3-05 | 2 × W1, 2 × W2, 2 × W3 | Ateneo de Manila, St. Paul Surigao, Mapúa MCM, UP Diliman, Southern Philippines Foundation |
| B | W1-02, W2-02, W3-02 | W1-06, W2-06, W3-06 | 2 × W1, 2 × W2, 2 × W3 | Ateneo de Manila, St. Paul Surigao, Southern Philippines Foundation, UP Diliman, De La Salle |
| C | W1-03, W2-03, W3-03 | W1-07, W2-07, W3-07 | 2 × W1, 2 × W2, 2 × W3 | Cebu Normal, De La Salle, Pateros Technological College, Mapúa MCM |
| D | W1-04, W2-04, W3-04 | W1-08, W2-08, W3-08 | 2 × W1, 2 × W2, 2 × W3 | UP Diliman, Southeastern Philippines, Mapúa MCM, St. Paul Surigao |

The split is deterministic: cases are dealt round-robin across the four packets within each workflow group,
lowest case number first. Every packet therefore carries two cases from each workflow group, and the numeric
cases are spread: W3-01 in A, W3-02 in B, W2-07 in C, W3-04 and W3-08 in D.

## Choosing reviewers

Any Philippine higher-education faculty member, registrar or academic-affairs officer can review any packet;
the cases are policy-reading tasks, not technical ones. If a reviewer's background fits a group, use it:

| Background | Packet that fits best |
|---|---|
| Syllabus, course policy, academic integrity | B, then A |
| Records, grades, INC and completion rules | D, then C |
| Examinations, special exams, attendance | C, then A |
| Grading computation and weights | D, then B |

Two reviewers cover half the benchmark; four cover all of it. Coverage is reported as it turns out: a packet
that is never returned is reported as not reviewed, never filled in from another packet.

## Sending

1. Send the Core file with [REVIEWER_INSTRUCTIONS.md](REVIEWER_INSTRUCTIONS.md) in the body of the message.
2. Say that partial completion is welcome and that there is no stopwatch.
3. Offer the Optional file only if they ask for more, or after Core comes back.
4. Record who received which packet and when, and keep returns unread until they are all in, exactly as in
   round 1.
5. Ask about acknowledgment permission separately, not inside the packet. A name appears in the paper only
   with recorded permission.

## After they come back

```bash
python3 -B code/extensions/round2/key_review_intake.py --packets <folder of returned files> --out <folder>/intake
```

The intake writes one row per criterion judgment, plus a list of every challenged criterion. Nothing is
changed in an answer key without a dated note, and any key that does change triggers a re-score of the
affected answers under both the old and the new key, with both results reported.
