# Useful extension: retained excerpt versus full document text

**Finish your primary 48 judgments first.** Then use the first-priority Gemini index below. There are 12 runs, not 48 new scores. Kimi's matching 12-run set is optional and already prepared.

1. Fill [Gemini setup](gemini/SETUP_AND_COLLECTION_NOTES.md): exact displayed model, app, reasoning, and search off. The planned label is Gemini Pro 3.1. Choose a time cutoff before running; protect time for paper/slides.
2. Open [Gemini collection index](gemini/COLLECTION_INDEX.md).
3. Open the first row's prompt TXT and copy all of it.
4. Open a fresh chat with that model. Turn browsing/search off; no external tools.
5. Attach exactly the row's linked TXT evidence file. Wait until the interface confirms upload. Do not attach the reference answer, original PDF or both evidence files.
6. Paste the full prompt once. Record send time in the run record or a batch note if timing is of interest.
7. When the answer finishes, save the full unchanged reply into the row's Raw TXT. Record finish time and any actual usage/cost shown. Leave the parsed JSON placeholder alone.
8. Continue in order, one fresh chat per row. After D06 you have three complete pairs, one per workflow. After D12 you have six complete pairs, two per workflow. Never regenerate just because an answer seems uninteresting or wrong.
9. If a file cannot be read, the response is truncated, or the interface rejects its size, save that attempt and note the problem. Do not silently shorten the full document or turn on browsing. We will record the access limitation.
10. Tell me which run IDs are saved, the configuration and exceptions. I will parse replies, check source support and draft the observations for your verification; I will not merge them into primary human scores.

## Optional Kimi, after Gemini and only if the paper is secure

[Optional Kimi collection index](kimi_optional/COLLECTION_INDEX.md). It uses exactly the same tasks, evidence and order. First confirm the actual available model/settings in [Kimi setup](kimi_optional/SETUP_AND_COLLECTION_NOTES.md). The user-proposed label Kimi K3 is not an independently verified backend ID. Each model has separate output folders. Do not mix their replies.

## What the result can say

A small source-verified qualitative comparison may show differences in evidence location, citation support and practical handling. It does not establish which model is generally best, a pure length effect, a hallucination rate, or a time/cost saving. “No material difference” is a valid observation. Full text may contain additional valid rules; inspect them before treating differences as mistakes.

[Protocol and limits](01_PROTOCOL_AND_LIMITS.md) · [Source manifest](protocol/SOURCE_MANIFEST.json) · [Observation forms](observations/) · [QA](qa/PREPARATION_QA.json)

If your intended primary repeat scoring remains unfinished, opening new answers may influence that repeat. Prefer finishing the repeat first if feasible; otherwise disclose the extra exposure and do not call it fully unexposed. Do not delay the paper just to complete this optional extension.
