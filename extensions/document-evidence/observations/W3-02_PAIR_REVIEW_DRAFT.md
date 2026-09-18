# W3-02: paired observation (DRAFT for researcher confirmation)

Drafted by the AI assistant (Claude) on 18 September 2026 from the saved replies, run records and the automatic quotation check. Qualitative, not blind, not a score; the researcher confirms, modifies or rejects each row. Primary human scores are not affected.


## Gemini (google/gemini-3.1-pro-preview via ~google/gemini-pro-latest)

| Observation | Excerpt run | Full-text run |
|---|---|---|
| Run ID and attempt | D05 (attempt 1; RAW_SAVED) | D06 (attempt 1; RAW_SAVED) |
| Access evidence (platform, not only self-report) | Evidence pasted inline in the API request; 1618 input tokens; model self-report: read | Evidence pasted inline in the API request; 80294 input tokens; model self-report: read |
| Locators given | Lecture Criteria; Lecture Criteria; Lecture Criteria; Lecture Criteria | Section 5. Basis of Grading [PDF viewer page 26]; Section 5. Basis of Grading [PDF viewer page 26] |
| Quotations match the source? | 4 of 4 quotations found word for word in the evidence file | 2 of 2 quotations found word for word in the evidence file |
| Proposed action | Record the student's periodic grade as 84.6% calculated via the mandated component weights, and advise the instructor against using the unweighted raw points total. | Record the student's periodic grade as 84.60%. Advise the instructor to apply the mandated percentage weights and clarify that the exam does not require exactly 90 raw points. |
| Generation latency | 20.8 s (no upload step) | 57.6 s (no upload step) |
| Attributable cost | US$0.0391 (OpenRouter-reported) | US$0.2218 (OpenRouter-reported) |

## Kimi (moonshotai/kimi-k3)

| Observation | Excerpt run | Full-text run |
|---|---|---|
| Run ID and attempt | D05 (attempt 1; RAW_SAVED) | D06 (attempt 1; RAW_SAVED) |
| Access evidence (platform, not only self-report) | Evidence pasted inline in the API request; 1561 input tokens; model self-report: read | Evidence pasted inline in the API request; 77482 input tokens; model self-report: read |
| Locators given | Opening line, Lecture grading table, retained excerpt (Source file: S-USPF-Tertiary-Handbook-2023.pdf); Lecture criteria table; Lecture criteria table, under Class Standing; Lecture criteria table, under Class Standing | Article II, Section 5. Basis of Grading, [PDF viewer page 26] (printed page 21); Article II, Section 5. Basis of Grading, Lecture criteria table, [PDF viewer page 26] (printed page 21); Article II, Section 5. Basis of Grading, [PDF viewer page 27] (printed page 22); Article II, Section 4. Examinations and Grading System, [PDF viewer page 25] (printed page 20) |
| Quotations match the source? | 12 of 12 quotations found word for word in the evidence file | 5 of 5 quotations found word for word in the evidence file |
| Proposed action | Record the Prelim grade as 84.60% computed under the Section 5 weights; the department chair should confirm that subweights are nested within (not additive to) the 40/30/30 parent weights and that no fixed raw-point totals (e.g., a 90-point exam) are mandated, | Record 84.60% (16.80 + 9.00 + 9.00 + 12.00 + 13.80 + 24.00) as the Prelim periodic weighted score, computed by applying Section 5's subweights to each component's percentage; correct the grade sheet to reject both the 255/300 unweighted method and any double-c |
| Generation latency | 227.9 s (no upload step) | 827.5 s (no upload step) |
| Attributable cost | US$0.0702 (OpenRouter-reported) | US$0.2810 (OpenRouter-reported) |

**Main observed difference (draft):** Same result in both conditions for both models: the policy-weighted periodic grade is 84.6% (not the raw 255/300 = 85%), subweights are nested within parent weights, and no fixed 90-point exam is required. Kimi's full-document run (D06) came back empty three times at an 8,000-token limit and succeeded on one technical retry at 32,000 tokens (827 s). Kimi also noted that conversion to the official grade scale is not in the excerpt and should be routed to the college or registrar.

**Alternative explanations:** longer context changes location cues and length; single run per condition, so stochastic variation is possible; page markers exist only in the full-text extraction.

**Reference challenge:** none identified in drafting.

**Researcher final disposition:** Confirm / Modify / Unresolved — ______ (initials, date)
