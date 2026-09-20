"""Keep the local round-2 package and the public repository copy in step, local first.

The working package is the local one, beside packages 21 to 29. The repository holds only the publishable
subset: protocol, specifications, code, document map, aggregate results and reviewer materials. Prompts,
bundles, raw replies, per-answer tables, packets and score files stay local.

  python3 -B code/extensions/round2/sync_local_and_repo.py --package "<...>/30_ROUND2_EXTENSION" --check
  python3 -B code/extensions/round2/sync_local_and_repo.py --package "<...>/30_ROUND2_EXTENSION" --to-local
  python3 -B code/extensions/round2/sync_local_and_repo.py --package "<...>/30_ROUND2_EXTENSION" --to-repo

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
    "extensions/v2/README.md": "00_README.md",
    "extensions/v2/PROTOCOL.md": "01_PROTOCOL/PROTOCOL.md",
    "extensions/v2/DEVIATIONS.md": "01_PROTOCOL/DEVIATIONS.md",
    "extensions/v2/CHECKS_V2_SPEC.md": "01_PROTOCOL/CHECKS_V2_SPEC.md",
    "extensions/v2/RUN_COMMANDS.md": "01_PROTOCOL/RUN_COMMANDS.md",
    "extensions/v2/confirmed_errors.json": "01_PROTOCOL/confirmed_errors.json",
    "extensions/v2/scoring/ORDER.md": "02_SCORING/ORDER.md",
    "extensions/v2/scoring/FAILURE_CLASSES.md": "02_SCORING/FAILURE_CLASSES.md",
    "extensions/v2/scoring/HOW_TO_SCORE.md": "02_SCORING/HOW_TO_SCORE.md",
    "extensions/v2/documents/README.md": "03_DOCUMENTS/README.md",
    "extensions/v2/documents/DOCUMENT_MAP.json": "03_DOCUMENTS/DOCUMENT_MAP.json",
    "extensions/v2/rule-discovery/CASES.md": "04_RULE_DISCOVERY/CASES.md",
    "extensions/v2/access-arm/MODELS.md": "05_ACCESS_ARM/MODELS.md",
    "extensions/v2/key-review/README.md": "06_KEY_REVIEW/README.md",
    "extensions/v2/key-review/PACKETS.md": "06_KEY_REVIEW/PACKETS.md",
    "extensions/v2/key-review/REVIEWER_INSTRUCTIONS.md": "06_KEY_REVIEW/REVIEWER_INSTRUCTIONS.md",
    "extensions/v2/second-timer/README.md": "07_SECOND_TIMER/README.md",
    "extensions/v2/second-timer/TIMER_INSTRUCTIONS.md": "07_SECOND_TIMER/TIMER_INSTRUCTIONS.md",
    "extensions/v2/second-timer/SESSION_CHECKLIST.md": "07_SECOND_TIMER/SESSION_CHECKLIST.md",
    "extensions/v2/results/EXTENSION_ARMS_FINDINGS.md": "08_RESULTS_PUBLIC/EXTENSION_ARMS_FINDINGS.md",
    "extensions/v2/results/access_summary.csv": "08_RESULTS_PUBLIC/access_summary.csv",
    "extensions/v2/results/documents_summary.csv": "08_RESULTS_PUBLIC/documents_summary.csv",
    "extensions/v2/results/discovery_summary.csv": "08_RESULTS_PUBLIC/discovery_summary.csv",
    "results/Analysis_Workbook_Extension.xlsx": "analysis/Analysis_Workbook_Extension.xlsx",
    "extensions/v2/results/CHECKS_V2_FINDINGS.md": "08_RESULTS_PUBLIC/CHECKS_V2_FINDINGS.md",
    "extensions/v2/results/checks_v2_decisions_by_model.csv": "08_RESULTS_PUBLIC/checks_v2_decisions_by_model.csv",
    "extensions/v2/results/checks_v2_effect_by_outcome.csv": "08_RESULTS_PUBLIC/checks_v2_effect_by_outcome.csv",
    "extensions/v2/results/checks_v2_changes_public.csv": "08_RESULTS_PUBLIC/checks_v2_changes_public.csv",
    "extensions/v2/results/checks_v2_run_record.json": "08_RESULTS_PUBLIC/checks_v2_run_record.json",
}
CODE = ["build_extension_workbook.py", "checks_v2.py", "rerun_checks.py", "freeze_round2.py", "prepare_round2.py", "run_openrouter.py",
        "parse_round2.py", "score_round2.py", "timing_round2.py", "key_review_packets.py",
        "key_review_intake.py", "sync_local_and_repo.py"]
TESTS = ["test_checks_v2.py", "test_score_round2.py", "test_timing_round2.py"]
for name in CODE:
    MAP[f"code/extensions/round2/{name}"] = f"09_CODE/{name}"
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
