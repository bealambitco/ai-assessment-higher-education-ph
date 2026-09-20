"""Hash the round-2 materials and verify them against the freeze record in extensions/v2/PROTOCOL.md.

  python3 -B code/extensions/round2/freeze_round2.py            # print the table
  python3 -B code/extensions/round2/freeze_round2.py --verify   # compare with the protocol, exit 1 on drift
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FILES = [
    "extensions/v2/CHECKS_V2_SPEC.md",
    "code/extensions/round2/checks_v2.py",
    "code/tests/test_checks_v2.py",
    "code/extensions/round2/rerun_checks.py",
    "extensions/v2/confirmed_errors.json",
]
PROTOCOL = ROOT / "extensions/v2/PROTOCOL.md"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def recorded():
    out = {}
    for name, digest in re.findall(r"\|\s*`([^`]+)`\s*\|\s*`([0-9a-f]{64})`\s*\|", PROTOCOL.read_text()):
        out[name] = digest
    return out


def main():
    verify = "--verify" in sys.argv
    table, drift = [], []
    known = recorded()
    for name in FILES:
        actual = sha256(ROOT / name)
        table.append((name, actual))
        if verify:
            want = known.get(name)
            if want is None:
                drift.append(f"{name}: not in the freeze record")
            elif want != actual:
                drift.append(f"{name}: recorded {want[:12]}…, actual {actual[:12]}…")
    for name, digest in table:
        print(f"| `{name}` | `{digest}` |")
    if verify:
        if drift:
            print("\nFREEZE DRIFT")
            for d in drift:
                print(" -", d)
            sys.exit(1)
        print(f"\n{len(FILES)} of {len(FILES)} round-2 files match the freeze record.")


if __name__ == "__main__":
    main()
