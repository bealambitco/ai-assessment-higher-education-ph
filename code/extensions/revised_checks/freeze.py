"""Hash the extension materials and verify them against the freeze record in docs/extension-protocol.md.

  python3 -B code/extensions/revised_checks/freeze.py            # print the table
  python3 -B code/extensions/revised_checks/freeze.py --verify   # compare with the protocol, exit 1 on drift
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FILES = [
    "extensions/revised-checks/SPECIFICATION.md",
    "code/extensions/revised_checks/checks.py",
    "code/tests/test_revised_checks.py",
    "code/extensions/revised_checks/rerun.py",
    "extensions/revised-checks/confirmed-errors.json",
]
PROTOCOL = ROOT / "docs/extension-protocol.md"


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
        print(f"\n{len(FILES)} of {len(FILES)} extension files match the freeze record.")


if __name__ == "__main__":
    main()
