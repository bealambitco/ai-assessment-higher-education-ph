# Extensions

These are exploratory records collected after the primary answers. They are **not** part of the primary comparison and never change the primary scores. Aggregate results are in [../results/aggregate/](../results/aggregate/). The amendments D29–D31 in [../docs/deviations.md](../docs/deviations.md) record exactly what was done.

| Folder | What it is |
|---|---|
| [ai-judge-primary/](ai-judge-primary/) | DeepSeek V4 Pro (`deepseek/deepseek-v4-pro-0813`) judged each of the 96 primary answers once, against the same answer keys. It worked through OpenCode and OpenRouter with reasoning set to High, and was collected September 18, 2026, 04:10–04:56 +08:00. All 96 replies are valid; J024 was re-collected once and its first attempt is kept. |
| [ai-judge-claude/](ai-judge-claude/) | The same judge and instructions, applied through the OpenRouter API to 48 matched Claude answers (Fable 5.1 and Haiku 4.5; 12 scored cases × 2 models × 2 repetitions). Seven technically failed requests were retried once; their first attempts are kept. |
| [ai-judge-documents/](ai-judge-documents/) | The same judge and instructions, applied through the OpenRouter API on September 18, 2026 to the 24 document-evidence answers (Gemini and Kimi; excerpt and whole document). Whole-document answers were judged with the full document supplied. All 24 replies are valid: every answer was rated acceptable, with no serious error; the only Minor flags (3) were on excerpt runs. Eight first attempts used a prompt template with the wrong number of criteria (a preparation error) and were re-run; they are kept in `raw_outputs_first_attempts/`. The 12 whole-document prompts are withheld (they embed full institutional documents); their SHA-256 is recorded. |
| [document-evidence/](document-evidence/) | Six cases (two per workflow), each answered by Gemini 3.1 Pro Preview and by Kimi K3, once with the frozen excerpt and once with the whole retained document pasted as text. That gives 12 runs per model through the OpenRouter API, with no browsing or tools. |

## What each judge folder contains

- `prompts/`: the exact full prompt, one per judged answer. Each prompt holds the case, the policy excerpt, the answer key and the original model answer.
- `raw_outputs/`: the reply exactly as received.
- `parsed_outputs/`: the validated JSON judgment.
- `run_records/`: run metadata. In `ai-judge-primary`, the per-run records stayed in their prepared `NOT_RUN` state because collection was manual; the actual settings and times are in `protocol/SETUP_AND_EXCEPTIONS.md` and `03_COLLECTION_NOTES.md`.
- `raw_outputs_first_attempts/`: attempts that failed technically and were replaced.
- `protocol/`: judge instructions, setup and hashes.
- `qa/`: ingestion logs.

Judge IDs (J001–J096, K097–K144) are aliases. The private map from judge ID to masked answer ID, and from there to model, is **not** published. The 48 Claude answers and their judge IDs share numbers (K097 = masked answer R097), but the model behind each answer is not listed.

## Document-evidence folder

- `gemini/` and `kimi_optional/` hold the prompts, raw replies, parsed replies, run records (model ID, provider, tokens, OpenRouter-reported cost) and collection notes.
- `attachments/` holds only the **excerpt** evidence files. The full-document text files are not redistributed, because the institutions' terms were not verified. `protocol/SOURCE_MANIFEST.json` gives the SHA-256 of each full text and of the original source document, and [../literature/institutional-sources.csv](../literature/institutional-sources.csv) gives the URLs.
- `observations/*_PAIR_REVIEW_DRAFT.md` are paired observations drafted by an AI assistant (Claude) from the saved replies and the automatic quotation check (`auto_citation_check.json`), for the researcher to confirm. They are qualitative, not scores.

## Limits

- An AI judge is a cross-check, never the decider. There were no serious errors among the scored primary answers, so agreement cannot show whether the judge would catch one.
- The judge's severity calls were not fully consistent between the two runs.
- Provider effort labels do not mean matched computation. Latency includes provider and network effects.

Code to validate these replies: [../code/README.md](../code/README.md#4-re-validate-the-saved-ai-judge-and-extension-replies).
