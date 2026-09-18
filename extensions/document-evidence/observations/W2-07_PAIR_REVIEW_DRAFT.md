# W2-07: paired observation (DRAFT for researcher confirmation)

Drafted by the AI assistant (Claude) on 18 September 2026 from the saved replies, run records and the automatic quotation check. Qualitative, not blind, not a score; the researcher confirms, modifies or rejects each row. Primary human scores are not affected.


## Gemini (google/gemini-3.1-pro-preview via ~google/gemini-pro-latest)

| Observation | Excerpt run | Full-text run |
|---|---|---|
| Run ID and attempt | D09 (attempt 1; RAW_SAVED) | D10 (attempt 1; RAW_SAVED) |
| Access evidence (platform, not only self-report) | Evidence pasted inline in the API request; 1276 input tokens; model self-report: read | Evidence pasted inline in the API request; 8637 input tokens; model self-report: read |
| Locators given | Source text; THE FOLLOWING SHALL BE CONSIDERED LATE/ABSENT; THE FOLLOWING SHALL BE CONSIDERED LATE/ABSENT; B. Approved Absence and Student Call Slip | Article 5: Attendance; Article 5: Attendance; Article 5: Attendance; Article 5: Attendance |
| Quotations match the source? | 6 of 6 quotations found word for word in the evidence file | 6 of 6 quotations found word for word in the evidence file |
| Proposed action | Refer the student's attendance record and medical certificate to the Guidance Counselor to determine if special consideration applies for the sickness-related absences before finalizing a failing grade. | Refer the student's attendance record and medical certificate to the Guidance Counselor to determine if special consideration applies for the illness, and suspend the issuance of a failing grade pending that final authority decision. |
| Generation latency | 19.2 s (no upload step) | 21.3 s (no upload step) |
| Attributable cost | US$0.0364 (OpenRouter-reported) | US$0.0525 (OpenRouter-reported) |

## Kimi (moonshotai/kimi-k3)

| Observation | Excerpt run | Full-text run |
|---|---|---|
| Run ID and attempt | D09 (attempt 1; RAW_SAVED) | D10 (attempt 1; RAW_SAVED) |
| Access evidence (platform, not only self-report) | Evidence pasted inline in the API request; 1318 input tokens; model self-report: read | Evidence pasted inline in the API request; 8487 input tokens; model self-report: read |
| Locators given | Opening attendance policy statement (preceding 'THE FOLLOWING SHALL BE CONSIDERED LATE/ABSENT'); THE FOLLOWING SHALL BE CONSIDERED LATE/ABSENT; THE FOLLOWING SHALL BE CONSIDERED LATE/ABSENT; B. Approved Absence and Student Call Slip | Article 5: Attendance — A. Policies and Guidelines; Article 5: Attendance — A. Policies and Guidelines (THE FOLLOWING SHALL BE CONSIDERED LATE/ABSENT); Article 5: Attendance — A. Policies and Guidelines (THE FOLLOWING SHALL BE CONSIDERED LATE/ABSENT); Article 5: Attendance — A. Policies and Guidelines (THE FOLLOWING SHALL BE CONSIDERED LATE/ABSENT) |
| Quotations match the source? | 7 of 7 quotations found word for word in the evidence file | 9 of 9 quotations found word for word in the evidence file |
| Proposed action | Record 12.0 countable absence hours (approximately 22.22%, exceeding the 20%/10.8-hour maximum) and the baseline failing-grade consequence, then refer the attendance record to the Guidance Counselor — who holds final authority — to determine whether special co | Confirm the count (12.0 countable hours = 22.22%, excluding the 3.0 AAAF-excused hours), then refer the record to the Guidance Counselor for an Article 5.C special-consideration determination; if special consideration is not granted, record the failing grade r |
| Generation latency | 328.4 s (no upload step) | 276.0 s (no upload step) |
| Attributable cost | US$0.0588 (OpenRouter-reported) | US$0.0673 (OpenRouter-reported) |

**Main observed difference (draft):** Same numbers and conclusion in both conditions for both models: 12.0 countable absence hours (10.5 illness + 1.5 from the third tardiness; the 3.0 AAAF hours excused) = 22.22% of 54 hours, over the 20% (10.8-hour) limit; baseline consequence is a failing grade; the Guidance Counselor decides special consideration. Full-text runs cited article-level provisions (Article 5.A, 5.C).

**Alternative explanations:** longer context changes location cues and length; single run per condition, so stochastic variation is possible; page markers exist only in the full-text extraction.

**Reference challenge:** none identified in drafting.

**Researcher final disposition:** Confirm / Modify / Unresolved — ______ (initials, date)
