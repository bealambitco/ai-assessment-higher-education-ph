#!/bin/zsh
# Re-runs the 8 judgments whose first prompts used the wrong criteria template. Needs OPENROUTER_API_KEY in this shell.
cd "${0:A:h}" || exit 1
[ -z "$OPENROUTER_API_KEY" ] && { echo "OPENROUTER_API_KEY is not set in this tab. Export it, then run this script again."; exit 1; }
python3 ../22_RESEARCH_AUDIT_AND_RESULTS_READY_PACKAGE/06_code/ai_judge.py --package . --ids K203 K204 K211 K212 K215 K216 K223 K224 --reasoning high --max-tokens 16000 --provider baidu deepseek --workers 4
python3 -B code/process_outputs.py --write
echo "JUDGE FIX RUN FINISHED"
