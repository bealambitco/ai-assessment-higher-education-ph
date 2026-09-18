# Execution commands for Codex

Run from the package directory using the bundled Python runtime. These are processing tools for Codex; the researcher need not run commands or maintain JSON manually. There are no provider calls, network collection or paid API operations.

1. `python3 code/test_experiment.py` — excluded offline fixtures; writes a dated code-hash test receipt.
2. `python3 code/experiment.py preflight` — lists remaining actual prerequisites. It does not freeze anything.
3. `python3 code/experiment.py freeze` — only after the researcher's freeze instruction and actual readiness. Refuses existing core output, missing confirmations or changed test code. Preserves a local timestamp and hashes. It is not independent preregistration.
4. The researcher generates and saves raw TXT replies. Codex fills receipt details from actual reports, never invented times/settings. The JSON response placeholders are not experimental observations.
5. `python3 code/experiment.py import` — preserves TXT bytes, creates structured derivatives, quarantines identity mismatches, and applies two pathways to each answer. Prints counts only. Reimport refuses changed raw bytes after a received response was registered.
6. `python3 code/reviewer_packets.py --populate` — creates new masked Word packets after the assigned outputs and provenance are present. It refuses to overwrite issued packets. Run document rendering/visual QA again before sending. Do not reveal identity keys or gate outcomes in packets.
7. `python3 code/timed_review.py` — starts a local-only interface at `http://127.0.0.1:8765`. The server records timestamps, explicit pauses, inspection overrides, decisions and separate final products. References are never served. Restart interruptions are flagged, not silently erased. Stop with Ctrl-C after completing or pausing the session.
8. `python3 code/scoring.py prepare` — refuses to expose formal content-scoring material before all 24 timed items are complete. Creates masked HTML reading copies and Markdown review forms, plus a JSON log. Codex synchronizes the researcher's saved judgments and checks every original criterion before score lock.
9. `python3 code/experiment.py lock_scores` — requires explicit scored/missing/cannot-judge status for every scheduled answer and coherent severity/acceptability labels. No gate join occurs until this lock.
10. `python3 code/analyze.py` — checks frozen-file integrity and locked score hash; computes primary rates, case-paired composition sensitivity, diagnostics and declared sensitivity summaries. Human source challenges/alternative labels and independent-review agreement still require actual returned judgments.
11. `python3 code/scoring.py repeat` — prepares the prespecified repeat set only after each initial scoring interval meets 24 hours, with earlier scores omitted. Partial eligible coverage can be prepared through an explicit dated operational amendment; do not change the interval silently.
12. `python3 code/scoring.py extract --docx reviewers/returned/FILE.docx --out reviewers/returned/FILE_extracted.json` — extracts Word control values verbatim and preserves original-file hash. Typing outside controls requires a separate transcription check; do not assume blank controls mean the reviewer wrote nothing.

All six reviewer assignments are fixed before outcomes. If someone cannot complete a packet, preserve missingness. A missing selected response is not replaced with a more convenient output after seeing performance. Any necessary assignment amendment is dated and justified without choosing by output quality.

Do not edit frozen code, source inputs, criteria or control profiles while retaining the same freeze record. A defect requires a preserved amendment/version and an assessment of affected outputs. Never alter reference labels silently after seeing outcomes.
