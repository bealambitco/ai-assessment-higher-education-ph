"""Verify file integrity for the public repository (standard library only).

1. Frozen record: every non-private file listed in benchmark/freeze/ORIGINAL_FREEZE_MANIFEST.json
   (frozen September 15, 2026) is found at its new path (benchmark/freeze/frozen_path_map.json)
   with the recorded SHA-256. Expected: 88 of 88 match; 4 private assignment files withheld.
2. Release manifest: every file listed in benchmark/MANIFEST_SHA256.json matches its SHA-256.

Optional:
  --write-manifest regenerate benchmark/MANIFEST_SHA256.json (run only after an intended change to a
                   file in benchmark/, code/frozen_2026-09-15/, results/ or extensions/; record it in CHANGELOG.md)
  --assemble DIR   copy the 88 public frozen files back into the original frozen layout
                   (code/, inputs/, references/, prompts/, protocol/) so the frozen modules can be
                   imported as they were run. Commands that call assert_frozen() still need the four
                   withheld private files and will stop; that is intended.

Run from the repository root:  python3 -B code/verify_hashes.py
"""
import argparse, datetime, hashlib, json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOPE = ('benchmark', 'code/frozen_2026-09-15', 'results', 'extensions')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--assemble'); ap.add_argument('--write-manifest', action='store_true'); a = ap.parse_args()
    if a.write_manifest:
        files = {}
        for top in SCOPE:
            for p in sorted((ROOT / top).rglob('*')):
                if p.is_file() and p.name not in ('MANIFEST_SHA256.json', '.DS_Store') and '__pycache__' not in p.parts:
                    files[p.relative_to(ROOT).as_posix()] = sha(p)
        (ROOT / 'benchmark/MANIFEST_SHA256.json').write_text(json.dumps(
            {'generated': datetime.date.today().isoformat(), 'algorithm': 'SHA-256',
             'scope': ', '.join(t + '/' for t in SCOPE) + ' (all files except this manifest)', 'files': files}, indent=1) + '\n')
        print(f'Wrote benchmark/MANIFEST_SHA256.json ({len(files)} files)')
    freeze = json.loads((ROOT / 'benchmark/freeze/ORIGINAL_FREEZE_MANIFEST.json').read_text())['sha256']
    pmap = json.loads((ROOT / 'benchmark/freeze/frozen_path_map.json').read_text())['map']
    ok, bad, withheld = 0, [], []
    for old, digest in freeze.items():
        if old.startswith('private/'):
            withheld.append(old); continue
        new = ROOT / pmap[old]
        if new.exists() and sha(new) == digest:
            ok += 1
        else:
            bad.append(old)
    public = len(freeze) - len(withheld)
    print(f'Frozen record: {ok} of {public} public frozen files match; {len(withheld)} private files withheld: {", ".join(withheld)}')
    for b in bad:
        print('  MISMATCH or missing:', b, '->', pmap.get(b))

    man = json.loads((ROOT / 'benchmark/MANIFEST_SHA256.json').read_text())['files']
    mbad = [p for p, d in man.items() if not (ROOT / p).exists() or sha(ROOT / p) != d]
    print(f'Release manifest: {len(man) - len(mbad)} of {len(man)} files match')
    for b in mbad:
        print('  MISMATCH or missing:', b)

    if a.assemble:
        dst = Path(a.assemble)
        for old in freeze:
            if old.startswith('private/'):
                continue
            (dst / old).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / pmap[old], dst / old)
        (dst / 'freeze.json').write_text(json.dumps({'sha256': freeze}, indent=1))
        print(f'Assembled {public} frozen files in the original layout at {dst}')
    sys.exit(1 if bad or mbad else 0)


if __name__ == '__main__':
    main()
