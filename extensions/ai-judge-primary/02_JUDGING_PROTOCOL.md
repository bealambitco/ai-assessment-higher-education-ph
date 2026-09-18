# Exploratory AI-judge protocol

Prepared 2026-09-18T01:15:11+08:00. User requested this addition after primary collection and during human scoring. User selected and confirmed deepseek/deepseek-v4-pro-0813. Interface, reasoning setting and other actual execution settings remain pending confirmation. No model was run by the preparation script.

## Scope and purpose

One AI judge independently receives each saved response with the same case, supplied policy, researcher-adjudicated reference and criteria. It does not see human labels, reviewer judgments, release outcomes, model identities or other responses. This is reference-guided AI/human comparison, not independent answer-key validation or a new primary release pathway. Keep the original study title, RQs, cases and controls unchanged.

All 96 original primary responses are prepared, one first attempt each. First 48 exactly match the authorized fallback subset, followed by the next 24 and last 24. Random seed 2026091804 shuffles within those blocks. Judge aliases prevent direct recognition of human response IDs but do not remove recognition of familiar case content. The private map is withheld from the judge. The 48 priority records include the three human responses previously subject to substantive AI clarification; preserve that disclosure and show an exclusion sensitivity with its resulting imbalance.

## Configuration and execution

Confirm exact version, app, displayed reasoning/temperature and routing before the first run. Record unknown/not exposed rather than invent settings. Hold them fixed. Fresh chat per prompt, prompt unchanged, no workspace or external tools. One response per call avoids pairwise position comparisons. The full prompt already contains all evidence; do not attach files. Do not ask for a corrected answer or tune the prompt to improve agreement on study items.

Use the supplied fictitious practice exercise only to check transport and formatting, not to select the model with greatest agreement on study outcomes. Preserve a practice failure. Any prompt change after the first experimental output creates a separately versioned deviation; preserve the earlier target and response.

Keep original replies exactly as received. Save refusals and malformed outputs too. No best-of retries. If a technical retry is necessary, record every attempt and the reason, use a new attempt file, and retain first-attempt coverage as the primary exploratory report. Never silently replace a judgment.

## Exposure and sequence

Safest manual sequence: finish all intended human initial and repeat scoring before collecting/viewing judge results. If collection happens earlier, hide results from the researcher through a separate collector or automated capture; manual copy/paste cannot guarantee non-exposure. Record response-specific exposure when known. Do not adjust human scores to match the judge. Preserve initial labels, any later adjudication and disagreements separately.

## Planned descriptive analysis, after locking relevant human scores

Report AI collection coverage, valid versus malformed/refused/missing outputs, model/settings, any retries and exposure. Compare only overlapping human-scored and AI-judged originals: exact criterion agreement, severity confusion table, serious (Major/Critical) versus non-serious agreement, and acceptability agreement, each with explicit eligible counts. Cannot judge and unavailable records remain separate and visible; they are not automatically incorrect. Multiple criteria, repetitions and paired assessments are dependent within cases. Describe agreement, not AI accuracy against validated ground truth. Independent human reviewer comparisons are separate and limited to actual overlap.

Inspect disagreements with source support after the human lock; do not assume either rater is correct. Shared agreement with a flawed reference is possible. No majority vote replaces the original human score. AI-only judgments on human-unscored responses remain a separate exploratory description, not imputed primary scores. Do not choose the collection stop based on observed agreement. Prefer complete priority blocks; record exact coverage if interrupted.

## Sources and limits

Zheng et al. (2023), Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena: https://arxiv.org/abs/2306.05685 . Empirical motivation for checking judge biases; different tasks, not validation for Philippine policy judgments.
Chen et al. (2025), Beyond the Surface: Measuring Self-Preference in LLM Judgments: https://aclanthology.org/2025.emnlp-main.86/ . Motivation to separate judge family and disclose self-preference risks; an outside family is not proof of neutrality.
OpenRouter model listing checked September 18, 2026: https://openrouter.ai/deepseek/deepseek-v4-pro-0813 . The researcher confirmed this model ID after preparation; actual interface and settings remain unconfirmed. Another listing uses the older 0423 label: https://openrouter.ai/deepseek/deepseek-v4-pro/api . Do not silently treat them as the same version.
