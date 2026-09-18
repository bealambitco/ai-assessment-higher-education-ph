# W1-03: paired observation (DRAFT for researcher confirmation)

Drafted by the AI assistant (Claude) on 18 September 2026 from the saved replies, run records and the automatic quotation check. Qualitative, not blind, not a score; the researcher confirms, modifies or rejects each row. Primary human scores are not affected.


## Gemini (google/gemini-3.1-pro-preview via ~google/gemini-pro-latest)

| Observation | Excerpt run | Full-text run |
|---|---|---|
| Run ID and attempt | D01 (attempt 1; RAW_SAVED) | D02 (attempt 1; RAW_SAVED) |
| Access evidence (platform, not only self-report) | Evidence pasted inline in the API request; 963 input tokens; model self-report: read | Evidence pasted inline in the API request; 55399 input tokens; model self-report: read |
| Locators given | Section 3; Sec. 3.1; Sec. 3.2; Sec. 3.2 | Title 2, Article 5, Sec. 3.1; Title 2, Article 5, Sec. 3.2; Title 2, Article 5, Sec. 3.2; Title 2, Article 5, Section 3 |
| Quotations match the source? | 5 of 5 quotations found word for word in the evidence file | 5 of 5 quotations found word for word in the evidence file |
| Proposed action | Inform the instructor that a 2.5 cannot be submitted as a passing mark for a graduate student, and provide the requested undergraduate exam thresholds (70% for major subjects, 60% for general education). | Inform the instructor of the correct graduate and undergraduate grading scales and thresholds, reject the 2.5 as a passing grade for the graduate seminar, and advise the instructor to submit the appropriate non-passing notation for the graduate student. |
| Generation latency | 19.2 s (no upload step) | 30.1 s (no upload step) |
| Attributable cost | US$0.0327 (OpenRouter-reported) | US$0.1504 (OpenRouter-reported) |

## Kimi (moonshotai/kimi-k3)

| Observation | Excerpt run | Full-text run |
|---|---|---|
| Run ID and attempt | D01 (attempt 1; RAW_SAVED) | D02 (attempt 1; RAW_SAVED) |
| Access evidence (platform, not only self-report) | Evidence pasted inline in the API request; 993 input tokens; model self-report: read | Evidence pasted inline in the API request; 53812 input tokens; model self-report: read |
| Locators given | Sec. 3.1; Sec. 3.2; Sec. 3.2; Section 4 | Title 2, Article 5 (Examinations and Grades), Sec. 3.1; PDF viewer page 16; Title 2, Article 5, Sec. 3.2; PDF viewer page 17; Title 2, Article 5, Sec. 3.2; PDF viewer page 17; Title 2, Article 5, Section 4; PDF viewer page 17 |
| Quotations match the source? | 5 of 5 quotations found word for word in the evidence file | 8 of 8 quotations found word for word in the evidence file |
| Proposed action | Do not submit the 2.5 as a graduate passing mark; apply the graduate scale (2.0 lowest passing) and refer the result to the graduate school/registrar for the correct non-passing notation and any official remedy. For the undergraduate major course, apply the 1. | Withhold submission of 2.5 as a passing graduate grade; re-evaluate the result against the Sec. 3.1 graduate scale (2.0 lowest passing) and refer the confirmed outcome to the graduate school dean and the Registrar to determine the correct recording/notation fo |
| Generation latency | 109.7 s (no upload step) | 273.7 s (no upload step) |
| Attributable cost | US$0.0413 (OpenRouter-reported) | US$0.1900 (OpenRouter-reported) |

**Main observed difference (draft):** Same conclusion in both conditions for both models: 2.5 is not a passing graduate mark (graduate scale 1.0–2.0; 2.0 lowest passing), the undergraduate scale is 1.0–3.0 with 70% (major) and 60% (general education) examination cut-offs, and instructor authority operates within the prescribed system. With the full document, locators became specific (article and section, with page markers for Kimi); Gemini's full-text answer advised entering 'the appropriate non-passing notation' without naming one, and Kimi referred the notation question to the dean and registrar.

**Alternative explanations:** longer context changes location cues and length; single run per condition, so stochastic variation is possible; page markers exist only in the full-text extraction.

**Reference challenge:** none identified in drafting.

**Researcher final disposition:** Confirm / Modify / Unresolved — ______ (initials, date)
