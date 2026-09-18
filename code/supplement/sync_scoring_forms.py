"""Synchronise the researcher's Markdown scoring forms into researcher_scores.json (Package 22 proposal).

Transcription only: every value comes verbatim from the researcher's forms. Nothing is inferred
or corrected. Free-text times are converted to ISO 8601 in Asia/Manila (+08:00) and every
conversion is logged. Forms that are not yet complete are left unchanged as PENDING unless
--mark-missing is given at the cutoff.

Default is a DRY RUN that prints counts only. Writing requires --write, which first saves a
timestamped backup of the existing score file next to it, then writes the synced file.

    python3 sync_scoring_forms.py --scoring "<21_.../scoring>"                  # dry run
    python3 sync_scoring_forms.py --scoring "<21_.../scoring>" --write          # sync complete forms
    python3 sync_scoring_forms.py --scoring "<21_.../scoring>" --write --mark-missing "not scored by the submission cutoff"
"""
import argparse, json, re, shutil
from datetime import datetime
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_scoring_forms import check_form, parse_time, FIELD  # noqa: E402

ACCEPT = {'yes': True, 'no': False, 'cannot judge': None}
SEV = {'none': 'None', 'minor': 'Minor', 'major': 'Major', 'critical': 'Critical', 'cannot judge': None}
JUD = {'correct': 'Correct', 'incorrect': 'Incorrect', 'incomplete': 'Incomplete', 'cannot judge': 'Cannot judge'}


def parse_form(path):
    text = path.read_text()
    blocks = re.split(r'^## Criterion\s+', text, flags=re.M)[1:]
    criteria = []
    for b in blocks:
        cid = b.split('\n', 1)[0].strip()
        j = re.search(r'^Judgment[^:\n]*:[ \t]*(.*)$', b, re.M)
        ev = re.search(r'^Response evidence and brief reason:[ \t]*(.*?)(?=^## |\Z)', b, re.M | re.S)
        criteria.append({'criterion': int(cid) if cid.isdigit() else cid,
                         'judgment': JUD.get((j.group(1) if j else '').strip().lower()),
                         'response_evidence': (ev.group(1).strip() if ev else ''), 'reason': ''})
    get = lambda name: (FIELD(name).search(text) or [None, ''])[1].strip()
    return {'status': get('Status').upper(), 'time': get('Actual scoring completed at'),
            'severity': get('Severity'), 'acceptable': get('Acceptable'),
            'concern': get('Source or reference concern'), 'comments': get('Other comments'),
            'criteria': criteria}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scoring', required=True)
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--mark-missing', default=None, help='reason text; marks every not-started or incomplete form MISSING')
    ap.add_argument('--materials-dir', default='materials')
    ap.add_argument('--scores-name', default='researcher_scores.json')
    a = ap.parse_args()
    folder = Path(a.scoring); target = folder / a.scores_name
    lock_name = 'score_lock.json' if a.scores_name == 'researcher_scores.json' else a.scores_name.replace('_scores.json', '_score_lock.json')
    scores = json.loads(target.read_text())
    if (folder / lock_name).exists():
        raise SystemExit('Scores already locked; refusing to change them.')
    log, counts = [], {'synced': 0, 'left_pending': 0, 'marked_missing': 0}
    for row in scores:
        form = folder / a.materials_dir / f"{row['masked_id']}_review.md"
        check = check_form(form)
        if check['state'] != 'READY' and row.get('status') in ('SCORED', 'CANNOT_JUDGE'):
            raise SystemExit(f"{row['masked_id']}: already synced as {row['status']} but the form is now {check['state']}; "
                             'fix the form before syncing (the old values would otherwise be locked silently)')
        if check['state'] != 'READY':
            if a.mark_missing:
                row.update({'status': 'MISSING', 'severity': None, 'acceptable': None,
                            'reference_challenge': row.get('reference_challenge', ''),
                            'missing_reason': a.mark_missing})
                counts['marked_missing'] += 1; log.append({'masked_id': row['masked_id'], 'action': 'MISSING', 'form_issues': check['issues']})
            else:
                counts['left_pending'] += 1
            continue
        f = parse_form(form)
        if f['status'] in ('MISSING', 'CANNOT_JUDGE'):
            row.update({'status': f['status'], 'severity': None, 'acceptable': None,
                        'missing_reason' if f['status'] == 'MISSING' else 'cannot_judge_reason': f['comments'] or f['concern']})
            counts['synced'] += 1
            continue
        ts, note = parse_time(f['time'])
        if note:
            log.append({'masked_id': row['masked_id'], 'time_conversion': {'from': f['time'], 'to': ts.isoformat()}})
        by_id = {c['criterion']: c for c in f['criteria']}
        for c in row['criteria']:
            src = by_id.get(c['criterion'])
            if src is None:
                raise SystemExit(f"{row['masked_id']}: criterion {c['criterion']} missing from form")
            c.update({'judgment': src['judgment'], 'response_evidence': src['response_evidence']})
        concern = f['concern'] if f['concern'].strip().lower() not in ('', 'none', 'n/a', 'none.') else ''
        row.update({'status': f['status'], 'scored_at': ts.isoformat(),
                    'severity': SEV[f['severity'].lower()] if f['status'] == 'SCORED' else SEV.get(f['severity'].lower()),
                    'acceptable': ACCEPT[f['acceptable'].lower()] if f['status'] == 'SCORED' else ACCEPT.get(f['acceptable'].lower()),
                    'reference_challenge': concern, 'researcher_comments': f['comments']})
        counts['synced'] += 1
    print(json.dumps(counts))
    if a.write:
        stamp = datetime.now().strftime('%Y%m%dT%H%M%S')
        shutil.copy2(target, folder / f"{target.stem}.backup_{stamp}.json")
        target.write_text(json.dumps(scores, ensure_ascii=False, indent=2) + '\n')
        (folder / f'SYNC_LOG_{stamp}.json').write_text(json.dumps({'counts': counts, 'log': log}, ensure_ascii=False, indent=2))
        print('Written with backup and log.')
    else:
        print('Dry run only. Add --write to update researcher_scores.json (a backup is kept).')


if __name__ == '__main__':
    main()
