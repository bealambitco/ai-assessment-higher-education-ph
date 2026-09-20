"""Read returned answer-key review packets and write a tidy CSV plus a disagreement summary.

Standard library plus python-docx. No network calls. Nothing is adjudicated or rewritten here:
every judgment is recorded as the reviewer left it, and blanks stay blank.

Answers are read from the Word content controls by their tag, not by the wording printed beside
them, so the packet design can change without breaking intake. Each answer field sits inline in
its own paragraph, after a bold question. If a reviewer's Word cannot drive the dropdown and they
type the option beside the field instead -- the fallback the packet tells them to use -- the typed
text in the same paragraph is read.

The reviewer's typed name is deliberately not copied into the CSV. Each packet is identified by
its file name, so returns can be compared without publishing anyone's name.

Usage:
  python3 -B code/extensions/review/key_review_intake.py --packets DIR --out DIR
  python3 -B code/extensions/review/key_review_intake.py --packets a.docx b.docx --out DIR
"""
from pathlib import Path
import argparse, csv, re, sys

from docx import Document
from docx.oxml.ns import qn

CRITERION_OPTIONS = ['Correct', 'Incorrect', 'Unclear', 'Out of scope']
LOCATOR_OPTIONS = ['Yes', 'No', 'Cannot tell']
ACCEPT_OPTIONS = ['Yes', 'Yes with changes', 'No']
UNANSWERED = ['', 'choose an answer', 'type here']

# Field tags written by key_review_packets.py.
CRITERION_TAG = re.compile(r'^([A-Za-z]\d+-\d+)_C(\d+)_(JUDGMENT|LOCATOR|COMMENT)$')
OVERALL_TAG = re.compile(r'^([A-Za-z]\d+-\d+)_(ACCEPT|ACCEPT_WHY|RULE_VERSION)$')
# Cover fields carry the reviewer's own name and are never copied into the CSV.
COVER_TAG = re.compile(r'^COVER_|^SESSION_|^ACKNOWLEDGMENT$')

FIELDS = ['packet', 'case', 'criterion', 'judgment', 'locator_judgment', 'comment']


# ---------------------------------------------------------------- reading a packet

def node_text(node):
    """All text under an element, including text inside Word content controls."""
    parts = [child.text or '' for child in node.iter(qn('w:t'))]
    return re.sub(r'[ \t]+', ' ', ''.join(parts)).strip()


def answers_in(document):
    """Yield (tag, value) for every content control in the document, in document order.

    value is what the control holds. When the control still shows its placeholder and the
    reviewer typed beside it instead, the text typed in the same paragraph is returned.
    """
    for paragraph in document.element.body.iter(qn('w:p')):
        children = list(paragraph)
        for index, child in enumerate(children):
            if child.tag != qn('w:sdt'):
                continue
            props = child.find(qn('w:sdtPr'))
            tag_node = props.find(qn('w:tag')) if props is not None else None
            tag = tag_node.get(qn('w:val')) if tag_node is not None else None
            if not tag:
                continue
            content = child.find(qn('w:sdtContent'))
            value = node_text(content) if content is not None else ''
            if value.lower() in UNANSWERED:
                beside = ' '.join(node_text(sibling) for sibling in children[index + 1:]
                                  if sibling.tag != qn('w:sdt')).strip()
                if beside:
                    value = beside
            yield tag, value


def normalise(value, options):
    """Return (clean value, note). An unrecognised answer is kept verbatim and flagged."""
    text = (value or '').strip()
    if text.lower() in UNANSWERED:
        return '', None
    for option in options:
        if text.lower() == option.lower():
            return option, None
    return text, 'unrecognised answer: %r' % text


