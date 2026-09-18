"""Read-only completeness check for the 96 Markdown scoring forms (Package 22 proposal).

It never writes to Package 21 and never opens private/ files. It reports, per form,
what would make the frozen `score_lock` reject it, so the researcher can fix forms
before synchronisation:

  * blank Status, criterion Judgment, Severity or Acceptable
  * a completion time that cannot be read as a Manila (+08:00) timestamp (free text that can be
    read is accepted with a note and converted during synchronisation)
  * Severity or Acceptable = "Cannot judge" while Status = SCORED (lock rejects this;
    use Status CANNOT_JUDGE instead)
  * Acceptable = Yes together with Major/Critical severity or any "Cannot judge" criterion

Usage:
    python3 check_scoring_forms.py --materials "<21_.../scoring/materials>" [--case-order]

--case-order prints a case-grouped scoring order (case IDs only; no model, repetition
or pathway information) for the optional case-block amendment described in 05.
"""
import argparse, json, re
from datetime import datetime, timedelta, timezone
from pathlib import Path

MANILA = timezone(timedelta(hours=8))
FIELD = lambda name: re.compile(rf'^{name}[^:\n]*:[ \t]*(.*)$', re.M)


def parse_time(text, default_year=2026):
    """Accept ISO 8601, or 'September 17, 12:55 PM - 1:01 PM' style (end time used)."""
    t = text.strip()
    if not t:
        return None, 'completion time blank'
    try:
        d = datetime.fromisoformat(t)
        if 'T' not in t and ' ' not in t:
            return None, f'date without a time: {t!r}'
        if d.tzinfo is None:
            return d.replace(tzinfo=MANILA), 'free-text: ISO time without offset interpreted as +08:00; confirm'
        return d, None
    except ValueError:
        pass
    m = re.match(r'([A-Za-z]+)\s+(\d{1,2})(?:,\s*(\d{4}))?[,\s]+(?:.*?-\s*)?(\d{1,2}:\d{2}\s*[AP]M)', t, re.I)
    if m:
        month, day, year, clock = m.groups()
        start = re.search(r'(\d{1,2}:\d{2})\s*([AP]M)\s*-', t, re.I)
        if start and start.group(2).upper() == 'PM' and clock.upper().endswith('AM'):
            return None, f'time range crosses midnight; enter ISO 8601: {t!r}'
        try:
            d = datetime.strptime(f'{month} {day} {year or default_year} {clock.upper().replace(" ", "")}', '%B %d %Y %I:%M%p')
            return d.replace(tzinfo=MANILA), 'free-text time interpreted as Asia/Manila; confirm'
        except ValueError:
            pass
    return None, f'unreadable completion time: {t!r}'


def check_form(path):
    text = path.read_text()
    issues = []
    status = (FIELD('Status').search(text) or [None, ''])[1].strip().upper()
    when = (FIELD('Actual scoring completed at').search(text) or [None, ''])[1]
    severity = (FIELD('Severity').search(text) or [None, ''])[1].strip()
    acceptable = (FIELD('Acceptable').search(text) or [None, ''])[1].strip()
    judgments = [j.strip() for j in re.findall(r'^Judgment[^:\n]*:[ \t]*(.*)$', text, re.M)]
    started = bool(severity or acceptable or any(judgments) or status)
    if not started:
        return {'form': path.name, 'state': 'NOT_STARTED', 'issues': []}
    if status not in ('SCORED', 'MISSING', 'CANNOT_JUDGE'):
        issues.append('Status blank or invalid (use SCORED, MISSING or CANNOT_JUDGE)')
    warnings = []
    if status in ('MISSING', 'CANNOT_JUDGE'):
        # Addendum D2: an unresolved answer needs a reason, not a severity/acceptability label.
        reason = ''.join((FIELD(n).search(text) or [None, ''])[1].strip() for n in ('Other comments', 'Source or reference concern'))
        if not reason or reason.lower() in ('none', 'n/a', 'none.'):
            issues.append(f'{status} needs a reason in Other comments')
        return {'form': path.name, 'state': 'READY' if not issues else 'NEEDS_FIX', 'issues': issues, 'warnings': warnings, 'iso_time': None}
    ts, note = parse_time(when)
    if note and note.startswith('free-text'):
        warnings.append(note)
    elif note:
        issues.append(note)
    valid_j = {'correct', 'incorrect', 'incomplete', 'cannot judge'}
    for i, j in enumerate(judgments, 1):
        if j.lower() not in valid_j:
            issues.append(f'criterion {i} judgment blank or invalid')
    if severity.lower() not in {'none', 'minor', 'major', 'critical', 'cannot judge'}:
        issues.append('Severity blank or invalid')
    if acceptable.lower() not in {'yes', 'no', 'cannot judge'}:
        issues.append('Acceptable blank or invalid')
    if status == 'SCORED' and ('cannot judge' in (severity.lower(), acceptable.lower())):
        issues.append('SCORED with Cannot judge severity/acceptable: lock will reject; use Status CANNOT_JUDGE')
    if acceptable.lower() == 'yes' and (severity.lower() in ('major', 'critical') or any(j.lower() == 'cannot judge' for j in judgments)):
        issues.append('Acceptable Yes conflicts with Major/Critical severity or an unresolved criterion')
    return {'form': path.name, 'state': 'READY' if not issues else 'NEEDS_FIX', 'issues': issues,
            'warnings': warnings, 'iso_time': ts.isoformat() if ts else None}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--materials', required=True); ap.add_argument('--case-order', action='store_true')
    a = ap.parse_args(); folder = Path(a.materials)
    results = [check_form(p) for p in sorted(folder.glob('R*_review.md'))]
    counts = {s: sum(r['state'] == s for r in results) for s in ['READY', 'NEEDS_FIX', 'NOT_STARTED']}
    print(json.dumps(counts))
    for r in results:
        if r['state'] == 'NEEDS_FIX':
            print(f"{r['form']}: " + '; '.join(r['issues'] + r.get('warnings', [])))
        elif r.get('warnings'):
            print(f"{r['form']} (ready, note): " + '; '.join(r['warnings']) + f" -> {r['iso_time']}")
    if a.case_order:
        import random
        scores = json.loads((folder.parent / 'researcher_scores.json').read_text())
        rng = random.Random(2026091701)  # frozen scoring seed from the registration record
        by_wf = {}
        for cid in sorted({s['case_id'] for s in scores}):
            by_wf.setdefault(cid[:2], []).append(cid)
        for cases in by_wf.values():
            rng.shuffle(cases)
        order, queues = [], [by_wf[w] for w in sorted(by_wf)]
        while any(queues):  # interleave workflows W1, W2, W3, W1, ... so a partial stop keeps all three
            for q in queues:
                if q:
                    order.append(q.pop(0))
        print('\nCase-grouped order (seed 2026091701, workflows interleaved; case and masked IDs only):')
        for cid in order:
            ids = sorted(s['masked_id'] for s in scores if s['case_id'] == cid)
            rng.shuffle(ids)
            for mid in ids:
                print(f"{cid}  {mid}")

if __name__ == '__main__':
    main()
