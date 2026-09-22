"""Synthetic-fixture tests for analyze_supplement.py and check_scoring_forms.py.

No real experimental data is read. A temporary base directory is built with a copy of the
frozen experiment.py so the tests exercise the same metrics() definition.
Run:  python3 test_supplement.py --frozen-code "<21_.../code/experiment.py>"
"""
import argparse, hashlib, json, shutil, sys, tempfile, unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1] / 'supplement'  # repository layout (2026-09-18): modules are in code/supplement/
sys.path.insert(0, str(HERE))
# The frozen module is in the repository, so plain discovery works; --frozen-code still points elsewhere.
FROZEN = Path(__file__).resolve().parents[1] / 'frozen_2026-09-15/experiment.py'


def h(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def w(p, obj):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(obj, indent=1))


def make_base(tmp, unscorable=False):
    base = Path(tmp)
    (base / 'code').mkdir(parents=True)
    shutil.copy(FROZEN, base / 'code/experiment.py')
    for d in ['protocol', 'prompts', 'references']:
        (base / d).mkdir(); (base / d / 'placeholder.txt').write_text(d)
    cases = ['W1-01', 'W1-02', 'W2-01', 'W2-02', 'W3-01', 'W3-02']
    inst = {'W1-01': 'U1', 'W1-02': 'U1', 'W2-01': 'U2', 'W2-02': 'U3', 'W3-01': 'U3', 'W3-02': 'U2'}
    for c in cases:
        w(base / f'inputs/{c}.json', {'case_id': c, 'institution': inst[c]})
    key, imported, paths, scores, timing_assign = [], [], [], [], []
    i = 0
    for c in cases:
        for m in ['astra', 'luna']:
            for rep in [1, 2]:
                i += 1; rid = f'run{i:02d}'; mid = f'R{i:03d}'
                key.append({'case_id': c, 'masked_id': mid, 'model': m, 'order': i, 'prompt': '', 'raw_txt': '', 'receipt': '', 'repetition': rep, 'run_id': rid})
                imported.append({'run_id': rid, 'case_id': c, 'record_status': 'RECEIVED'})
                # Design: astra acceptable except W2-02; luna serious on W2-* and W3-01
                serious = (m == 'luna' and (c.startswith('W2') or c == 'W3-01')) or (m == 'astra' and c == 'W2-02')
                acc = not serious
                status = 'SCORED'
                if unscorable and mid == 'R001':
                    status, acc = 'CANNOT_JUDGE', None
                scores.append({'masked_id': mid, 'case_id': c, 'status': status, 'scored_at': '2026-09-17T20:00:00+08:00',
                               'severity': ('Major' if serious else 'None') if status == 'SCORED' else None,
                               'acceptable': acc, 'criteria': [{'criterion': 1, 'judgment': 'Correct' if acc else 'Incorrect'}],
                               'reference_challenge': 'reading disputed' if mid == 'R005' else ''})
                paths.append({'run_id': rid, 'case_id': c, 'pathway': 'direct', 'decision': 'release', 'trace': [], 'raw_sha256': '', 'control_error': None})
                # controls: block serious luna W3-01 via numeric; route one acceptable astra W1-01
                if m == 'luna' and c == 'W3-01':
                    dec, trace = 'block', [{'check': 'recompute_MGA', 'status': 'FAIL'}]
                elif m == 'astra' and c == 'W1-01':
                    dec, trace = 'route', [{'check': 'consequential_action_routing', 'status': 'TRIGGERED'}]
                else:
                    dec, trace = 'release_with_warning', [{'check': 'schema', 'status': 'PASS'}]
                paths.append({'run_id': rid, 'case_id': c, 'pathway': 'controlled', 'decision': dec, 'trace': trace, 'raw_sha256': '', 'control_error': None})
    # T24 must belong to the SAME condition it is excluded from, or the exclusion test is vacuous.
    for n, (rid, p) in enumerate([('run01', 'direct'), ('run02', 'controlled'), ('run07', 'direct'), ('run06', 'controlled')], 1):
        timing_assign.append({'timing_id': f'T{n:02d}' if n < 4 else 'T24', 'run_id': rid, 'pathway': p, 'case_id': 'W1-01' if n < 3 else 'W1-02'})
    w(base / 'private/identity_key.json', key); w(base / 'private/imported_primary.json', imported)
    w(base / 'private/pathways.json', paths); w(base / 'private/timing_assignment.json', timing_assign)
    w(base / 'private/repeat_assignment.json', []); w(base / 'private/reviewer_assignments.json', [])
    w(base / 'scoring/researcher_scores.json', scores)
    w(base / 'scoring/score_lock.json', {'sha256': h(base / 'scoring/researcher_scores.json')})
    items, events = {}, []
    for n, tid in enumerate([t['timing_id'] for t in timing_assign]):
        items[tid] = {'clock1_seconds': 100 + n * 10, 'clock2_seconds': 0 if n % 2 == 0 else 400, 'decision': 'accept',
                      'completion_status': 'justified_disposition', 'inspect_override': False}
        events += [{'timing_id': tid, 'action': 'decide', 'at': '2026-09-16T13:50:05+00:00'}]
        if tid == 'T03':  # zero-work completion with a long untimed interval (the real T16 pattern)
            events.append({'timing_id': tid, 'action': 'no_work', 'at': '2026-09-16T14:02:00+00:00'})
        else:
            events.append({'timing_id': tid, 'action': 'finalize_start', 'at': '2026-09-16T14:43:19+00:00' if tid == 'T01' else '2026-09-16T13:50:10+00:00'})
    w(base / 'timing/session.json', {'items': items, 'events': events})
    sys.path.insert(0, str(base / 'code'))
    import importlib, experiment
    importlib.reload(experiment)
    w(base / 'freeze.json', {'sha256': {str(p.relative_to(base)): h(p) for p in experiment.frozen_files(base)}})
    return base


