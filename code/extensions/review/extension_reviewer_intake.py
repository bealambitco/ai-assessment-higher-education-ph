"""Read returned extension reviewer packets and write a tidy CSV plus a disagreement summary.

Standard library plus python-docx. No network calls. Nothing is adjudicated or rewritten here:
every judgment is recorded as the reviewer left it, and blanks stay blank.

Answers are read from the Word content controls by their tag, not by the wording printed beside
them, so the packet design can change without breaking intake. Each answer field sits inline in
its own paragraph, after a bold question. If a reviewer's Word cannot drive the dropdown and they
type the option beside the field instead -- the fallback the packet tells them to use -- the typed
text in the same paragraph is read.

The reviewer's typed name is deliberately not copied into the CSV. Each packet is identified by
its file name, and each response by the masked id printed in the packet, so returns can be
compared without publishing anyone's name and without naming a model.

The two anchor responses appear in every packet, so the summary reports agreement on them
separately. That is the only reviewer-to-reviewer agreement these returns can support.

Usage:
  python3 -B code/extensions/review/extension_reviewer_intake.py --packets DIR --out DIR
  python3 -B code/extensions/review/extension_reviewer_intake.py --packets a.docx b.docx --out DIR
"""
from pathlib import Path
import argparse, csv, re, sys

from docx import Document
from docx.oxml.ns import qn

JUDGMENTS = ['Correct', 'Incorrect', 'Incomplete', 'Cannot judge']
SEVERITIES = ['None', 'Minor', 'Major', 'Critical', 'Cannot judge']
CONCERNS = ['None identified', 'Concern needs review']
ENOUGH = ['Yes', 'No, some criteria needed the full document', 'Cannot tell']
UNANSWERED = ['', 'choose an answer', 'type here']

# Field tags written by extension_reviewer_packets.py.
CRITERION_TAG = re.compile(r'^(E\d{3})_C(\d+)$')
OVERALL_TAG = re.compile(r'^(E\d{3})_(SEVERITY|EVIDENCE_ENOUGH|REFERENCE_CONCERN|COMMENT)$')
# Cover fields carry the reviewer's own name and are never copied into the CSV.
COVER_TAG = re.compile(r'^SESSION_|^COVER_|^ACKNOWLEDGMENT$')

OVERALL_ROWS = [('SEVERITY', 'severity', SEVERITIES),
                ('EVIDENCE_ENOUGH', 'evidence_enough', ENOUGH),
                ('REFERENCE_CONCERN', 'reference_concern', CONCERNS),
                ('COMMENT', 'comment', [])]
FIELDS = ['packet', 'response', 'criterion', 'judgment', 'comment']


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
    if not options:
        return text, None
    for option in options:
        if text.lower() == option.lower():
            return option, None
    # A reviewer who types the fallback often types only the first words of a long option.
    for option in options:
        if option.lower().startswith(text.lower()) and len(text) > 2:
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

    criteria, overall, seen_field = {}, {}, False
    for tag, value in answers_in(document):
        if COVER_TAG.match(tag):
            seen_field = True
            continue

        match = CRITERION_TAG.match(tag)
        if match:
            seen_field = True
            response, number = match.group(1).upper(), match.group(2)
            judgment, note = normalise(value, JUDGMENTS)
            if note:
                problems.append('%s: response %s criterion %s %s'
                                % (path.name, response, number, note))
            criteria[(response, number)] = {
                'packet': packet, 'response': response, 'criterion': number,
                'judgment': judgment, 'comment': ''}
            continue

        match = OVERALL_TAG.match(tag)
        if match:
            seen_field = True
            response, which = match.group(1).upper(), match.group(2)
            options = dict((a, c) for a, _, c in OVERALL_ROWS)[which]
            clean, note = normalise(value, options)
            if note:
                problems.append('%s: response %s %s %s'
                                % (path.name, response, which.lower(), note))
            overall.setdefault(response, {})[which] = clean
            continue

        problems.append('%s: unknown answer field %r' % (path.name, tag))

    records = list(criteria.values())
    for response, values in overall.items():
        for tag_name, label, _ in OVERALL_ROWS:
            value = values.get(tag_name, '')
            if tag_name == 'COMMENT':
                records.append({'packet': packet, 'response': response, 'criterion': 'comment',
                                'judgment': '', 'comment': value})
            else:
                records.append({'packet': packet, 'response': response, 'criterion': label,
                                'judgment': value, 'comment': ''})

    if not records:
        problems.append('%s: no review fields found%s'
                        % (path.name, ' (only cover fields)' if seen_field else ''))
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
    return (record['response'], order, record['criterion'], record['packet'])


