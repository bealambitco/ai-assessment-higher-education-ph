# Round 2: the commands to run

The working copy is the local package `30_ROUND2_EXTENSION`, beside packages 21 to 29; this repository holds
the publishable subset. Work locally, sync, then commit here:

```bash
python3 -B code/extensions/round2/sync_local_and_repo.py --package "$PKG" --check
python3 -B code/extensions/round2/sync_local_and_repo.py --package "$PKG" --to-repo
```

Every command below is run from the repository root. Paths in angle brackets are the ones on this machine;
replace them if the folders move. Prompts, bundles and replies stay **outside** the repository, in the
working directory, because raw answers are not published.

```
WORK=".../Assessment_Control_Capstone_Methodology_Revision_Staging/30_ROUND2_EXTENSION/work"
POLICIES=".../Assessment_Control_Capstone_v2/1_WORK_HERE/SOURCES/policies"
ATTACH=".../24_DOCUMENT_EVIDENCE_EXTENSION_PACKAGE/attachments"
PKG=".../30_ROUND2_EXTENSION"
```

## 0. Before anything (no cost)

```bash
python3 -B code/extensions/round2/freeze_round2.py --verify
python3 -B -m unittest discover -s code/tests -p 'test_*round2.py' -p 'test_checks_v2.py'
python3 -B code/extensions/round2/score_round2.py --self-test
python3 -B code/extensions/round2/timing_round2.py --self-test
```

The round-1 supplement tests take an argument and are run separately; plain discovery reports them as errors
because it cannot pass it:

```bash
python3 -B code/tests/test_supplement.py --frozen-code code/frozen_2026-09-15/experiment.py
```

## 1. Prepare the prompts (already done; re-runnable, no cost)

```bash
python3 -B code/extensions/round2/prepare_round2.py --arm access    --work "$WORK" --documents "$POLICIES" --documents "$ATTACH"
python3 -B code/extensions/round2/prepare_round2.py --arm documents --work "$WORK" --documents "$POLICIES" --documents "$ATTACH"
python3 -B code/extensions/round2/prepare_round2.py --arm discovery --work "$WORK" --documents "$POLICIES" --documents "$ATTACH"
```

Prepared on September 20, 2026: 24 access prompts (about 35,000 input tokens in total), 24 document prompts
(about 474,000) and 8 rule-discovery prompts (about 438,000; the largest single prompt is about 187,000
tokens, so that arm needs a model with a context window of 262k, not 131k).

## 2. Collect (this costs money; run it with your own key)

Set the key in your own terminal. It is never written to a file, a record or the screen.

```bash
export OPENROUTER_API_KEY=...
```

Always do a dry run first: it prints what would be sent and calls nothing.

```bash
python3 -B code/extensions/round2/run_openrouter.py --work "$WORK" --arm access \
    --model-id openai/gpt-oss-20b --label gptoss20b --dry-run
```

Then collect. Start with `--limit 2` on the first model to see a reply before spending the rest.

| Arm | Command | Rough cost |
|---|---|---|
| G access | `--arm access --model-id openai/gpt-oss-20b --label gptoss20b` | under US$0.01 |
| G access | `--arm access --model-id qwen/qwen3-30b-a3b-instruct-2507 --label qwen3-30b-a3b` | under US$0.01 |
| G access | `--arm access --model-id google/gemma-3-12b-it --label gemma3-12b` | under US$0.01 |
| C documents | `--arm documents --model-id google/gemini-3.1-pro-preview --label gemini31pro` | a few US$ |
| C documents | `--arm documents --model-id moonshotai/kimi-k3 --label kimik3` | a few US$ |
| D discovery | `--arm discovery --model-id google/gemini-3.1-pro-preview --label gemini31pro` | a few US$ |
| D discovery | `--arm discovery --model-id qwen/qwen3-30b-a3b-instruct-2507 --label qwen3-30b-a3b` | under US$0.10 |

Costs for arms C and D depend on the model's input price; the run record stores the figure OpenRouter
reports for every request, so the paper uses the provider's number rather than an estimate. Re-running the
same command retries only the runs that have no saved reply.

## 3. Parse and apply the checks (no cost)

```bash
python3 -B code/extensions/round2/parse_round2.py --work "$WORK" --arm access \
    --out-private "$WORK/../analysis" --out-public extensions/v2/results
```

Repeat for `--arm documents` and `--arm discovery`. This writes per-run tables locally and a public summary
CSV, and applies both check versions. It does not judge correctness: that is scoring.

## 4. Score (this is the part only you can do)

```bash
python3 -B code/extensions/round2/score_round2.py --status
```

See [scoring/HOW_TO_SCORE.md](scoring/HOW_TO_SCORE.md) for the order, the failure classes and how to lock.

## 5. Key review and the second timer

```bash
python3 -B code/extensions/round2/key_review_packets.py --sample 6 --out "$WORK/../key-review" --packet-label A,B
python3 -B code/extensions/round2/key_review_intake.py --packets "$WORK/../key-review-returned" --out "$WORK/../key-review-returned/intake"
python3 -B code/extensions/round2/timing_round2.py --self-test
```

Instructions to send out: [key-review/REVIEWER_INSTRUCTIONS.md](key-review/REVIEWER_INSTRUCTIONS.md) and
[second-timer/TIMER_INSTRUCTIONS.md](second-timer/TIMER_INSTRUCTIONS.md).

## Notes

* Nothing here modifies round-1 files. Round-2 outputs are written beside them.
* The runner sends one request per case, with no tools and no follow-up, and keeps the first reply.
  Technical failures are retried up to three times within fifteen minutes; a reply that arrives is kept
  whatever it contains, including an unparseable one, because format failures are a result.
* If a model refuses or returns an error for a specific case, that is recorded in the run record and counted;
  do not reword the prompt to get a better answer.
