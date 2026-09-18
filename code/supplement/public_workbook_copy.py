"""Make the public copy of the analysis workbook (27_ANALYSIS_WORKBOOK.xlsx), added 2026-09-18.

The researcher's workbook pairs each flagged timing item (T02, T04, T16, T24) with its condition in the
Timing sheet. Timing-item assignments are masked, so every cell whose whole value is a timing-item ID
is replaced with "1 (ID withheld)". Everything else is copied unchanged, including formatting and charts.
The script refuses to write a copy that still contains a reviewer name, an absolute local path or an
API-key-like string.

Usage:  python3 -B code/supplement/public_workbook_copy.py <source.xlsx> results/27_ANALYSIS_WORKBOOK.xlsx
Afterwards run:  python3 -B code/verify_hashes.py --write-manifest
"""
import hashlib, re, sys, zipfile
from pathlib import Path

CELL = re.compile(r'(<c r="[A-Z]+\d+"[^>]*><is><t[^>]*>)T\d\d(</t></is></c>)')
SHARED = re.compile(r'(<si><t[^>]*>)T\d\d(</t></si>)')
# Private terms (for example reviewer names) are read from a git-ignored local file, never stored here.
_TERMS = Path(__file__).resolve().parents[2] / 'local-only' / 'forbidden_terms.txt'
_PRIVATE = [re.escape(t.strip()) for t in (_TERMS.read_text().splitlines() if _TERMS.exists() else []) if t.strip()]
FORBIDDEN = re.compile('|'.join(_PRIVATE + [r'sk-or-', r'sk-[A-Za-z0-9]{24,}', re.escape(str(Path.home()))]))


def main(src, dst):
    n = 0
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename.endswith('.xml'):
                text = data.decode('utf-8')
                if info.filename.startswith('xl/worksheets/') or info.filename == 'xl/sharedStrings.xml':
                    text, k1 = CELL.subn(r'\g<1>1 (ID withheld)\g<2>', text)
                    text, k2 = SHARED.subn(r'\g<1>1 (ID withheld)\g<2>', text)
                    n += k1 + k2
                if FORBIDDEN.search(text):
                    raise SystemExit(f'Refusing: forbidden content in {info.filename}')
                data = text.encode('utf-8')
            zout.writestr(info, data)
    print(f'Replaced {n} timing-item cells.')
    print('source SHA-256', hashlib.sha256(Path(src).read_bytes()).hexdigest())
    print('public SHA-256', hashlib.sha256(Path(dst).read_bytes()).hexdigest())


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
