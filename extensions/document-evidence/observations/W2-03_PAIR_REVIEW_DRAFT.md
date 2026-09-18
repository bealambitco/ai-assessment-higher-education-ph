# W2-03: paired observation (DRAFT for researcher confirmation)

Drafted by the AI assistant (Claude) on 18 September 2026 from the saved replies, run records and the automatic quotation check. Qualitative, not blind, not a score; the researcher confirms, modifies or rejects each row. Primary human scores are not affected.


## Gemini (google/gemini-3.1-pro-preview via ~google/gemini-pro-latest)

| Observation | Excerpt run | Full-text run |
|---|---|---|
| Run ID and attempt | D04 (attempt 1; RAW_SAVED) | D03 (attempt 1; RAW_SAVED) |
| Access evidence (platform, not only self-report) | Evidence pasted inline in the API request; 1035 input tokens; model self-report: read | Evidence pasted inline in the API request; 10930 input tokens; model self-report: read |
| Locators given | R12-DLSU-GenAI-Policy.pdf; R12-DLSU-GenAI-Policy.pdf; R12-DLSU-GenAI-Policy.pdf; R12-DLSU-GenAI-Policy.pdf | Section IV-d. Handling of Generative AI-Related Academic Dishonesty, Page 7; Section IV-d. Handling of Generative AI-Related Academic Dishonesty, Page 7; Section IV-d. Handling of Generative AI-Related Academic Dishonesty, Page 7; Section IV-d. Handling of Generative AI-Related Academic Dishonesty, Page 7 |
| Quotations match the source? | 4 of 4 quotations found word for word in the evidence file | 4 of 4 quotations found word for word in the evidence file |
| Proposed action | Withhold the immediate grading penalty and dishonesty filing. Interview the student to assess their understanding of the submitted work and determine if additional evidence of non-ownership exists. | Suspend the proposed refusal and grade penalty. Instead, use the 94% score to flag the submission and initiate a discussion with the student to gather additional evidence (e.g., verifying their thought process) before making a misconduct determination. |
| Generation latency | 16.8 s (no upload step) | 13.4 s (no upload step) |
| Attributable cost | US$0.0309 (OpenRouter-reported) | US$0.0437 (OpenRouter-reported) |

## Kimi (moonshotai/kimi-k3)

| Observation | Excerpt run | Full-text run |
|---|---|---|
| Run ID and attempt | D04 (attempt 1; RAW_SAVED) | D03 (attempt 1; RAW_SAVED) |
| Access evidence (platform, not only self-report) | Evidence pasted inline in the API request; 1079 input tokens; model self-report: read | Evidence pasted inline in the API request; 10620 input tokens; model self-report: read |
| Locators given | Retained excerpt, first paragraph; Retained excerpt, first paragraph; Retained excerpt, second paragraph; Retained excerpt, second paragraph | Section IV-d (Handling of Generative AI-Related Academic Dishonesty), PDF viewer page 7; Section IV-d, PDF viewer page 7; Section IV-d, PDF viewer page 7; Section IV-d, PDF viewer page 7 |
| Quotations match the source? | 7 of 7 quotations found word for word in the evidence file | 10 of 10 quotations found word for word in the evidence file |
| Proposed action | Accept the submission and use the 94% result only as a flag triggering further inquiry: meet with the student to ask questions about the report, have the student explain their research and writing process, check the work for hallucinated sources, compare writi | Do not refuse the submission, impose a grade penalty, or file a dishonesty case based solely on the 94% indicator. Treat the submission as flagged, then meet with the student about their research process (e.g., ask them to explain their thought process and ans |
| Generation latency | 114.8 s (no upload step) | 134.1 s (no upload step) |
| Attributable cost | US$0.0453 (OpenRouter-reported) | US$0.0651 (OpenRouter-reported) |

**Main observed difference (draft):** Same conclusion in both conditions for both models: no refusal, penalty or dishonesty case on the 94% detector result alone; detectors may only flag; additional evidence of non-ownership is required and any penalty must be communicated with the indicators. With the full document, locators named Section IV-d and page 7; excerpt runs cited the file name or paragraph order. Kimi's answers listed each proposed action separately and were longer.

**Alternative explanations:** longer context changes location cues and length; single run per condition, so stochastic variation is possible; page markers exist only in the full-text extraction.

**Reference challenge:** none identified in drafting.

**Researcher final disposition:** Confirm / Modify / Unresolved — ______ (initials, date)
