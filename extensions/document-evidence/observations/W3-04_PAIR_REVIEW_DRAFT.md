# W3-04: paired observation (DRAFT for researcher confirmation)

Drafted by the AI assistant (Claude) on 18 September 2026 from the saved replies, run records and the automatic quotation check. Qualitative, not blind, not a score; the researcher confirms, modifies or rejects each row. Primary human scores are not affected.


## Gemini (google/gemini-3.1-pro-preview via ~google/gemini-pro-latest)

| Observation | Excerpt run | Full-text run |
|---|---|---|
| Run ID and attempt | D12 (attempt 1; RAW_SAVED) | D11 (attempt 1; RAW_SAVED) |
| Access evidence (platform, not only self-report) | Evidence pasted inline in the API request; 1144 input tokens; model self-report: read | Evidence pasted inline in the API request; 5979 input tokens; model self-report: read |
| Locators given | Section 5.4; Section 5.5 / Table 2 | Section 5.4, page 3; Section 5.5, Table 2, page 3; Section 5.5, Table 2, page 3 |
| Quotations match the source? | 2 of 2 quotations found word for word in the evidence file | 3 of 3 quotations found word for word in the evidence file |
| Proposed action | Record the calculated MGA of 1.375 and report the student's official final course grade as 1.25. | Record the MGA as 1.375 and assign the student a final course grade of 1.25. |
| Generation latency | 11.7 s (no upload step) | 12.3 s (no upload step) |
| Attributable cost | US$0.0217 (OpenRouter-reported) | US$0.0325 (OpenRouter-reported) |

## Kimi (moonshotai/kimi-k3)

| Observation | Excerpt run | Full-text run |
|---|---|---|
| Run ID and attempt | D12 (attempt 1; RAW_SAVED) | D11 (attempt 1; RAW_SAVED) |
| Access evidence (platform, not only self-report) | Evidence pasted inline in the API request; 1138 input tokens; model self-report: read | Evidence pasted inline in the API request; 6011 input tokens; model self-report: read |
| Locators given | Section 5.4; Section 5.5; Section 5.5, Table 2. MGA to Course Grade Conversion | Section 5.3 (PDF viewer page 3); Section 5.4 (PDF viewer page 3); Section 5.4, equation transcribed from the PDF image (PDF viewer page 3); Section 5.5 (PDF viewer page 3) |
| Quotations match the source? | 3 of 3 quotations found word for word in the evidence file | 7 of 7 quotations found word for word in the evidence file |
| Proposed action | The instructor records the computed MGA of 1.375 and reports the corresponding Course Grade of 1.25 for the 5-unit course, per the interval 1.10 < MGA ≤ 1.40 in Table 2; final posting remains subject to MCM's institutional grade-reporting authority. | The instructor computes and reports the final Course Grade of 1.25, submitting it in the BBL/Canvas FGC in Mapúa MCM Digital per the Section 7/Table 3 schedule (Module 2 of a 5-unit course: Sunday at 12 MN of Week 14). |
| Generation latency | 66.1 s (no upload step) | 312.1 s (no upload step) |
| Attributable cost | US$0.0125 (OpenRouter-reported) | US$0.0673 (OpenRouter-reported) |

**Main observed difference (draft):** Same result in both conditions for both models: MGA = 1.375, course grade 1.25 under the 1.10 < MGA ≤ 1.40 interval. Kimi's full-text run added the submission channel and deadline from Section 7/Table 3, a correct detail not in the excerpt; excerpt runs noted that final posting remains subject to institutional grade-reporting authority.

**Alternative explanations:** longer context changes location cues and length; single run per condition, so stochastic variation is possible; page markers exist only in the full-text extraction.

**Reference challenge:** none identified in drafting.

**Researcher final disposition:** Confirm / Modify / Unresolved — ______ (initials, date)
