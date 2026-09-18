#!/bin/zsh
# Runs the 24 document-extension judgments (DeepSeek V4 Pro via OpenRouter), then validates the replies.
# Needs OPENROUTER_API_KEY in this shell. The key is never written to disk by this script.
cd "${0:A:h}" || exit 1
if [ -z "$OPENROUTER_API_KEY" ]; then
  echo "OPENROUTER_API_KEY is not set in this tab. Run: export OPENROUTER_API_KEY=... then run this script again."
  exit 1
fi
python3 ../22_RESEARCH_AUDIT_AND_RESULTS_READY_PACKAGE/06_code/ai_judge.py --package . --first 24 --reasoning high --max-tokens 16000 --provider baidu deepseek --workers 6
python3 -B code/process_outputs.py --write
echo "JUDGE RUN FINISHED"
