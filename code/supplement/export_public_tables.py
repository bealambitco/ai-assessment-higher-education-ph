"""Export the aggregate CSV tables published in results/aggregate/ (added 2026-09-18 for the public release).

Reads the researcher's local analysis outputs, which contain masked answer IDs and private keys, and
writes only counts, rates and summaries. No masked answer ID, timing-item ID, reviewer name, model-to-answer
mapping or free text is written. The inputs are not in this repository; this script documents exactly how
each public table was derived.

Usage (researcher's machine only):
  python3 -B code/supplement/export_public_tables.py \
      --base <21_EXPERIMENT_EXECUTION_PACKAGE> --judge <23_AI_JUDGE_EXTENSION_PACKAGE> \
      --claude-key <25_CLAUDE_MATCHED_SCORING_EXTENSION> --claude-judge <26_CLAUDE_AI_JUDGE_EXTENSION> \
      --doc <24_DOCUMENT_EVIDENCE_EXTENSION_PACKAGE> --out results/aggregate
"""
import argparse, csv, json, re, sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
CONDS = ['astra_direct', 'astra_controlled', 'luna_direct', 'luna_controlled']
ID_PATTERN = re.compile(r'\b(R\d{3}|T\d{2}|J\d{3}|K\d{3})\b')


def load(p):
    return json.loads(Path(p).read_text())


def split(cond):
    m, p = cond.split('_'); return m, p


def nd(x):
    return (x or {}).get('n'), (x or {}).get('d')


def ci(x):
    iv = (x or {}).get('interval')
    return (round(iv[0], 4), round(iv[1], 4)) if iv else ('', '')


def outcome_row(cond, s):
    m, p = split(cond)
    acc_n, acc_d = nd(s['acceptable']); ser_n, _ = nd(s['serious_released'])
    ur_n, ur_d = nd(s['useful_release']); lo, hi = ci(s['useful_release_ci'])
    uw_n, uw_d = nd(s['unnecessary_withholding']); sw_n, sw_d = nd(s['serious_withheld'])
    dec = s.get('decisions', {})
    return {'model': m, 'pathway': p, 'scheduled': s['scheduled'], 'scored': s['scored'],
            'acceptable': acc_n, 'other_unacceptable': s['other_unacceptable']['n'], 'unscored': s['unscored']['n'],
            'serious_released': ser_n, 'useful_release': ur_n, 'denominator': ur_d,
            'useful_release_ci95_low': lo, 'useful_release_ci95_high': hi,
            'acceptable_withheld': uw_n, 'acceptable_denominator': uw_d,
            'acceptable_withheld_routed': s['withheld_acceptable_routed'], 'acceptable_withheld_blocked': s['withheld_acceptable_blocked'],
            'serious_withheld': sw_n, 'serious_denominator': sw_d,
            'decisions_release': dec.get('release', 0), 'decisions_release_with_warning': dec.get('release_with_warning', 0),
            'decisions_route': dec.get('route', 0), 'decisions_block': dec.get('block', 0)}


def write(out, name, rows, note=None):
    path = out / name
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    text = path.read_text()
    assert not ID_PATTERN.search(text), f'identifier leaked into {name}'
    assert str(Path.home()) not in text  # no absolute local paths
    print(f'{name}: {len(rows)} rows')