def read_packet(path):
    """Return (records, problems). A partly filled or malformed packet still returns what it has."""
    problems = []
    packet = path.stem
    try:
        document = Document(str(path))
    except Exception as error:                                  # unreadable or not a .docx
        return [], ['%s: cannot be read as a Word file (%s)' % (path.name, error)]

    # {(case, criterion): record}, kept in first-seen order so the packet's own order survives.
    criteria, overall, seen_field = {}, {}, False
    for tag, value in answers_in(document):
        if COVER_TAG.match(tag):
            seen_field = True
            continue
        match = CRITERION_TAG.match(tag)
        if match:
            seen_field = True
            case_id, number, which = match.group(1).upper(), match.group(2), match.group(3)
            record = criteria.setdefault((case_id, number), {
                'packet': packet, 'case': case_id, 'criterion': number,
                'judgment': '', 'locator_judgment': '', 'comment': ''})
            if which == 'JUDGMENT':
                record['judgment'], note = normalise(value, CRITERION_OPTIONS)
                if note:
                    problems.append('%s: case %s criterion %s %s' %
                                    (path.name, case_id, number, note))
            elif which == 'LOCATOR':
                record['locator_judgment'], note = normalise(value, LOCATOR_OPTIONS)
                if note:
                    problems.append('%s: case %s criterion %s locator %s' %
                                    (path.name, case_id, number, note))
            else:
                record['comment'], _ = normalise(value, [])
            continue

        match = OVERALL_TAG.match(tag)
        if match:
            seen_field = True
            case_id, which = match.group(1).upper(), match.group(2)
            record = overall.setdefault(case_id, {'accept': '', 'why': '', 'rule': ''})
            if which == 'ACCEPT':
                record['accept'], note = normalise(value, ACCEPT_OPTIONS)
                if note:
                    problems.append('%s: case %s overall %s' % (path.name, case_id, note))
            elif which == 'ACCEPT_WHY':
                record['why'], _ = normalise(value, [])
            else:
                record['rule'], _ = normalise(value, [])
            continue

        problems.append('%s: unknown answer field %r' % (path.name, tag))

    records = list(criteria.values())
    for case_id, record in overall.items():
        records.append({'packet': packet, 'case': case_id, 'criterion': 'overall',
                        'judgment': record['accept'], 'locator_judgment': '',
                        'comment': record['why']})
        records.append({'packet': packet, 'case': case_id, 'criterion': 'rule_version_concern',
                        'judgment': '', 'locator_judgment': '', 'comment': record['rule']})

    if not records:
        problems.append('%s: no answer-key review fields found%s' %
                        (path.name, ' (only cover fields)' if seen_field else ''))
    return records, problems


def collect_paths(inputs):
    paths, problems = [], []
    for item in inputs:
        path = Path(item)
        if path.is_dir():
            found = sorted(p for p in path.glob('*.docx') if not p.name.startswith('~$'))
            if not found:
                problems.append('%s: directory holds no .docx files' % path)
            paths.extend(found)
        elif path.exists():
            paths.append(path)
        else:
            problems.append('%s: file not found' % path)
    return paths, problems


# ---------------------------------------------------------------- summarising

def sort_key(record):
    number = record['criterion']
    order = (0, int(number)) if number.isdigit() else (1, 0)
    return (record['case'], order, record['criterion'], record['packet'])