def disagreements(records):
    """One row per point where the returns differ, or where a response was challenged."""
    grouped, comments = {}, {}
    for record in records:
        grouped.setdefault((record['response'], record['criterion']), []).append(record)
        if record['criterion'] == 'comment' and record['comment']:
            comments.setdefault(record['response'], {})[record['packet']] = record['comment']

    def note(response, group):
        pool = comments.get(response, {})
        packets = sorted({r['packet'] for r in group})
        return ' || '.join('%s: %s' % (p, pool[p]) for p in packets if p in pool)

    out = []
    for (response, criterion), group in sorted(grouped.items(), key=lambda kv: sort_key(kv[1][0])):
        if criterion == 'comment':
            continue
        answers = {r['packet']: r['judgment'] for r in group if r['judgment']}
        if len(set(answers.values())) > 1:
            out.append({'response': response, 'criterion': criterion, 'field': criterion,
                        'kind': 'disagreement',
                        'answers': '; '.join('%s=%s' % kv for kv in sorted(answers.items())),
                        'comments': note(response, group)})
        flagged = {}
        if criterion.isdigit():
            flagged = {p: v for p, v in answers.items() if v != 'Correct'}
            kind = 'challenged'
        elif criterion == 'severity':
            flagged = {p: v for p, v in answers.items() if v != 'None'}
            kind = 'severity recorded'
        elif criterion == 'evidence_enough':
            flagged = {p: v for p, v in answers.items() if v != 'Yes'}
            kind = 'evidence not sufficient'
        elif criterion == 'reference_concern':
            flagged = {p: v for p, v in answers.items() if v != 'None identified'}
            kind = 'reference concern'
        else:
            kind = ''
        if flagged:
            out.append({'response': response, 'criterion': criterion, 'field': criterion,
                        'kind': kind,
                        'answers': '; '.join('%s=%s' % kv for kv in sorted(flagged.items())),
                        'comments': note(response, group)})
    return out


def anchor_agreement(records):
    """Responses that more than one packet judged, and how often the judgments matched."""
    grouped = {}
    for record in records:
        if record['criterion'].isdigit() and record['judgment']:
            grouped.setdefault((record['response'], record['criterion']), {})[
                record['packet']] = record['judgment']
    shared = {key: value for key, value in grouped.items() if len(value) > 1}
    agreed = [key for key, value in shared.items() if len(set(value.values())) == 1]
    pairs = matched = 0
    for value in shared.values():
        answers = sorted(value.items())
        for i in range(len(answers)):
            for j in range(i + 1, len(answers)):
                pairs += 1
                matched += answers[i][1] == answers[j][1]
    responses = sorted({response for response, _ in shared})
    return responses, len(shared), len(agreed), pairs, matched


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Intake returned extension reviewer packets.')
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

    responses_csv = args.out / 'extension_review_responses.csv'
    disagreements_csv = args.out / 'extension_review_disagreements.csv'
    conflicts = disagreements(records)
    write_csv(responses_csv, FIELDS, records)
    write_csv(disagreements_csv, ['response', 'criterion', 'field', 'kind', 'answers', 'comments'],
              conflicts)

    criterion_rows = [r for r in records if r['criterion'].isdigit()]
    answered = [r for r in criterion_rows if r['judgment']]
    packets = sorted({r['packet'] for r in records})
    responses = sorted({r['response'] for r in records})

    print('Extension reviewer intake')
    print('  packets read:   %d (%s)' % (len(packets), ', '.join(packets) or 'none'))
    print('  responses seen: %d (%s)' % (len(responses), ', '.join(responses) or 'none'))
    print('  criterion judgments: %d answered, %d left blank'
          % (len(answered), len(criterion_rows) - len(answered)))
    counts = {}
    for record in answered:
        counts[record['judgment']] = counts.get(record['judgment'], 0) + 1
    for option in JUDGMENTS:
        if counts.get(option):
            print('    %-13s %d' % (option, counts[option]))
    for key, value in sorted((k, v) for k, v in counts.items() if k not in JUDGMENTS):
        print('    %-13s %d  (not one of the listed answers)' % (key, value))

    for label, criterion, options in [('severity', 'severity', SEVERITIES),
                                      ('evidence enough', 'evidence_enough', ENOUGH),
                                      ('reference concern', 'reference_concern', CONCERNS)]:
        values = [r['judgment'] for r in records if r['criterion'] == criterion and r['judgment']]
        if values:
            tally = {v: values.count(v) for v in sorted(set(values), key=lambda v: (
                options.index(v) if v in options else len(options)))}
            print('  %s: %s' % (label, ', '.join('%s %d' % kv for kv in tally.items())))

    shared, points, agreed, pairs, matched = anchor_agreement(records)
    if points:
        print('  responses judged by more than one packet: %d (%s)'
              % (len(shared), ', '.join(shared)))
        print('  criteria on those responses: %d, of which %d were judged the same by every '
              'packet that answered them (%.0f%%)' % (points, agreed, 100.0 * agreed / points))
        print('  pairwise: %d reviewer pairs compared, %d agreed (%.0f%%)'
              % (pairs, matched, 100.0 * matched / pairs if pairs else 0))
    else:
        print('  No response was judged by more than one packet, so no agreement can be described.')

    print('  rows written: %d -> %s' % (len(records), responses_csv))
    print('  disagreement and concern rows: %d -> %s' % (len(conflicts), disagreements_csv))
    kinds = {}
    for row in conflicts:
        kinds[row['kind']] = kinds.get(row['kind'], 0) + 1
    for kind, count in sorted(kinds.items()):
        print('    %-24s %d' % (kind, count))
    if problems:
        print('  Problems (%d):' % len(problems))
        for problem in problems:
            print('    - %s' % problem)
    print('Nothing was adjudicated or rewritten. Reviewer names were not copied into the CSV.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