def main(a):
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    sup = load(Path(a.base) / 'analysis/supplement/supplement_results.json')

    c = sup['S1_coverage']
    write(out, 'coverage.csv', [{'scheduled_answers': c['scheduled'], 'scored': c['SCORED'], 'cannot_judge': c['CANNOT_JUDGE'],
                                 'not_scored_at_cutoff': c['MISSING'], 'reference_challenges_recorded': c['reference_challenges'],
                                 'scoring_cutoff': '2026-09-18T12:50:00+08:00', 'scoring_order': 'balanced first-48 order fixed in advance (seed 2026091703); 12 complete cases'}])

    write(out, 'primary_outcomes.csv', [outcome_row(k, sup['S2_conditions'][k]) for k in CONDS])

    rows = []
    for wf, conds in sup['S5_workflow'].items():
        for k in CONDS:
            r = outcome_row(k, conds[k]); rows.append({'workflow': wf, **r})
    write(out, 'outcomes_by_workflow.csv', rows)

    s11 = sup['S11_check_applicability']
    rows = [{'check': chk, 'status': st, 'answers': n, 'scope': 'all 96 primary answers'} for chk, sts in s11['status_by_check'].items() for st, n in sts.items()]
    write(out, 'check_status.csv', rows)
    rows = [{'block_cause': cause, 'outcome_class': oc, 'blocked_answers': n} for cause, d in s11['block_causes'].items() for oc, n in d.items()]
    write(out, 'block_causes.csv', rows)
    s4 = sup['S4_checks']
    rows = []
    for view in ('fired_by_outcome', 'withheld_by_first_check'):
        for chk, d in s4[view].items():
            rows.append({'view': view, 'check': chk, 'serious': d['serious'], 'acceptable': d['acceptable'], 'other_unacceptable': d['other_unacceptable'], 'scope': 'scored answers under controlled release (48)'})
    write(out, 'checks_by_outcome.csv', rows)

    rows = []
    for key, text in sup['S16_frozen_surfaced'].items():
        kind, analysis, cond = key.split('|')
        m = re.search(r'serious(?: released)? (\d+)/(\d+); useful (\d+)/(\d+)', text)
        rows.append({'kind': 'frozen diagnostic' if kind == 'diag' else 'frozen sensitivity', 'analysis': analysis.replace('loio:', 'leave out institution: '),
                     'condition': cond, 'serious_released': m.group(1), 'useful_release': m.group(3), 'denominator': m.group(2)})
    for label, block in (('bound: least favourable to controls (S6a)', sup['S6a_least_favourable_to_controls']),
                         ('bound: least favourable to direct release (S6b)', sup['S6b_least_favourable_to_direct'])):
        for k in CONDS:
            s = block[k]
            rows.append({'kind': 'post-freeze bound', 'analysis': label, 'condition': k, 'serious_released': s['serious_released']['n'],
                         'useful_release': s['useful_release']['n'], 'denominator': s['useful_release']['d']})
    for label, block in sup['S14_exposure'].items():
        for k in CONDS:
            s = block[k]
            rows.append({'kind': 'post-freeze exposure sensitivity', 'analysis': label, 'condition': k, 'serious_released': s['serious_released']['n'],
                         'useful_release': s['useful_release']['n'], 'denominator': s['useful_release']['d']})
    write(out, 'sensitivity_analyses.csv', rows)

    rows = []
    for m in ('astra', 'luna'):
        s10u, s10s, s10b = sup['S10_case_direction'][f'{m}_useful_release'], sup['S10_case_direction'][f'{m}_serious_release'], sup['S10b_case_tradeoff'][m]
        rep, dlg, crit = sup['S7_repetition_consistency'][m], sup['S15_delegation'][m], sup['S12_criterion_correctness'][m]
        rows.append({'model': m, 'cases_useful_release_controls_better': s10u['cases_controls_better'], 'cases_useful_release_controls_worse': s10u['cases_controls_worse'],
                     'cases_useful_release_unchanged': s10u['cases_unchanged'], 'cases_serious_release_controls_better': s10s['cases_controls_better'],
                     'cases_serious_release_controls_worse': s10s['cases_controls_worse'], 'cases_not_evaluable': s10u['cases_not_evaluable'],
                     'cases_withheld_only_acceptable': s10b['withheld_only_acceptable'], 'cases_withheld_only_serious': s10b['withheld_only_serious'],
                     'cases_scored_both_repetitions': rep['cases_with_both'], 'cases_same_label_both_repetitions': rep['same_label'],
                     'critical_inappropriate_delegation': dlg['critical_n'], 'scored_answers': dlg['scored_n'],
                     'criterion_correctness_scheduled_case_mean': round(crit['scheduled_case_mean'], 4), 'criterion_correctness_scored_case_mean': round(crit['scored_case_mean'], 4)})
    write(out, 'paired_case_summary.csv', rows)

    t = sup['S8_timing']['by_condition']; rows = []
    for k in CONDS:
        m, p = split(k); x = t[k]
        pc, pc2, c1 = x['primary_clock1'], x['primary_clock2_among_corrected'] or {}, x['clock1']
        rows.append({'model': m, 'pathway': p, 'timed_items': c1['n'], 'primary_items': pc['n'],
                     'decision_time_s_median': round(pc['median']), 'decision_time_s_min': round(pc['min']), 'decision_time_s_max': round(pc['max']),
                     'items_needing_correction': x['primary_items_with_correction'].split('/')[0],
                     'correction_time_s_median_among_corrected': round(pc2['median']) if pc2 else '',
                     'all_recorded_decision_time_s_median': round(c1['median']), 'handling_accept': x['decisions'].get('accept', 0),
                     'handling_minor_edit': x['decisions'].get('minor_edit', 0), 'release_decision_overrides': x['overrides'],
                     'note': 'primary summary excludes one flagged item per condition (untimed gap > 5 min, unresolved interruption, or unknown prior exposure)'})
    write(out, 'timing_summary.csv', rows)
    s13 = sup['S13_handler_vs_score']
    rows = [dict(zip(('pathway', 'handling_decision', 'locked_score_class'), cell.split('|')), items=n) for cell, n in sorted(s13['cells'].items())]
    write(out, 'handling_vs_score.csv', rows)

    ra = load(Path(a.base) / 'analysis/supplement/reviewer_agreement.json')
    per = ra['per_reviewer']
    groups = {'Reviewer 1': ['Reviewer-01'], 'Reviewer 2': ['Reviewer-02', 'Reviewer-03']}  # Reviewer 2 returned two packets
    rows = []
    for label, keys in groups.items():
        for k in keys:
            r = per[k]
            rows.append({'reviewer': label, 'packet': r['packet'], 'responses_returned': r['responses_returned'], 'criteria_judged': r['criteria_judged'],
                         'criteria_compared_with_researcher': r['criteria_compared'], 'criteria_exact_agreement': r['criteria_exact_agree'],
                         'reference_concerns': r['reference_concerns'], 'responses_researcher_had_not_scored': r['responses_not_comparable_researcher_unscored']})
    write(out, 'reviewer_agreement_by_packet.csv', rows)
    rows = []
    for measure in ('criterion_correct_vs_not', 'serious_vs_not', 'acceptable_vs_not'):
        x = ra[measure]; tb = x['table']
        rows.append({'measure': measure, 'comparisons': x['n'], 'agree': x['agree'], 'both_yes': tb['both_yes'],
                     'researcher_yes_reviewer_no': tb['researcher_yes_reviewer_no'], 'researcher_no_reviewer_yes': tb['researcher_no_reviewer_yes'], 'both_no': tb['both_no']})
    rows.append({'measure': 'severity_exact', 'comparisons': ra['severity_exact_agreement']['n'], 'agree': ra['severity_exact_agreement']['agree'],
                 'both_yes': '', 'researcher_yes_reviewer_no': '', 'researcher_no_reviewer_yes': '', 'both_no': ''})
    write(out, 'reviewer_agreement.csv', rows)

    ag = load(Path(a.judge) / 'analysis/agreement_with_human.json')
    rows = []
    for measure in ('serious_error', 'acceptable', 'criterion_correct'):
        x = ag[measure]
        rows.append({'measure': measure, 'comparisons': x['n'], 'both_yes': x['both_yes'], 'human_yes_judge_no': x['human_yes_judge_no'],
                     'human_no_judge_yes': x['human_no_judge_yes'], 'both_no': x['both_no'], 'raw_agreement': x['raw_agreement'], 'kappa': '' if x['kappa'] is None else x['kappa']})
    sev = round(ag['severity_exact'] * ag['answers_compared'])
    rows.append({'measure': 'severity_exact', 'comparisons': ag['answers_compared'], 'both_yes': '', 'human_yes_judge_no': '', 'human_no_judge_yes': '', 'both_no': '',
                 'raw_agreement': ag['severity_exact'], 'kappa': f'{sev} of {ag["answers_compared"]} exact'})
    write(out, 'ai_judge_primary_agreement.csv', rows)
    dist = Counter(); valid = 0
    for p in sorted((Path(a.judge) / 'parsed_outputs').glob('J*.json')):
        d = load(p)
        if d['record_status'] == 'VALIDATED_STRUCTURE':
            valid += 1; dist[(d['judgment']['acceptable'], d['judgment']['severity'])] += 1
    write(out, 'ai_judge_primary_distribution.csv', [{'judge_acceptable': k[0], 'judge_severity': k[1], 'answers': n, 'valid_replies': valid} for k, n in sorted(dist.items())])

    ec = load(Path(a.base) / 'analysis/supplement/extension_controls.json'); rows = []
    for scope, block in (('matched 48 answers per model (12 scored cases)', ec['by_model']), ('desktop-interface sensitivity (46 per model)', ec['desktop_matched_sensitivity'])):
        for m, x in block.items():
            rel_n, rel_d = x['released'].split('/')
            row = {'scope': scope, 'model': m, 'answers': x['answers'], 'format_failures': x['format_failures'].split('/')[0], 'released': rel_n,
                   'block': x['decisions']['block'], 'route': x['decisions']['route'], 'release_with_warning': x['decisions']['release_with_warning']}
            for chk in ('quoted_source_membership', 'recompute', 'consequential_action_routing'):
                for st in ('PASS', 'FAIL', 'NOT_APPLICABLE', 'TRIGGERED', 'NOT_TRIGGERED'):
                    row[f'{chk}_{st}'] = x['check_status'].get(chk, {}).get(st, '')
            rows.append(row)
    write(out, 'claude_extension_checks.csv', rows)

    key = {r['masked_id'][1:]: r['model_key'] for r in load(Path(a.claude_key) / 'private/identity_key.json')}
    agg = {}
    for p in sorted((Path(a.claude_judge) / 'parsed_outputs').glob('K*.json')):
        d = load(p); m = key[p.stem[1:]]; j = d['judgment']
        g = agg.setdefault(m, Counter()); g['answers'] += 1; g['valid'] += d['record_status'] == 'VALIDATED_STRUCTURE'
        g['acceptable'] += j['acceptable'] == 'Yes'; g[f"severity_{j['severity']}"] += 1
    conf = load(Path(a.claude_key) / 'CONFIRMATION_SCORES_2026-09-18.json')
    rows = []
    for m in sorted(agg):
        g = agg[m]
        rows.append({'model': m, 'answers_judged': g['answers'], 'valid_replies': g['valid'], 'judge_acceptable': g['acceptable'],
                     'judge_severity_None': g['severity_None'], 'judge_severity_Minor': g['severity_Minor'], 'judge_severity_Major': g['severity_Major'],
                     'judge_severity_Critical': g['severity_Critical'],
                     'researcher_confirmation_rescored': len(conf) if m == 'haiku' else 0,
                     'researcher_confirmed_serious': sum(c['acceptable'] == 'No' for c in conf) if m == 'haiku' else 0,
                     'note': 'AI-judged only; researcher confirmation scoring was not blind (done after seeing the judge view)' if m == 'haiku' else 'AI-judged only'})
    write(out, 'claude_extension_ai_judge.csv', rows)

    cites = load(Path(a.doc) / 'observations/auto_citation_check.json'); rows = []
    for folder, label in (('gemini', 'Gemini 3.1 Pro Preview'), ('kimi_optional', 'Kimi K3')):
        for p in sorted((Path(a.doc) / folder / 'run_records').glob('D*.json')):
            r = load(p); c = cites.get(f'{folder}|{r["run_id"]}', {})
            rows.append({'model': label, 'model_id': r.get('model_id_used'), 'provider': r.get('provider'), 'run': r['run_id'], 'case_id': r['case_id'],
                         'condition': r['condition'], 'status': r.get('status'), 'attempt': r.get('attempt'), 'latency_s': r.get('latency_seconds'),
                         'input_tokens': r.get('input_tokens'), 'output_tokens': r.get('output_tokens'), 'reasoning_tokens': r.get('reasoning_tokens'),
                         'cost_usd': r.get('actual_cost'), 'quotations': c.get('ncit'), 'quotations_found_verbatim': c.get('exact')})
    # run IDs D01-D12 are public extension run IDs (not masked); allow them explicitly
    path = out / 'document_extension_runs.csv'
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f'document_extension_runs.csv: {len(rows)} rows')

    write(out, 'metered_costs.csv', [
        {'item': 'AI judge (DeepSeek V4 Pro) on 96 primary answers', 'usd': 0.79, 'basis': 'OpenRouter activity records (US$0.80 including one practice prompt)'},
        {'item': 'AI judge (DeepSeek V4 Pro) on 48 matched Claude answers', 'usd': 0.99, 'basis': 'OpenRouter activity records (US$1.14 including replaced attempts)'},
        {'item': 'Gemini 3.1 Pro Preview, 12 document-extension runs', 'usd': 0.72, 'basis': 'OpenRouter-reported usage.cost per run'},
        {'item': 'Kimi K3, 12 document-extension runs', 'usd': 1.01, 'basis': 'OpenRouter-reported usage.cost per run'},
        {'item': 'Primary configurations (Astra, Luna) in Codex', 'usd': '', 'basis': 'Not measured: subscription access produced no per-answer usage records'},
    ])


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    for k in ('base', 'judge', 'claude-key', 'claude-judge', 'doc', 'out'):
        ap.add_argument('--' + k, required=True)
    main(ap.parse_args())
