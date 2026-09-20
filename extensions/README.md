# Extensions

These folders hold work beyond the primary comparison: cross-checks on the scoring, revised release checks,
and further collections that change one thing at a time (which model answers, and what evidence it is given).
Results across the new collections are in [findings-by-arm.md](findings-by-arm.md); the plan they follow is
[../docs/extension-protocol.md](../docs/extension-protocol.md) and every departure from it is in
[../docs/extension-deviations.md](../docs/extension-deviations.md).

The AI-judge and document-evidence folders below are exploratory records collected after the primary answers. They are **not** part of the primary comparison and never change the primary scores. Aggregate results are in [../results/aggregate/](../results/aggregate/). The amendments D29–D31 in [../docs/deviations.md](../docs/deviations.md) record exactly what was done.

| Folder | What it is |
|---|---|
| [revised-checks/](revised-checks/) | The release checks rewritten to tolerate harmless differences and to fail closed when a quantity is missing, then re-run over all 192 collected answers. [Specification](revised-checks/SPECIFICATION.md), [findings](revised-checks/FINDINGS.md). |
| [low-resource-models/](low-resource-models/) | The same 24 cases answered by open-weight models in the 8B-30B range, the kind a school could self-host, with the same excerpt and the same required format. |
| [whole-documents/](whole-documents/) | All 24 cases answered with the entire governing document attached instead of the excerpt, so the model must find the passage itself. |
| [rule-discovery/](rule-discovery/) | Eight cases answered with every retained document from the institution and no passage selected, so the model must decide which document and which section govern the case. |
| [answer-key-review/](answer-key-review/) | Packets and instructions for independent Philippine higher-education experts to validate the answer keys themselves. |
| [second-timer/](second-timer/) | The instrument and instructions for a second, outside observer to time the checking work. |
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
