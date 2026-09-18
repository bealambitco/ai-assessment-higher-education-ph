# W1-06: paired observation (DRAFT for researcher confirmation)

Drafted by the AI assistant (Claude) on 18 September 2026 from the saved replies, run records and the automatic quotation check. Qualitative, not blind, not a score; the researcher confirms, modifies or rejects each row. Primary human scores are not affected.


## Gemini (google/gemini-3.1-pro-preview via ~google/gemini-pro-latest)

| Observation | Excerpt run | Full-text run |
|---|---|---|
| Run ID and attempt | D08 (attempt 1; RAW_SAVED) | D07 (attempt 1; RAW_SAVED) |
| Access evidence (platform, not only self-report) | Evidence pasted inline in the API request; 856 input tokens; model self-report: read | Evidence pasted inline in the API request; 5541 input tokens; model self-report: read |
| Locators given | Source text | Section VI, PDF viewer page 12 |
| Quotations match the source? | 1 of 1 quotations found word for word in the evidence file | 1 of 1 quotations found word for word in the evidence file |
| Proposed action | Query the central university administration or check the official institutional policy repository to determine if a newer Higher Education Memo supersedes the April 2025 version, or if the April 2025 guidelines remain in active enforcement. | Consult the central university policy repository or the issuing authority to determine if a newer version of the guidelines has been promulgated since April 2025 or if the retained version remains in force. |
| Generation latency | 15.2 s (no upload step) | 15.5 s (no upload step) |
| Attributable cost | US$0.0227 (OpenRouter-reported) | US$0.0347 (OpenRouter-reported) |

## Kimi (moonshotai/kimi-k3)

| Observation | Excerpt run | Full-text run |
|---|---|---|
| Run ID and attempt | D08 (attempt 1; RAW_SAVED) | D07 (attempt 1; RAW_SAVED) |
| Access evidence (platform, not only self-report) | Evidence pasted inline in the API request; 880 input tokens; model self-report: read | Evidence pasted inline in the API request; 5425 input tokens; model self-report: read |
| Locators given | Section VI (Updating and Revision), as identified in the scenario; retained excerpt, Source file: R19-ADMU-GenAI-HE-Guidelines.pdf; Attachment header, W1-06_excerpt.txt | VI. Updating and Revision [PDF viewer page 12]; I. Introduction, A. Purpose [PDF viewer page 3]; IV. Specific Guidelines of Schools, Departments, and Other Units [PDF viewer page 11]; Retained document header (front matter, before [PDF viewer page 1]) |
| Quotations match the source? | 2 of 2 quotations found word for word in the evidence file | 5 of 5 quotations found word for word in the evidence file |
| Proposed action | Treat the April 29, 2025 guidance as a retained historical copy and, before finalizing the department's assessment-policy update, request written confirmation of its current operative status from the issuing Higher Education office, including any post-April 20 | Before finalizing the department's assessment-policy update, send a currency-verification request to the Higher Education memo custodian/issuing office for (a) the current official version of the GenAI guidelines, (b) any amendments, review records, or superse |
| Generation latency | 110.0 s (no upload step) | 319.6 s (no upload step) |
| Attributable cost | US$0.0361 (OpenRouter-reported) | US$0.0771 (OpenRouter-reported) |

**Main observed difference (draft):** Same conclusion in both conditions for both models: the six-to-twelve-month review clause has lapsed by September 2026, but the clause is a review mandate, not an expiry rule, so current status is uncertain and must be verified with the issuing office. With the full document, both models cited the section and page (VI, page 12) and Kimi added the purpose section; excerpt runs cited only the excerpt.

**Alternative explanations:** longer context changes location cues and length; single run per condition, so stochastic variation is possible; page markers exist only in the full-text extraction.

**Reference challenge:** none identified in drafting.

**Researcher final disposition:** Confirm / Modify / Unresolved — ______ (initials, date)