class SupplementTests(unittest.TestCase):
    def run_analysis(self, **kw):
        import importlib, analyze_supplement
        importlib.reload(analyze_supplement)
        self.tmp = tempfile.mkdtemp()
        base = make_base(self.tmp, **kw)
        return analyze_supplement.analyze(base), base

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        sys.modules.pop('experiment', None)

    def test_primary_counts_match_frozen_metrics(self):
        res, _ = self.run_analysis()
        for cond, block in res['S2_conditions'].items():
            fm = res['frozen_metrics_crosscheck'][cond]
            self.assertEqual(block['useful_release']['n'], fm['useful_release_n'], cond)
            self.assertEqual(block['serious_released']['n'], fm['serious_release_n'], cond)

    def test_expected_values(self):
        res, _ = self.run_analysis()
        s = res['S2_conditions']
        self.assertEqual(s['luna_direct']['serious_released']['text'], '6/12')   # W2-01, W2-02, W3-01 x 2 reps
        self.assertEqual(s['luna_controlled']['serious_released']['n'], 4)       # W3-01 (2 reps) blocked
        self.assertEqual(s['luna_controlled']['serious_withheld']['text'], '2/6')
        self.assertEqual(s['astra_controlled']['unnecessary_withholding']['text'], '2/10')
        self.assertEqual(s['astra_controlled']['withheld_acceptable_routed'], 2)
        self.assertEqual(s['astra_direct']['unnecessary_withholding']['n'], 0)

    def test_workflow_and_placeholders(self):
        res, _ = self.run_analysis()
        p = res['S9_placeholders']
        self.assertEqual(p['R-W3-4-SERIOUS'], '0/4')
        self.assertEqual(p['R-W1-2-WITHHELD'], '2/4')
        self.assertIn('R-13a', p); self.assertIn('R-14d', p); self.assertNotIn('R-14a', p)
        self.assertTrue(p['R-00-coverage'].startswith('24 scored'))

    def test_case_direction_counts(self):
        res, _ = self.run_analysis()
        d = res['S10_case_direction']
        self.assertEqual(d['luna_serious_release'], {'cases_controls_better': 1, 'cases_controls_worse': 0, 'cases_unchanged': 5, 'cases_not_evaluable': 0})
        self.assertEqual(d['astra_useful_release'], {'cases_controls_better': 0, 'cases_controls_worse': 1, 'cases_unchanged': 5, 'cases_not_evaluable': 0})
        self.assertEqual(res['S10b_case_tradeoff']['luna']['withheld_only_serious'], 1)
        self.assertEqual(res['S10b_case_tradeoff']['astra']['withheld_only_acceptable'], 1)
        res2, _ = self.run_analysis(unscorable=True)
        self.assertEqual(res2['S10_case_direction']['astra_useful_release']['cases_not_evaluable'], 1)

    def test_bounding_sensitivities(self):
        res, _ = self.run_analysis(unscorable=True)   # R001 = astra W1-01 rep 1, routed under controls
        s2 = res['S2_conditions']
        self.assertEqual(res['S6b_least_favourable_to_direct']['astra_direct']['serious_released']['n'], s2['astra_direct']['serious_released']['n'] + 1)
        self.assertEqual(res['S6b_least_favourable_to_direct']['astra_controlled']['serious_withheld']['n'], s2['astra_controlled']['serious_withheld']['n'] + 1)
        self.assertEqual(res['S6a_least_favourable_to_controls']['astra_direct']['serious_released']['n'], s2['astra_direct']['serious_released']['n'] + 1)
        self.assertEqual(res['S6a_least_favourable_to_controls']['astra_controlled']['unnecessary_withholding']['n'], s2['astra_controlled']['unnecessary_withholding']['n'] + 1)
        self.assertEqual(s2['astra_direct']['unscored']['n'], 1)
        self.assertIn('unscored 1', res['S9_placeholders']['R-11a'])

    def test_timing_primary_rule_handler_exposure_delegation(self):
        res, _ = self.run_analysis()
        t = res['S8_timing']
        self.assertEqual(t['flagged_items'], ['T01', 'T03', 'T24'])
        ac = t['by_condition']['astra_controlled']
        self.assertEqual(ac['primary_clock1']['n'], 1); self.assertEqual(ac['excluded_items'], ['T24'])
        self.assertIn('with correction', res['S9_placeholders']['R-34b'])
        h = res['S13_handler_vs_score']
        self.assertEqual(h['n'], 4); self.assertEqual(h['cells'].get('direct|accept|acceptable'), 2); self.assertEqual(h['serious_scored_items'], 0)
        self.assertEqual(res['S14_exposure']['excluding_controlled_timed_answers']['astra_controlled']['scheduled'], 10)
        self.assertEqual(res['S15_delegation']['luna']['critical_n'], 0); self.assertEqual(res['S15_delegation']['luna']['scored_n'], 12)
        self.assertIn('withheld_by_first_check', res['S4_checks'])

    def test_timing_gap_flag_and_T24_exclusion(self):
        res, _ = self.run_analysis()
        t = res['S8_timing']
        self.assertEqual(t['untimed_gap_over_5_min'], ['T01', 'T03'])   # finalize_start gap and no_work gap
        ac = t['by_condition']['astra_controlled']
        self.assertEqual((ac['clock2']['n'], ac['clock2_excluding_T24']['n'], ac['clock1_excluding_T24']['n']), (2, 1, 1))

    def test_blocked_acceptable_unavailable_and_ci(self):
        import importlib, analyze_supplement as a
        importlib.reload(a)
        self.tmp = tempfile.mkdtemp(); base = make_base(self.tmp)
        paths = json.loads((base / 'private/pathways.json').read_text())
        imported = json.loads((base / 'private/imported_primary.json').read_text())
        for pth in paths:   # astra W3-02 (acceptable): blocked by a unit-label failure
            if pth['run_id'] in ('run21', 'run22') and pth['pathway'] == 'controlled':
                pth['decision'] = 'block'
                pth['trace'] = [{'check': 'recompute_weighted_score', 'status': 'FAIL', 'reported': [{'value': 84.6}], 'computed_from_inputs': 84.6, 'tolerance': .0051}]
            if pth['run_id'] == 'run24':   # luna W3-02 rep 2 not received
                pth['decision'] = 'unavailable'; pth['trace'] = []
        for r in imported:
            if r['run_id'] == 'run24':
                r['record_status'] = 'NOT_RECEIVED'
        w(base / 'private/pathways.json', paths); w(base / 'private/imported_primary.json', imported)
        import experiment
        w(base / 'freeze.json', {'sha256': {str(p.relative_to(base)): h(p) for p in experiment.frozen_files(base)}})
        res = a.analyze(base)
        ac = res['S2_conditions']['astra_controlled']
        self.assertEqual((ac['withheld_acceptable_blocked'], ac['withheld_acceptable_routed']), (2, 2))
        self.assertEqual(res['S11_check_applicability']['block_causes']['recompute_weighted_score:unit_label_not_in_allow_list']['acceptable'], 2)
        lc = res['S2_conditions']['luna_controlled']
        self.assertEqual(lc['scheduled'], 12); self.assertEqual(lc['scored'], 11)
        self.assertEqual(res['S6b_least_favourable_to_direct']['luna_direct']['serious_released']['n'],
                         res['S2_conditions']['luna_direct']['serious_released']['n'])  # unavailable is not 'unscored'
        ci = res['S2_conditions']['luna_direct']['serious_released_ci']
        self.assertIsNotNone(ci['interval']); self.assertLessEqual(ci['interval'][0], ci['point']); self.assertLessEqual(ci['point'], ci['interval'][1])
        self.assertIn('[', res['S9_placeholders']['R-12c'])
        self.assertEqual(res['S7_repetition_consistency']['astra']['same_label'], 6)

    def test_answers_read_after_the_lock_are_added_but_never_overwrite_one(self):
        """The overlay fills in unread answers, refuses to revise a locked score, and changes the counts."""
        import importlib, analyze_supplement as a
        importlib.reload(a)
        self.tmp = tempfile.mkdtemp(); base = make_base(self.tmp)
        scores = json.loads((base / 'scoring/researcher_scores.json').read_text())
        key = {r['masked_id']: r for r in json.loads((base / 'private/identity_key.json').read_text())}
        left_unread = [s for s in scores if s['case_id'] == 'W1-02']
        for s in left_unread:
            s['status'], s['acceptable'], s['severity'], s['criteria'] = 'MISSING', None, None, []
        w(base / 'scoring/researcher_scores.json', scores)
        w(base / 'scoring/score_lock.json', {'sha256': h(base / 'scoring/researcher_scores.json')})
        before = a.analyze(base)
        self.assertEqual(before['S1_coverage']['SCORED'], 20)

        record = lambda s, acc: {'run_id': key[s['masked_id']]['run_id'], 'status': 'SCORED', 'acceptable': acc,
                                 'severity': 'None' if acc else 'Major',
                                 'criteria': [{'criterion': 1, 'judgment': 'Correct' if acc else 'Incorrect'}]}
        ext = base / 'ext_scores.json'
        w(ext, {'records': [record(s, True) for s in left_unread]})
        after = a.analyze(base, str(ext), 'supplement_results_with_extension.json')
        self.assertEqual(after['extension_overlay']['answers_added'], 4, 'one case, four answers, counted once each')
        self.assertEqual(after['S1_coverage']['SCORED'], 24)
        self.assertGreater(after['S2_conditions']['astra_direct']['useful_release']['n'],
                           before['S2_conditions']['astra_direct']['useful_release']['n'])
        self.assertIn('S17_recomputed_sensitivities', after)
        self.assertNotIn('S17_recomputed_sensitivities', before)
        self.assertTrue((base / 'analysis/supplement/supplement_results.json').exists(),
                        'the run without the overlay keeps its own file')

        already = [s for s in scores if s['status'] == 'SCORED'][0]
        w(ext, {'records': [record(already, False)]})
        with self.assertRaises(ValueError) as e:
            a.analyze(base, str(ext), 'supplement_results_with_extension.json')
        self.assertIn('never revised', str(e.exception))

        w(ext, {'records': [{'run_id': 'no-such-run', 'status': 'SCORED', 'acceptable': True, 'severity': 'None', 'criteria': []}]})
        with self.assertRaises(ValueError):
            a.analyze(base, str(ext), 'supplement_results_with_extension.json')

    def test_frozen_base_untouched(self):
        # Run in a fresh interpreter WITHOUT -B, so only the script's own guard can prevent __pycache__.
        import subprocess, os
        self.tmp = tempfile.mkdtemp(); base = make_base(self.tmp)
        env = {k: v for k, v in os.environ.items() if k != 'PYTHONDONTWRITEBYTECODE'}
        out = subprocess.run([sys.executable, str(HERE / 'analyze_supplement.py'), '--base', str(base)], capture_output=True, text=True, env=env)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertFalse((base / 'code/__pycache__').exists())


