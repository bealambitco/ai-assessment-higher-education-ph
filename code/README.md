# Code

Run every command **from the repository root**, using Python 3.12. Most of the code uses only the standard library. The flag `-B` stops Python from writing `__pycache__` folders.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r code/requirements.txt      # only python-docx, for the Word reviewer packets
```

## 1. Check integrity

```bash
python3 -B code/verify_hashes.py
```

Expected output:
- `Frozen record: 88 of 88 public frozen files match; 4 private files withheld`
- `Release manifest: N of N files match`

## 2. Try the release checks

```bash
python3 -B code/try_checks.py
```

This applies the frozen checks to three example answers for case W3-02:
- A correct 84.6% is released with a warning.
- A wrong 85% under the expected name is **blocked**.
- The same wrong 85% under a different name is **released**, because the arithmetic check does not run on a renamed quantity. This is the gap seen in the Claude extension.

To test your own answer, run `--case W3-04 --answer-json my_answer.json`. The answer must follow [benchmark/controls/output_schema.json](../benchmark/controls/output_schema.json).

## 3. Run the tests

```bash
python3 -B code/tests/test_supplement.py --frozen-code code/frozen_2026-09-15/experiment.py
python3 -B code/tests/test_ai_judge_parser.py
```

Both suites use synthetic fixtures only; no real data is read. Expected result: `Ran 12 tests ... OK` for each suite.

## 4. Re-validate the saved AI-judge and extension replies

```bash
python3 -B code/extensions/ai_judge/process_outputs.py --package extensions/ai-judge-primary   # expect 96 valid
python3 -B code/extensions/ai_judge/process_outputs.py --package extensions/ai-judge-claude    # expect 48 valid
```

These commands check the replies only and write nothing. Do **not** add `--write`, because that rewrites parsed records.

The document-evidence parser (`code/extensions/document_evidence/process_outputs.py --package extensions/document-evidence --model gemini`) checks the SHA-256 of every attached evidence file. The full-document text files are not redistributed, so it stops at the first full-text run. To rerun it:
1. Recreate each full text from the source listed in [extensions/document-evidence/protocol/SOURCE_MANIFEST.json](../extensions/document-evidence/protocol/SOURCE_MANIFEST.json).
2. Check each file against its `full_text_sha256`.
3. Place the files in `extensions/document-evidence/attachments/`.

## What is here

| Path | What it is | Runnable here? |
|---|---|---|
| [frozen_2026-09-15/](frozen_2026-09-15/) | The code frozen on September 15, 2026. The files are byte-identical; their hashes are in the freeze record. It includes `experiment.py` (parser, checks, import, score lock), `analyze.py` (primary metrics), `scoring.py`, `timed_review.py`, `reviewer_packets.py` and `test_experiment.py`. Its own [README](frozen_2026-09-15/README.md) was written for the original working folder and is kept as provenance. | You can import the functions, as `try_checks.py` does. The commands that call `assert_frozen()` need the 4 withheld private files, so they stop. |
| [supplement/analyze_supplement.py](supplement/analyze_supplement.py) | Post-freeze analysis S1–S16 (addendum D1–D24). It reuses the frozen `metrics()`. | Needs private keys and per-answer scores |
| [supplement/check_scoring_forms.py](supplement/check_scoring_forms.py), [supplement/sync_scoring_forms.py](supplement/sync_scoring_forms.py) | Checks the scoring forms and copies them into the score file | Needs the scoring forms |
| [supplement/reviewer_agreement.py](supplement/reviewer_agreement.py) | Compares reviewer returns with the locked scores (D25) | Needs the reviewer returns |
| [supplement/extension_controls.py](supplement/extension_controls.py), [supplement/prepare_extension_scoring.py](supplement/prepare_extension_scoring.py) | Claude extension: applies the checks and prepares masked forms (D26) | Needs private imports |
| [supplement/ai_judge.py](supplement/ai_judge.py) | AI-judge API runner (OpenRouter) and the `--agree` computation (D29, D30) | The runner needs your own API key. `--agree` needs the private judge-to-answer map |
| [supplement/export_public_tables.py](supplement/export_public_tables.py) | Writes the aggregate CSV files in `results/aggregate/` from the private analysis outputs | Documents the derivation; needs the private outputs |
| [supplement/public_workbook_copy.py](supplement/public_workbook_copy.py) | Makes the public copy of the analysis workbook, with the timing-item IDs withheld | Needs the researcher's workbook |
| [extensions/ai_judge/process_outputs.py](extensions/ai_judge/process_outputs.py) | Validates and parses judge replies (used for both judge sets) | Yes |
| [extensions/document_evidence/run_api.py](extensions/document_evidence/run_api.py), [extensions/document_evidence/process_outputs.py](extensions/document_evidence/process_outputs.py) | Document-evidence runner and parser (D31) | The runner needs an API key and the full texts |
| [tests/](tests/) | `test_supplement.py` (12 synthetic tests) and `test_ai_judge_parser.py` (12 tests) | Yes |
| [verify_hashes.py](verify_hashes.py), [try_checks.py](try_checks.py) | Integrity check and a checks demonstration, added for this release | Yes |

### Running the frozen code in its original layout

```bash
python3 -B code/verify_hashes.py --assemble /tmp/frozen_2026-09-15
```

This command copies the 88 public frozen files back into the original layout (`code/`, `inputs/`, `references/`, `prompts/`, `protocol/`). It does not add the withheld private files.

### API runners

`ai_judge.py` and `run_api.py` call the OpenRouter API. You will be charged for the calls.
- Set your key only in your own terminal, with `export OPENROUTER_API_KEY=...`. Never put a key in a file.
- Use `--dry-run` first.
- Both scripts refuse to overwrite a saved reply.

## Changes from the working copies

The scripts outside `frozen_2026-09-15/` are copies of the working versions with minimal edits so they run from this layout. The original SHA-256 values and each edit are listed in [../docs/path-mapping.md](../docs/path-mapping.md#code-copies-and-portability-edits). No analysis logic was changed.