def disagreements(records):
    """One row per point where the returns differ, or where a criterion was challenged."""
    grouped = {}
    for record in records:
        grouped.setdefault((record['case'], record['criterion']), []).append(record)
    out = []
    for (case_id, criterion), group in sorted(grouped.items(), key=lambda kv: sort_key(kv[1][0])):
        for field, label in [('judgment', 'criterion judgment'),
                             ('locator_judgment', 'locator judgment')]:
            answers = {r['packet']: r[field] for r in group if r[field]}
            if len(set(answers.values())) > 1:
                out.append({'case': case_id, 'criterion': criterion, 'field': label,
                            'kind': 'disagreement',
                            'answers': '; '.join('%s=%s' % kv for kv in sorted(answers.items())),
                            'comments': ' || '.join(
                                '%s: %s' % (r['packet'], r['comment']) for r in sorted(
                                    group, key=lambda r: r['packet']) if r['comment'])})
        challenged = {r['packet']: r['judgment'] for r in group
                      if r['judgment'] and r['judgment'] != 'Correct' and criterion.isdigit()}
        if challenged:
            out.append({'case': case_id, 'criterion': criterion, 'field': 'criterion judgment',
                        'kind': 'challenged',
                        'answers': '; '.join('%s=%s' % kv for kv in sorted(challenged.items())),
                        'comments': ' || '.join(
                            '%s: %s' % (r['packet'], r['comment']) for r in sorted(
                                group, key=lambda r: r['packet']) if r['comment'])})
        locator_doubt = {r['packet']: r['locator_judgment'] for r in group
                         if r['locator_judgment'] and r['locator_judgment'] != 'Yes'}
        if locator_doubt:
            out.append({'case': case_id, 'criterion': criterion, 'field': 'locator judgment',
                        'kind': 'locator concern',
                        'answers': '; '.join('%s=%s' % kv for kv in sorted(locator_doubt.items())),
                        'comments': ''})
        if criterion == 'overall':
            not_accepted = {r['packet']: r['judgment'] for r in group
                            if r['judgment'] and r['judgment'] != 'Yes'}
            if not_accepted:
                out.append({'case': case_id, 'criterion': 'overall', 'field': 'overall acceptance',
                            'kind': 'challenged',
                            'answers': '; '.join('%s=%s' % kv for kv in sorted(not_accepted.items())),
                            'comments': ' || '.join(
                                '%s: %s' % (r['packet'], r['comment']) for r in sorted(
                                    group, key=lambda r: r['packet']) if r['comment'])})
    return out


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Intake returned answer-key review packets.')
    parser.add_argument('--packets', nargs='+', required=True,
                        help='Returned .docx files, or a directory holding them.')
    parser.add_argument('--out', required=True, type=Path, help='Directory for the CSV files.')
    args = parser.parse_args(argv)

    paths, problems = collect_paths(args.packets)
    records = []
    for path in paths:
        found, issues = read_packet(path)
        records.extend(found)
        problems.extend(issues)
    records.sort(key=sort_key)

    responses_csv = args.out / 'key_review_responses.csv'
    disagreements_csv = args.out / 'key_review_disagreements.csv'
    conflicts = disagreements(records)
    write_csv(responses_csv, FIELDS, records)
    write_csv(disagreements_csv, ['case', 'criterion', 'field', 'kind', 'answers', 'comments'], conflicts)

    criterion_rows = [r for r in records if r['criterion'].isdigit()]
    answered = [r for r in criterion_rows if r['judgment']]
    packets = sorted({r['packet'] for r in records})
    cases = sorted({r['case'] for r in records})

    print('Answer-key review intake')
    print('  packets read: %d (%s)' % (len(packets), ', '.join(packets) or 'none'))
    print('  cases seen:   %d (%s)' % (len(cases), ', '.join(cases) or 'none'))
    print('  criterion judgments: %d answered, %d left blank' %
          (len(answered), len(criterion_rows) - len(answered)))
    counts = {}
    for record in answered:
        counts[record['judgment']] = counts.get(record['judgment'], 0) + 1
    for option in CRITERION_OPTIONS:
        if counts.get(option):
            print('    %-12s %d' % (option, counts[option]))
    other = {k: v for k, v in counts.items() if k not in CRITERION_OPTIONS}
    for key, value in sorted(other.items()):
        print('    %-12s %d  (not one of the listed answers)' % (key, value))
    print('  rows written: %d -> %s' % (len(records), responses_csv))
    print('  disagreement and challenge rows: %d -> %s' % (len(conflicts), disagreements_csv))
    kinds = {}
    for row in conflicts:
        kinds[row['kind']] = kinds.get(row['kind'], 0) + 1
    for kind, count in sorted(kinds.items()):
        print('    %-16s %d' % (kind, count))
    if len(packets) < 2:
        print('  Fewer than two packets were read, so no agreement between reviewers can be described.')
    if problems:
        print('  Problems (%d):' % len(problems))
        for problem in problems:
            print('    - %s' % problem)
    print('Nothing was adjudicated or rewritten. Reviewer names were not copied into the CSV.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