class SyncTests(unittest.TestCase):
    def test_sync_ready_and_missing(self):
        import subprocess
        tmp = Path(tempfile.mkdtemp()); (tmp / 'materials').mkdir()
        rows = []
        for i, complete in [(1, True), (2, False)]:
            mid = f'R{i:03d}'
            rows.append({'masked_id': mid, 'case_id': 'W1-01', 'status': 'PENDING', 'scored_at': None, 'severity': None, 'acceptable': None,
                         'failure_classes': [], 'criteria': [{'criterion': 1, 'judgment': None, 'response_evidence': '', 'reason': ''},
                                                             {'criterion': 2, 'judgment': None, 'response_evidence': '', 'reason': ''}],
                         'reference_challenge': '', 'prior_timing_exposure': False})
            form = ('Actual scoring completed at (date, time and timezone): September 17, 12:55 PM - 1:01 PM\n'
                    f"Status (SCORED / MISSING / CANNOT_JUDGE): {'SCORED' if complete else ''}\n\n"
                    '## Criterion 1\n\nx\n\nJudgment (Correct / Incorrect / Incomplete / Cannot judge): Correct\nResponse evidence and brief reason: quoted text\n\n'
                    '## Criterion 2\n\ny\n\nJudgment (Correct / Incorrect / Incomplete / Cannot judge): Incomplete\nResponse evidence and brief reason: omits step\n\n'
                    '## Overall\n\nSeverity (None / Minor / Major / Critical / Cannot judge): Minor\nAcceptable (Yes / No / Cannot judge): Yes\n'
                    'Source or reference concern: None\nOther comments: fine\n')
            (tmp / 'materials' / f'{mid}_review.md').write_text(form)
        (tmp / 'researcher_scores.json').write_text(json.dumps(rows))
        out = subprocess.run([sys.executable, str(HERE / 'sync_scoring_forms.py'), '--scoring', str(tmp), '--write', '--mark-missing', 'cutoff'],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        res = json.loads((tmp / 'researcher_scores.json').read_text())
        self.assertEqual(res[0]['status'], 'SCORED'); self.assertEqual(res[0]['scored_at'], '2026-09-17T13:01:00+08:00')
        self.assertEqual([c['judgment'] for c in res[0]['criteria']], ['Correct', 'Incomplete'])
        self.assertIs(res[0]['acceptable'], True); self.assertEqual(res[0]['severity'], 'Minor'); self.assertEqual(res[0]['reference_challenge'], '')
        self.assertEqual(res[1]['status'], 'MISSING')
        self.assertTrue(any(p.name.startswith('researcher_scores.backup_') for p in tmp.iterdir()))
        shutil.rmtree(tmp)


class ReviewerAgreementTests(unittest.TestCase):
    def test_agreement_requires_lock_and_counts(self):
        import subprocess, zipfile
        tmp = Path(tempfile.mkdtemp()); base = make_base(tmp / 'b')
        shutil.copy(FROZEN.with_name('scoring.py'), base / 'code/scoring.py') if FROZEN.with_name('scoring.py').exists() else None
        ret = tmp / 'returned'; ret.mkdir()
        wns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        def sdt(tag, val):
            return f'<w:sdt><w:sdtPr><w:tag w:val="{tag}"/></w:sdtPr><w:sdtContent><w:r><w:t>{val}</w:t></w:r></w:sdtContent></w:sdt>'
        body = sdt('R001_C1', 'Correct') + sdt('R001_SEVERITY', 'None') + sdt('R001_REFERENCE_CONCERN', 'No concerns') + sdt('R013_C1', 'Correct') + sdt('R013_SEVERITY', 'Minor') + sdt('R013_REFERENCE_CONCERN', 'Key too narrow')
        with zipfile.ZipFile(ret / 'Somebody - A1-Core.docx', 'w') as z:
            z.writestr('word/document.xml', f'<w:document xmlns:w="{wns}"><w:body>{body}</w:body></w:document>')
        script = str(HERE / 'reviewer_agreement.py')
        (base / 'scoring/score_lock.json').rename(base / 'scoring/lock.bak')
        out = subprocess.run([sys.executable, script, '--base', str(base), '--returned', str(ret)], capture_output=True, text=True)
        self.assertNotEqual(out.returncode, 0); self.assertIn('not locked', out.stdout + out.stderr)
        (base / 'scoring/lock.bak').rename(base / 'scoring/score_lock.json')
        out = subprocess.run([sys.executable, script, '--base', str(base), '--returned', str(ret)], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        r = json.loads((base / 'analysis/supplement/reviewer_agreement.json').read_text())
        pr = r['per_reviewer']['Reviewer-01']
        self.assertEqual((pr['packet'], pr['responses_returned'], pr['criteria_compared'], pr['reference_concerns']), ('A1-Core', 2, 2, 1))
        self.assertEqual(r['criterion_exact_agreement'], {'agree': 1, 'n': 2})   # R013 is luna W2-02... serious in fixture
        self.assertEqual(r['serious_vs_not']['table']['researcher_yes_reviewer_no'], 1)
        labels = json.loads((base / 'private/reviewer_labels.json').read_text())
        self.assertEqual(labels, {'Somebody - A1-Core.docx': 'Reviewer-01'})
        self.assertNotIn('Somebody', (base / 'analysis/supplement/reviewer_agreement.json').read_text())
        shutil.rmtree(tmp)


class FormTests(unittest.TestCase):
    def test_form_rules(self):
        import check_scoring_forms as f
        tmp = Path(tempfile.mkdtemp())
        good = tmp / 'R001_review.md'
        good.write_text('Actual scoring completed at (date): 2026-09-17T21:05:00+08:00\nStatus (SCORED / MISSING / CANNOT_JUDGE): SCORED\n'
                        'Judgment (Correct / Incorrect / Incomplete / Cannot judge): Correct\nSeverity (None / Minor / Major / Critical / Cannot judge): None\n'
                        'Acceptable (Yes / No / Cannot judge): Yes\n')
        self.assertEqual(f.check_form(good)['state'], 'READY')
        bad = tmp / 'R002_review.md'
        bad.write_text('Actual scoring completed at (date): September 17, 12:55 PM - 1:01 PM\nStatus (SCORED): SCORED\n'
                       'Judgment (Correct): Cannot judge\nSeverity (None): Cannot judge\nAcceptable (Yes): Yes\n')
        r = f.check_form(bad)
        self.assertEqual(r['state'], 'NEEDS_FIX')
        self.assertEqual(r['iso_time'], '2026-09-17T13:01:00+08:00')
        self.assertTrue(any('lock will reject' in i for i in r['issues']))
        self.assertTrue(any('free-text' in w for w in r['warnings']))
        self.assertTrue(any('conflicts' in i for i in r['issues']))
        cj = tmp / 'R003_review.md'   # addendum D2: CANNOT_JUDGE with a reason and blank labels is complete
        cj.write_text('Status (SCORED / MISSING / CANNOT_JUDGE): CANNOT_JUDGE\nSeverity (None): \nAcceptable (Yes): \nOther comments: reference ambiguous on scope\n')
        self.assertEqual(f.check_form(cj)['state'], 'READY')
        self.assertIsNone(f.parse_time('2026-09-17')[0])                       # date-only is not a completion time
        self.assertIn('confirm', f.parse_time('2026-09-17 13:01')[1])          # naive ISO is flagged
        self.assertIsNone(f.parse_time('September 17, 11:58 PM - 12:04 AM')[0])  # crosses midnight
        shutil.rmtree(tmp)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--frozen-code', default=str(FROZEN))
    a, rest = ap.parse_known_args()
    FROZEN = Path(a.frozen_code)
    unittest.main(argv=[sys.argv[0]] + rest, verbosity=2)
