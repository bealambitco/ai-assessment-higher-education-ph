# Package 29: AI judge for the document-evidence extension

Exploratory. Applies the same DeepSeek V4 Pro judge (instructions and schema unchanged from packages 23 and 26) to the 24 Gemini and Kimi answers in package 24, so the excerpt and full-document conditions can be compared on the same criteria. Full-text runs are judged with the full retained document supplied, because that is what the model saw. No human scores exist for these answers; the judge is a cross-check, never a decider.

Run (your key, about US$0.50):

```bash
cd "<Staging>/29_DOCUMENT_AI_JUDGE_EXTENSION"
export OPENROUTER_API_KEY=...   # in your own terminal only
python3 ../22_RESEARCH_AUDIT_AND_RESULTS_READY_PACKAGE/06_code/ai_judge.py --package . --first 24 --reasoning high --max-tokens 16000 --provider baidu deepseek --workers 6
python3 -B code/process_outputs.py --write
```
