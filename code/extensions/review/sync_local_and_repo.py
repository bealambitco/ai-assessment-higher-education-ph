"""Keep the local extension package and the public repository copy in step, local first.

The working package is the local one, beside packages 21 to 29. The repository holds only the publishable
subset: protocol, specifications, code, document map, aggregate results and reviewer materials. Prompts,
bundles, raw replies, per-answer tables, packets and score files stay local.

  python3 -B code/extensions/review/sync_local_and_repo.py --package "<...>/30_ROUND2_EXTENSION" --check
  python3 -B code/extensions/review/sync_local_and_repo.py --package "<...>/30_ROUND2_EXTENSION" --to-local
  python3 -B code/extensions/review/sync_local_and_repo.py --package "<...>/30_ROUND2_EXTENSION" --to-repo

--to-local   copies the publishable files from the repository into the package (mirror for your own copy)
--to-repo    copies them back from the package into the repository, for you to commit
--check      reports differences and writes nothing

Nothing is deleted and nothing outside the mapped paths is touched.
"""
import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

# repository path -> package path
MAP = {
    "extensions/README.md": "00_EXTENSIONS_INDEX.md",
    "docs/extension-protocol.md": "01_PROTOCOL/EXTENSION_PROTOCOL.md",
    "docs/extension-deviations.md": "01_PROTOCOL/EXTENSION_DEVIATIONS.md",
    "extensions/revised-checks/SPECIFICATION.md": "01_PROTOCOL/REVISED_CHECKS_SPECIFICATION.md",
    "docs/extension-commands.md": "01_PROTOCOL/COMMANDS.md",
    "extensions/revised-checks/confirmed-errors.json": "01_PROTOCOL/confirmed-errors.json",
    "docs/scoring-plan.md": "02_SCORING/SCORING_PLAN.md",
    "docs/failure-classes.md": "02_SCORING/FAILURE_CLASSES.md",
    "docs/how-to-score.md": "02_SCORING/HOW_TO_SCORE.md",
    "extensions/whole-documents/README.md": "03_DOCUMENTS/README.md",
    "benchmark/governing-documents.json": "03_DOCUMENTS/governing-documents.json",
    "extensions/rule-discovery/README.md": "04_RULE_DISCOVERY/README.md",
    "extensions/low-resource-models/README.md": "05_LOW_RESOURCE_MODELS/README.md",
    "extensions/answer-key-review/README.md": "06_KEY_REVIEW/README.md",
    "extensions/answer-key-review/PACKETS.md": "06_KEY_REVIEW/PACKETS.md",
    "extensions/answer-key-review/REVIEWER_INSTRUCTIONS.md": "06_KEY_REVIEW/REVIEWER_INSTRUCTIONS.md",
    "extensions/second-timer/README.md": "07_SECOND_TIMER/README.md",
    "extensions/second-timer/TIMER_INSTRUCTIONS.md": "07_SECOND_TIMER/TIMER_INSTRUCTIONS.md",
    "extensions/second-timer/SESSION_CHECKLIST.md": "07_SECOND_TIMER/SESSION_CHECKLIST.md",
    "extensions/findings-by-arm.md": "08_RESULTS_PUBLIC/FINDINGS_BY_ARM.md",
    "extensions/low-resource-models/summary.csv": "08_RESULTS_PUBLIC/low_resource_summary.csv",
    "extensions/low-resource-models/summary-matched-prompt.csv": "08_RESULTS_PUBLIC/low_resource_summary_matched_prompt.csv",
    "extensions/whole-documents/summary.csv": "08_RESULTS_PUBLIC/documents_summary.csv",
    "extensions/rule-discovery/summary.csv": "08_RESULTS_PUBLIC/discovery_summary.csv",
    "results/Analysis_Workbook_Extension.xlsx": "analysis/Analysis_Workbook_Extension.xlsx",
    "extensions/revised-checks/FINDINGS.md": "08_RESULTS_PUBLIC/REVISED_CHECKS_FINDINGS.md",
    "extensions/revised-checks/decisions_by_model.csv": "08_RESULTS_PUBLIC/revised_checks_decisions_by_model.csv",
    "extensions/revised-checks/effect_by_outcome.csv": "08_RESULTS_PUBLIC/revised_checks_effect_by_outcome.csv",
    "extensions/revised-checks/changes_public.csv": "08_RESULTS_PUBLIC/revised_checks_changes.csv",
    "extensions/revised-checks/run-record.json": "08_RESULTS_PUBLIC/revised_checks_run_record.json",
}
CODE = ["revised_checks/checks.py", "revised_checks/rerun.py", "revised_checks/freeze.py",
        "collection/prepare_prompts.py", "collection/run_openrouter.py", "collection/parse_replies.py",
        "collection/build_workbook.py", "review/score_answers.py", "review/timing_session.py",
        "review/key_review_packets.py", "review/key_review_intake.py", "review/sync_local_and_repo.py"]
TESTS = ["test_revised_checks.py", "test_score_answers.py", "test_timing_session.py"]
for name in CODE:
    MAP[f"code/extensions/{name}"] = f"09_CODE/{name.split('/')[-1]}"
for name in TESTS:
    MAP[f"code/tests/{name}"] = f"09_CODE/tests/{name}"

LOCAL_ONLY = ["work/", "analysis/", "key-review/*.docx", "scores/"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).exists() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", required=True, help="the local 30_ROUND2_EXTENSION folder")
    ap.add_argument("--to-local", action="store_true")
    ap.add_argument("--to-repo", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if sum(map(bool, (a.to_local, a.to_repo, a.check))) != 1:
        raise SystemExit("choose exactly one of --to-local, --to-repo, --check")

    pkg = Path(a.package).expanduser()
    same, differ, missing_repo, missing_pkg, copied = [], [], [], [], []
    for rel, prel in MAP.items():
        r, p = REPO / rel, pkg / prel
        hr, hp = sha(r), sha(p)
        if hr is None:
            missing_repo.append(rel)
        if hp is None:
            missing_pkg.append(prel)
        if hr and hp and hr == hp:
            same.append(rel)
        elif hr and hp:
            differ.append(rel)
        if a.to_local and hr and hr != hp:
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(r, p)
            copied.append(prel)
        if a.to_repo and hp and hr != hp:
            r.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, r)
            copied.append(rel)

    print(f"mapped files {len(MAP)}: identical {len(same)}, different {len(differ)}, "
          f"missing in repo {len(missing_repo)}, missing in package {len(missing_pkg)}")
    for rel in differ:
        print("  differs:", rel)
    for rel in missing_repo:
        print("  missing in repo:", rel)
    for rel in missing_pkg:
        print("  missing in package:", rel)
    if copied:
        print(f"copied {len(copied)} file(s)")
    if a.to_local or a.to_repo:
        record = {"synced_at": datetime.now(timezone.utc).astimezone().isoformat(),
                  "direction": "repo -> package" if a.to_local else "package -> repo",
                  "files": copied, "local_only_paths": LOCAL_ONLY,
                  "sha256": {rel: sha(REPO / rel) for rel in MAP}}
        out = pkg / "SYNC_RECORD.json"
        out.write_text(json.dumps(record, indent=2) + "\n")
        print("wrote", out)


if __name__ == "__main__":
    main()
