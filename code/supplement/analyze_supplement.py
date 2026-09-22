"""Post-lock supplementary analysis for Package 21 (proposed in Package 22, 17 Sep 2026).

Labelled POST-FREEZE, PRE-UNMASKING: written before any score was locked or joined.
It never modifies frozen files. It reuses the frozen `metrics()` definition so that
primary numbers stay identical to `analyze.py`, and adds only what the frozen script
does not compute (see 05_POST-FREEZE_ANALYSIS_ADDENDUM):

  S1  scoring coverage and the explicit status of every scheduled answer
  S2  per-condition table values with case-cluster bootstrap intervals (single-arm)
  S3  routed-vs-blocked split of unnecessary withholding
  S4  catches and misses by the check that fired (replaces failure-class matching,
      because failure classes were never collected on the scoring form)
  S5  per-workflow (W1/W2/W3) table
  S6  two bounding sensitivities for unresolved answers (S6a least favourable to controls,
      S6b least favourable to direct release)
  S7  repetition consistency (acceptable in rep 1 vs rep 2, per model)
  S8  timing: primary summaries exclude flagged items (untimed interval > 5 min, pause or
      interruption, prior exposure not NO), per the pre-run plan; all-recorded as sensitivity
  S9  placeholder fill file keyed by the Package 22 paper placeholder IDs
  S10 case-level direction counts and S10b case trade-off classes
  S11 check applicability and block causes
  S12 criterion correctness (scheduled and scored-only)
  S13 handling decision in the timed exercise versus locked score class
  S14 exposure sensitivity: excluding answers handled in the timed exercise
  S15 inappropriate delegation (Critical severity) counts
  S16 frozen diagnostics and sensitivities surfaced as n/48 counts (if primary_summary.json exists)

Outputs go to <base>/analysis/supplement/ and contain model labels: keep private.

Usage (only after scoring/score_lock.json exists):
    python3 analyze_supplement.py --base "<path to 21_EXPERIMENT_EXECUTION_PACKAGE>"
"""
import argparse, json, random, statistics, sys
from pathlib import Path

sys.dont_write_bytecode = True  # never add __pycache__ inside the frozen code folder

MODELS = ['astra', 'luna']
PATHWAYS = ['direct', 'controlled']
COND = {('astra', 'direct'): 'a', ('astra', 'controlled'): 'b', ('luna', 'direct'): 'c', ('luna', 'controlled'): 'd'}
SEED = 2026091801  # frozen bootstrap seed from the registration record
RELEASED = ('release', 'release_with_warning')
T24 = 'T24'  # unresolved interruption during Clock 2 (addendum D10); sensitivity excludes it


def overlay_extension(joined, path):
    """Add the judgments recorded after the lock, for answers the study left unscored.

    The locked score file is never touched: this reads the extension's own score file and fills in
    `acceptable`, `severity` and the criterion judgments for answers whose locked status was not SCORED.
    An answer the study scored is never overwritten, and an answer neither has read stays unscored.
    """
    data = json.loads(Path(path).read_text())
    ext = {r['run_id']: r for r in data['records'] if r['status'] == 'SCORED'}
    added, refused = [], []
    for r in joined:
        e = ext.get(r['run_id'])
        if not e:
            continue
        if r['status'] == 'SCORED':
            refused.append(r['run_id'])
            continue
        r['status'] = 'SCORED'
        r['acceptable'] = bool(e['acceptable'])
        r['severity'] = e['severity']
        r['criteria_judgments'] = [c.get('judgment') for c in (e.get('criteria') or [])]
        r['score_source'] = 'extension'
        if r['pathway'] == 'direct':
            added.append(r['run_id'])
    if refused:
        raise ValueError(f'{len(refused)} answer(s) are scored in both files; locked scores are never revised: {sorted(refused)[:5]}')
    missing = sorted(set(ext) - {r['run_id'] for r in joined})
    if missing:
        raise ValueError(f'extension scores with no matching answer: {missing}')
    return {'answers_added': len(added), 'run_ids': sorted(added), 'source': str(path),
            'note': 'Judgments recorded after the score lock, for answers the study had left unread. '
                    'Locked scores are unchanged.'}


def load_frozen(base):
    sys.path.insert(0, str(base / 'code'))
    import experiment  # noqa: E402  (frozen module; imported read-only)
    return experiment


def percentile(xs, p):
    ys = sorted(xs); pos = (len(ys) - 1) * p; a = int(pos); b = min(a + 1, len(ys) - 1)
    return ys[a] + (ys[b] - ys[a]) * (pos - a)


def cluster_interval(rows, stat, n=10000, seed=SEED):
    """Resample cases (clusters) with replacement; rows of a case stay together."""
    cases = sorted({r['case_id'] for r in rows})
    by = {c: [r for r in rows if r['case_id'] == c] for c in cases}
    point = stat(rows)
    if point is None or len(cases) < 2:
        return {'point': point, 'interval': None, 'note': 'not estimable'}
    rng = random.Random(seed); draws = []
    for _ in range(n):
        sample = [r for c in rng.choices(cases, k=len(cases)) for r in by[c]]
        v = stat(sample)
        if v is not None:
            draws.append(v)
    if len(set(draws)) <= 1:
        return {'point': point, 'interval': None, 'note': 'degenerate resampling distribution'}
    return {'point': point, 'interval': [percentile(draws, .025), percentile(draws, .975)],
            'note': 'case-cluster percentile bootstrap; describes sensitivity to benchmark composition, not a population bound'}


def is_known(r):
    return r['available'] and r['acceptable'] is not None and r['severity'] is not None


def rate(num_pred, den_pred=None):
    def f(rows):
        den = [r for r in rows if (den_pred(r) if den_pred else True)]
        return (sum(num_pred(r) for r in den) / len(den)) if den else None
    return f


useful = lambda r: is_known(r) and r['acceptable'] is True and r['decision'] in RELEASED
serious_rel = lambda r: is_known(r) and r['severity'] in ('Major', 'Critical') and r['decision'] in RELEASED
acceptable = lambda r: is_known(r) and r['acceptable'] is True


def frac(n, d):
    return {'n': n, 'd': d, 'text': f'{n}/{d}' if d else f'{n}/0 (undefined)'}


def fmt_ci(ci, scale=100):
    if ci['point'] is None:
        return 'undefined'
    s = f"{ci['point'] * scale:.0f}%"
    if ci['interval']:
        s += f" [{ci['interval'][0] * scale:.0f}, {ci['interval'][1] * scale:.0f}]"
    return s


def fired_checks(r):
    return sorted({c['check'].split('_')[0] if c['check'].startswith('recompute_') else c['check']
                   for c in r.get('trace', []) if c.get('status') in ('FAIL', 'TRIGGERED', 'ERROR')})


def recompute_fail_reason(c):
    rep = c.get('reported') or []
    if len(rep) != 1:
        return 'duplicate_entries'
    delta = abs(rep[0]['value'] - c['computed_from_inputs'])
    if delta <= c['tolerance']:
        return 'unit_label_not_in_allow_list'
    if abs(rep[0]['value'] * 100 - c['computed_from_inputs']) <= c['tolerance']:
        return 'fraction_not_percent_scale'
    # display rounding (e.g. 22.2 for 22.22) only for 2-dp tolerances; course_grade is a table lookup
    return 'coarser_rounding_than_tolerance' if c['tolerance'] >= 0.005 and delta <= 0.05 else 'value_mismatch'


def check_applicability(rows):
    out = {'status_by_check': {}, 'numeric_cases_all_recompute_not_applicable': 0, 'block_causes': {}}
    for r in rows:
        if r['pathway'] != 'controlled' or not r.get('trace'):
            continue
        recompute = [c for c in r['trace'] if c['check'].startswith('recompute_')]
        if recompute and all(c['status'] == 'NOT_APPLICABLE' for c in recompute):
            out['numeric_cases_all_recompute_not_applicable'] += 1
        for c in r['trace']:
            name = 'recompute' if c['check'].startswith('recompute_') else c['check']
            d = out['status_by_check'].setdefault(name, {})
            d[c['status']] = d.get(c['status'], 0) + 1
        if r['decision'] == 'block':
            label = 'serious' if is_known(r) and r['severity'] in ('Major', 'Critical') else ('acceptable' if acceptable(r) else 'other_or_unscored')
            for c in r['trace']:
                if c['status'] in ('FAIL', 'ERROR'):
                    cause = c['check'] + (':' + recompute_fail_reason(c) if c['check'].startswith('recompute_') else '')
                    b = out['block_causes'].setdefault(cause, {})
                    b[label] = b.get(label, 0) + 1
    out['note'] = 'Exploratory. NOT_APPLICABLE means the check did not run on that answer (no citation, or quantity name not used).'
    return out


def build_join(base, ex):
    """Same join logic as the frozen analyze.py, without its failure-class matching."""
    ex.assert_frozen(base)
    lock = ex.read(base / 'scoring/score_lock.json')
    if ex.digest(base / 'scoring/researcher_scores.json') != lock['sha256']:
        raise ValueError('Locked scores changed')
    scores = {r['masked_id']: r for r in ex.read(base / 'scoring/researcher_scores.json')}
    key = {r['run_id']: r for r in ex.read(base / 'private/identity_key.json')}
    raw = {r['run_id']: r for r in ex.read(base / 'private/imported_primary.json')}
    joined = []
    for path in ex.read(base / 'private/pathways.json'):
        k = key[path['run_id']]; s = scores[k['masked_id']]; rr = raw[path['run_id']]
        known = s['status'] == 'SCORED'
        crit = s.get('criteria') or []
        joined.append({**path, 'model': k['model'], 'repetition': int(k['repetition']), 'masked_id': k['masked_id'],
                       'status': s['status'],
                       'available': rr['record_status'] == 'RECEIVED' and not rr.get('quarantine'),
                       'acceptable': s.get('acceptable') if known else None,
                       'severity': s.get('severity') if known else None,
                       'criteria_judgments': [c.get('judgment') for c in crit],
                       'reference_challenge': bool((s.get('reference_challenge') or '').strip()),
                       'prior_timing_exposure': bool(s.get('prior_timing_exposure'))})
    return joined, scores


def condition_block(rows):
    n = len(rows)
    acc = [r for r in rows if acceptable(r)]
    withheld_acc = [r for r in acc if r['decision'] not in RELEASED]
    ser = [r for r in rows if is_known(r) and r['severity'] in ('Major', 'Critical')]
    return {
        'scheduled': n,
        'scored': sum(is_known(r) for r in rows),
        'acceptable': frac(len(acc), n),
        'other_unacceptable': frac(sum(is_known(r) and r['acceptable'] is False and r['severity'] not in ('Major', 'Critical') for r in rows), n),
        'unscored': frac(sum(not is_known(r) for r in rows), n),
        'serious_released': frac(sum(serious_rel(r) for r in rows), n),
        'serious_released_ci': cluster_interval(rows, rate(serious_rel)),
        'useful_release': frac(sum(useful(r) for r in rows), n),
        'useful_release_ci': cluster_interval(rows, rate(useful)),
        'unnecessary_withholding': frac(len(withheld_acc), len(acc)),
        'withheld_acceptable_routed': sum(r['decision'] == 'route' for r in withheld_acc),
        'withheld_acceptable_blocked': sum(r['decision'] == 'block' for r in withheld_acc),
        'serious_withheld': frac(sum(r['decision'] not in RELEASED for r in ser), len(ser)),  # = serious answers withheld
        'decisions': {d: sum(r['decision'] == d for r in rows) for d in sorted({r['decision'] for r in rows})},
    }


def checks_table(rows):
    """S4: for controlled rows, which checks fired on serious vs acceptable answers."""
    out = {}
    for r in rows:
        if r['pathway'] != 'controlled' or not is_known(r):
            continue
        label = 'serious' if r['severity'] in ('Major', 'Critical') else ('acceptable' if r['acceptable'] else 'other_unacceptable')
        for chk in fired_checks(r) or ['none_fired']:
            out.setdefault(chk, {'serious': 0, 'acceptable': 0, 'other_unacceptable': 0})[label] += 1
    order = ['schema', 'quoted_source_membership', 'recompute', 'consequential_action_routing', 'runtime']
    first = {}
    for r in rows:
        if r['pathway'] != 'controlled' or not is_known(r) or r['decision'] in RELEASED:
            continue
        label = 'serious' if r['severity'] in ('Major', 'Critical') else ('acceptable' if r['acceptable'] else 'other_unacceptable')
        fired = fired_checks(r)
        f = next((o for o in order if o in fired), 'unknown')
        first.setdefault(f, {'serious': 0, 'acceptable': 0, 'other_unacceptable': 0})[label] += 1
    missed = sum(1 for r in rows if r['pathway'] == 'controlled' and serious_rel(r))
    return {'fired_by_outcome': out, 'withheld_by_first_check': first, 'serious_released_despite_controls': missed,
            'note': 'A check firing on a serious answer is a coarse catch; whether it fired for the right reason needs case inspection. fired_by_outcome rows can sum to more than answers because several checks may fire; withheld_by_first_check partitions withheld answers.'}


def timing_summary(base, ex, key_by_run):
    session = ex.read(base / 'timing/session.json')
    assignment = ex.read(base / 'private/timing_assignment.json')
    events = {}
    for e in session['events']:
        events.setdefault(e['timing_id'], []).append(e)
    rows = []
    for a in assignment:
        tid = a.get('timing_id'); item = session['items'].get(tid)
        if not item:
            continue
        model = a.get('model') or key_by_run.get(a.get('run_id'), {}).get('model')
        ev = {e['action']: e['at'] for e in events.get(tid, [])}
        gap = None
        end = next((ev[x] for x in ('finalize_start', 'no_work') if x in ev), None)  # T16 ends with no_work
        if 'decide' in ev and end:
            from datetime import datetime
            gap = (datetime.fromisoformat(end) - datetime.fromisoformat(ev['decide'])).total_seconds()
        flagged = bool((gap and gap > 300) or item.get('pauses') or tid == T24 or item.get('prior_exposure', 'NO') != 'NO')
        rows.append({'timing_id': tid, 'run_id': a.get('run_id'), 'flagged': flagged, 'prior_exposure': item.get('prior_exposure'),
                     'model': model, 'pathway': a.get('pathway'), 'case_id': a.get('case_id'),
                     'clock1': item['clock1_seconds'], 'clock2': item['clock2_seconds'],
                     'decision': item['decision'], 'completion_status': item['completion_status'],
                     'inspect_override': item['inspect_override'], 'untimed_gap_seconds': gap})

    if len(rows) != len(assignment):
        raise ValueError(f'timing join incomplete: {len(rows)} of {len(assignment)} assigned items found in session')
    if any(r['model'] not in MODELS or r['pathway'] not in PATHWAYS for r in rows):
        raise ValueError('timing row without a recognised model or pathway')
    if T24 not in {r['timing_id'] for r in rows}:
        raise ValueError(T24 + ' not found; the exclusion sensitivity would be silently empty')

    cell_sizes = {f'{m}_{p}': sum((r['model'], r['pathway']) == (m, p) for r in rows) for m in MODELS for p in PATHWAYS}
    cell_warning = None if all(v == 6 for v in cell_sizes.values()) else 'timing cells are not 6 each: ' + json.dumps(cell_sizes)

    def summ(rs, field):
        xs = [r[field] for r in rs]
        return {'median': statistics.median(xs), 'min': min(xs), 'max': max(xs), 'n': len(xs),
                'text': f"{statistics.median(xs):.0f} ({min(xs):.0f}–{max(xs):.0f}; {len(xs)})"} if xs else None

    out = {}
    for m in MODELS:
        for p in PATHWAYS:
            rs = [r for r in rows if r['model'] == m and r['pathway'] == p]
            clean = [r for r in rs if r['timing_id'] != T24]
            primary = [r for r in rs if not r['flagged']]
            out[f'{m}_{p}'] = {'primary_clock1': summ(primary, 'clock1'),
                               'primary_items_with_correction': f"{sum(r['clock2'] > 0 for r in primary)}/{len(primary)}",
                               'primary_clock2_among_corrected': summ([r for r in primary if r['clock2'] > 0], 'clock2'),
                               'excluded_items': [r['timing_id'] for r in rs if r['flagged']],
                               'clock1': summ(rs, 'clock1'), 'clock2': summ(rs, 'clock2'),
                               'clock1_excluding_T24': summ(clean, 'clock1'),
                               'clock2_excluding_T24': summ(clean, 'clock2'),
                               'items_with_clock2_work': sum(r['clock2'] > 0 for r in rs),
                               'clock2_among_worked_items': summ([r for r in rs if r['clock2'] > 0], 'clock2'),
                               'decisions': {d: sum(r['decision'] == d for r in rs) for d in sorted({r['decision'] for r in rs})},
                               'overrides': sum(r['inspect_override'] for r in rs)}
    flags = [r['timing_id'] for r in rows if r['untimed_gap_seconds'] and r['untimed_gap_seconds'] > 300]
    return {'by_condition': out, 'cell_sizes': cell_sizes, 'cell_warning': cell_warning, 'untimed_gap_over_5_min': flags, 'flagged_items': [r['timing_id'] for r in rows if r['flagged']],
            'rule': 'Primary summaries exclude flagged items (pre-run plan: clean records primary); all-recorded summaries are sensitivity.',
            'note': 'Single familiar researcher, one item per case; describes this study only.'}, rows


def analyze(base, extension_scores=None, out_name='supplement_results.json'):
    ex = load_frozen(base)
    joined, scores = build_join(base, ex)
    overlay = overlay_extension(joined, extension_scores) if extension_scores else None
    key_by_run = {r['run_id']: r for r in ex.read(base / 'private/identity_key.json')}
    inst = {c: ex.read(base / f'inputs/{c}.json')['institution'] for c in sorted({r['case_id'] for r in joined})}
    res = {'label': 'POST-FREEZE SUPPLEMENT (Package 22 proposal); primary definitions from frozen metrics()'}
    if overlay:
        res['label'] += '; with the answers read after the lock'
        res['extension_overlay'] = overlay

    # S1 coverage
    answers = [r for r in joined if r['pathway'] == 'direct']
    st = [r['status'] for r in answers] if overlay else [s['status'] for s in scores.values()]
    res['S1_coverage'] = {k: st.count(k) for k in ['SCORED', 'MISSING', 'CANNOT_JUDGE']} | {'scheduled': len(st),
                         'reference_challenges': sum(bool((s.get('reference_challenge') or '').strip()) for s in scores.values())}

    # S2/S3 per condition, identical scheduled denominators to frozen metrics()
    res['S2_conditions'] = {f'{m}_{p}': condition_block([r for r in joined if r['model'] == m and r['pathway'] == p])
                            for m in MODELS for p in PATHWAYS}
    res['frozen_metrics_crosscheck'] = {f'{m}_{p}': ex.metrics([r for r in joined if r['model'] == m and r['pathway'] == p])
                                        for m in MODELS for p in PATHWAYS}
    for k, b in res['S2_conditions'].items():
        fm = res['frozen_metrics_crosscheck'][k]
        if b['useful_release']['n'] != fm['useful_release_n'] or b['serious_released']['n'] != fm['serious_release_n']:
            raise ValueError('supplement counts disagree with frozen metrics() for ' + k)
    if overlay:
        # S16 restates the frozen script's own output, which describes the locked scores only.
        res['S16_note'] = ('The frozen diagnostics and sensitivities are not restated here: they are the frozen '
                           'script\'s output over the locked scores. Bounds (S6), exposure (S14) and the '
                           'per-condition tables above are recomputed over every answer read.')
    res['S4_checks'] = checks_table(joined)
    res['S5_workflow'] = {w: {f'{m}_{p}': condition_block([r for r in joined if r['case_id'].startswith(w) and r['model'] == m and r['pathway'] == p])
                              for m in MODELS for p in PATHWAYS} for w in ['W1', 'W2', 'W3']}

    # S6 bounding: unresolved = available and (unscored, or unacceptable without a Major/Critical error)
    unres = lambda r: r['available'] and (not is_known(r) or (r['acceptable'] is False and r['severity'] not in ('Major', 'Critical')))
    s6a = [dict(r, status='SCORED', acceptable=(r['decision'] not in RELEASED), severity=('None' if r['decision'] not in RELEASED else 'Major')) if unres(r) else r for r in joined]
    s6b = [dict(r, status='SCORED', acceptable=False, severity='Major') if unres(r) else r for r in joined]
    res['S6a_least_favourable_to_controls'] = {f'{m}_{p}': condition_block([r for r in s6a if r['model'] == m and r['pathway'] == p]) for m in MODELS for p in PATHWAYS}
    res['S6b_least_favourable_to_direct'] = {f'{m}_{p}': condition_block([r for r in s6b if r['model'] == m and r['pathway'] == p]) for m in MODELS for p in PATHWAYS}
    res['S6_note'] = 'In S6a the direct pathway treats every unresolved answer as serious because direct releases everything. Interpret serious_released and useful_release only.'

    rep = {}
    for m in MODELS:
        pairs = []
        for c in inst:
            a = {r['repetition']: r['acceptable'] for r in joined if r['model'] == m and r['case_id'] == c and r['pathway'] == 'direct'}
            if a.get(1) is not None and a.get(2) is not None:
                pairs.append((a[1], a[2]))
        rep[m] = {'cases_with_both': len(pairs), 'same_label': sum(x == y for x, y in pairs),
                  'acceptable_both': sum(x and y for x, y in pairs), 'acceptable_neither': sum((not x) and (not y) for x, y in pairs)}
    res['S7_repetition_consistency'] = rep

    # S10 case-level direction counts (exact, no distributional assumption; Bowyer et al., 2025)
    direction = {}
    for m in MODELS:
        for metric, pred in [('useful_release', useful), ('serious_release', serious_rel)]:
            better = worse = same = not_evaluable = 0
            for c in inst:
                if any(r['available'] and not is_known(r) for r in joined if r['case_id'] == c and r['model'] == m):
                    not_evaluable += 1
                    continue
                v = {p: sum(pred(r) for r in joined if r['case_id'] == c and r['model'] == m and r['pathway'] == p) for p in PATHWAYS}
                d = v['controlled'] - v['direct']
                good_dir = d > 0 if metric == 'useful_release' else d < 0
                bad_dir = d < 0 if metric == 'useful_release' else d > 0
                better += good_dir; worse += bad_dir; same += d == 0
            direction[f'{m}_{metric}'] = {'cases_controls_better': better, 'cases_controls_worse': worse, 'cases_unchanged': same,
                                          'cases_not_evaluable': not_evaluable}
    res['S10_case_direction'] = direction
    # Controls reuse the direct answer and can only withhold, so each single-metric count is one-sided
    # by construction. The case trade-off class shows both sides together.
    tradeoff = {}
    for m in MODELS:
        cls = dict.fromkeys(['withheld_only_serious', 'withheld_only_acceptable', 'withheld_both', 'withheld_neither', 'not_evaluable'], 0)
        for c in inst:
            rc = [r for r in joined if r['case_id'] == c and r['model'] == m and r['pathway'] == 'controlled']
            if any(r['available'] and not is_known(r) for r in rc):
                cls['not_evaluable'] += 1
                continue
            contained = sum(is_known(r) and r['severity'] in ('Major', 'Critical') and r['decision'] not in RELEASED for r in rc)
            lost = sum(acceptable(r) and r['decision'] not in RELEASED for r in rc)
            cls['withheld_both' if contained and lost else 'withheld_only_serious' if contained else 'withheld_only_acceptable' if lost else 'withheld_neither'] += 1
        tradeoff[m] = cls
    res['S10b_case_tradeoff'] = tradeoff

    # S11 check applicability and block causes (controlled rows): exposes silently skipped checks
    res['S11_check_applicability'] = check_applicability(joined)

    # S12 criterion correctness (R-10): scheduled (unscored or unresolved = 0; differs from frozen analyze.py for partially judged CANNOT_JUDGE rows) and scored-only
    corr = {}
    for m in MODELS:
        sched, scored = [], []
        for c in inst:
            fr = []
            for r in joined:
                if r['model'] == m and r['case_id'] == c and r['pathway'] == 'direct':
                    js = r['criteria_judgments']
                    fr.append(sum(j == 'Correct' for j in js) / len(js) if is_known(r) and js else None)
            sched.append(statistics.mean(x or 0 for x in fr))
            if any(x is not None for x in fr):
                scored.append(statistics.mean(x for x in fr if x is not None))
        corr[m] = {'scheduled_case_mean': statistics.mean(sched), 'scored_case_mean': statistics.mean(scored) if scored else None,
                   'cases_with_any_scored_answer': len(scored)}
    ps_path = base / 'analysis/primary_summary.json'
    if ps_path.exists():
        frozen_corr = ex.read(ps_path).get('correctness', {})
        for m in MODELS:
            corr[m]['frozen_case_macro_scheduled_correctness'] = frozen_corr.get(m, {}).get('case_macro_scheduled_correctness')
    res['S12_criterion_correctness'] = corr

    trows = []
    try:
        res['S8_timing'], trows = timing_summary(base, ex, key_by_run)
    except (FileNotFoundError, KeyError, ValueError) as e:
        res['S8_timing'] = {'status': f'not computed: {type(e).__name__}: {e}'}

    # S13 handling decision versus locked score class (does the human in the loop catch errors?)
    idx = {(r['run_id'], r['pathway']): r for r in joined}
    cells = {}
    for t in trows:
        j = idx.get((t['run_id'], t['pathway']))
        q = ('unscored' if not j or not is_known(j) else 'serious' if j['severity'] in ('Major', 'Critical')
             else 'acceptable' if j['acceptable'] else 'other_unacceptable')
        k = f"{t['pathway']}|{t['decision']}|{q}"
        cells[k] = cells.get(k, 0) + 1
    res['S13_handler_vs_score'] = {'cells': cells, 'n': len(trows),
                                   'serious_scored_items': sum(v for k, v in cells.items() if k.endswith('|serious')),
                                   'serious_accepted_without_edit': sum(v for k, v in cells.items() if k.endswith('|accept|serious')),
                                   'note': 'One familiar researcher; bounds rather than estimates reviewer miss rates. Whether edits removed errors needs inspection of saved final products.'}

    # S14 exposure sensitivity
    exposed_controlled = {t['run_id'] for t in trows if t['pathway'] == 'controlled'}
    res['S14_exposure'] = {
        'excluding_all_timed_answers': {f'{m}_{p}': condition_block([r for r in joined if r['model'] == m and r['pathway'] == p and not r['prior_timing_exposure']]) for m in MODELS for p in PATHWAYS},
        'excluding_controlled_timed_answers': {f'{m}_{p}': condition_block([r for r in joined if r['model'] == m and r['pathway'] == p and r['run_id'] not in exposed_controlled]) for m in MODELS for p in PATHWAYS},
    }

    # S15 inappropriate delegation = Critical severity (pre-run definition); direct rows count each answer once
    res['S15_delegation'] = {m: {
        'critical_n': sum(1 for r in joined if r['model'] == m and r['pathway'] == 'direct' and is_known(r) and r['severity'] == 'Critical'),
        'scored_n': sum(1 for r in joined if r['model'] == m and r['pathway'] == 'direct' and is_known(r)),
        'critical_W2_n': sum(1 for r in joined if r['model'] == m and r['pathway'] == 'direct' and is_known(r) and r['severity'] == 'Critical' and r['case_id'].startswith('W2')),
        'critical_released_controlled_n': sum(1 for r in joined if r['model'] == m and r['pathway'] == 'controlled' and is_known(r) and r['severity'] == 'Critical' and r['decision'] in RELEASED),
        'note': 'Over-referral was not recorded as a field; report only documented instances from criterion reasons.'} for m in MODELS}

    # S16 surface frozen diagnostics and sensitivities as counts
    ps = base / 'analysis/primary_summary.json'
    if ps.exists():
        prim = ex.read(ps); surf = {}
        for rule, by_model in prim.get('diagnostics', {}).items():
            if rule == 'always_release':
                continue
            for m, mm in by_model.items():
                surf[f'diag|{rule}|{m}'] = f"serious released {mm['serious_release_n']}/{mm['scheduled_n']}; useful {mm['useful_release_n']}/{mm['scheduled_n']}"
        for name, grp in prim.get('sensitivity_analyses', {}).items():
            if name == 'leave_one_institution_out':
                for inst_name, g in grp.items():
                    for cond, mm in g.items():
                        surf[f'sens|loio:{inst_name}|{cond}'] = f"serious {mm['serious_release_n']}/{mm['scheduled_n']}; useful {mm['useful_release_n']}/{mm['scheduled_n']}"
            elif isinstance(grp, dict) and all(isinstance(v, dict) and 'scheduled_n' in v for v in grp.values()):
                for cond, mm in grp.items():
                    surf[f'sens|{name}|{cond}'] = f"serious {mm['serious_release_n']}/{mm['scheduled_n']}; useful {mm['useful_release_n']}/{mm['scheduled_n']}"
        res['S16_frozen_surfaced'] = surf

    if overlay:
        # S17 restates the frozen script's diagnostics and sensitivities over every answer read, using the
        # same subsets and the same definitions. S16 keeps the frozen script's own output for the locked set.
        POST_AUDIT = ['W1-04', 'W1-07', 'W2-03', 'W3-01', 'W3-03', 'W3-06']
        INTERPRETATION_SENSITIVE = ['W1-04', 'W1-08']
        judgment_cases = [c for c in inst if c.startswith(('W1', 'W2'))]
        sens = {}

        def block(rows_):
            return {f'{m}_{p}': condition_block([r for r in rows_ if r['model'] == m and r['pathway'] == p])
                    for m in MODELS for p in PATHWAYS}

        sens['repetition_1'] = block([r for r in joined if r['repetition'] == 1])
        sens['repetition_2'] = block([r for r in joined if r['repetition'] == 2])
        sens['omit_interpretation_sensitive'] = block([r for r in joined if r['case_id'] not in INTERPRETATION_SENSITIVE])
        sens['omit_post_audit_changes'] = block([r for r in joined if r['case_id'] not in POST_AUDIT])
        for name in sorted(set(inst.values())):
            sens[f'loio:{name}'] = block([r for r in joined if inst[r['case_id']] != name])
        # Critical-only: a Major error no longer counts as serious, so only Critical can be a serious release.
        sens['critical_only'] = block([dict(r, severity='Minor' if r['severity'] == 'Major' else r['severity'])
                                       for r in joined])
        diag = {
            'always_withhold': {m: {'useful_release_n': 0, 'serious_release_n': 0,
                                    'scheduled_n': sum(1 for r in joined if r['model'] == m and r['pathway'] == 'direct')}
                                for m in MODELS},
            'structural_only': {m: {'useful_release_n': sum(1 for r in joined if r['model'] == m and r['pathway'] == 'direct' and acceptable(r)),
                                    'serious_release_n': sum(1 for r in joined if r['model'] == m and r['pathway'] == 'direct' and is_known(r) and r['severity'] in ('Major', 'Critical')),
                                    'scheduled_n': sum(1 for r in joined if r['model'] == m and r['pathway'] == 'direct')}
                                for m in MODELS},
            'stratum_routing_only': {m: {'useful_release_n': sum(1 for r in joined if r['model'] == m and r['pathway'] == 'direct' and acceptable(r) and r['case_id'] not in judgment_cases),
                                         'serious_release_n': sum(1 for r in joined if r['model'] == m and r['pathway'] == 'direct' and is_known(r) and r['severity'] in ('Major', 'Critical') and r['case_id'] not in judgment_cases),
                                         'scheduled_n': sum(1 for r in joined if r['model'] == m and r['pathway'] == 'direct')}
                                     for m in MODELS},
        }
        res['S17_recomputed_sensitivities'] = {
            'sensitivities': sens, 'diagnostics': diag,
            'not_computed': {'unmatched_serious_catches_as_released': 'failure classes were not collected on the '
                                                                      'study scoring form, so there is nothing to match',
                             'not_scorable_as_unacceptable': 'no answer read was marked impossible to judge'},
            'note': 'Same subsets and definitions as the frozen script, recomputed over every answer read.'}

    res['S9_placeholders'] = placeholders(res)
    out = base / 'analysis/supplement'
    ex.write(out / out_name, res)
    ex.write(out / out_name.replace('supplement_results', 'placeholder_values'), res['S9_placeholders'])
    return res


def placeholders(res):
    """Map computed values to Package 22 paper placeholder IDs. Narrative IDs stay for the author."""
    p = {}
    for (m, path), s in COND.items():
        c = res['S2_conditions'][f'{m}_{path}']
        p[f'R-11{s}'] = f"{c['acceptable']['text']}; other unacceptable {c['other_unacceptable']['n']}; unscored {c['unscored']['n']}"
        p[f'R-12{s}'] = f"{c['serious_released']['text']} ({fmt_ci(c['serious_released_ci'])})"
        p[f'R-13{s}'] = f"{c['useful_release']['text']} ({fmt_ci(c['useful_release_ci'])})"
        if path == 'controlled':
            p[f'R-14{s}'] = f"{c['unnecessary_withholding']['text']} (routed {c['withheld_acceptable_routed']}, blocked {c['withheld_acceptable_blocked']})"
            p[f'R-15{s}'] = f"{c['serious_withheld']['text']}"  # serious answers withheld
        for w in ['W1', 'W2', 'W3']:
            wc = res['S5_workflow'][w][f'{m}_{path}']
            idx = 'abcd'.index(s) + 1
            p[f'R-{w}-{idx}-SERIOUS'] = wc['serious_released']['text']
            p[f'R-{w}-{idx}-USEFUL'] = wc['useful_release']['text']
            if path == 'controlled':
                p[f'R-{w}-{idx}-WITHHELD'] = wc['unnecessary_withholding']['text']
    t = res.get('S8_timing', {}).get('by_condition')
    if t:
        for (m, path), s in COND.items():
            tc = t[f'{m}_{path}']
            pc1 = tc['primary_clock1']['text'] if tc['primary_clock1'] else 'no unflagged items'
            p[f'R-33{s}'] = f"{pc1}; all recorded {tc['clock1']['text'] if tc['clock1'] else 'none'}"
            among = tc['primary_clock2_among_corrected']
            p[f'R-34{s}'] = f"{tc['primary_items_with_correction']} with correction" + (f"; median {among['median']:.0f} ({among['min']:.0f}–{among['max']:.0f})" if among else '')
    for m in MODELS:
        for metric in ['useful_release', 'serious_release']:
            d = res['S10_case_direction'][f'{m}_{metric}']
            p[f'R-17-{m}-{metric}'] = (f"one-sided; do not report alone: controls better in {d['cases_controls_better']}, worse in {d['cases_controls_worse']}, "
                                       f"unchanged in {d['cases_unchanged']}, not evaluable in {d['cases_not_evaluable']} of {sum(d.values())} cases")
        t2 = res['S10b_case_tradeoff'][m]
        p[f'R-17-{m}-tradeoff'] = ', '.join(f"{k.replace('_', ' ')} {v}" for k, v in t2.items())
        cc = res['S12_criterion_correctness'][m]
        p['R-10' + ('a' if m == 'astra' else 'c')] = (f"{cc['scheduled_case_mean']:.2f} scheduled; "
                                                     + (f"{cc['scored_case_mean']:.2f} among scored ({cc['cases_with_any_scored_answer']} cases)" if cc['scored_case_mean'] is not None else 'no scored answers'))
    for m in MODELS:
        d = res['S15_delegation'][m]
        p[f'R-16-delegation-{m}'] = f"Critical {d['critical_n']}/{d['scored_n']} scored answers (W2: {d['critical_W2_n']}); released under controls {d['critical_released_controlled_n']}"
    h = res.get('S13_handler_vs_score')
    if h:
        p['R-36'] = f"{h['serious_scored_items']} of {h['n']} timed answers scored serious; {h['serious_accepted_without_edit']} accepted without edit"
    cov = res['S1_coverage']
    p['R-00-coverage'] = f"{cov['SCORED']} scored, {cov['CANNOT_JUDGE']} cannot judge, {cov['MISSING']} missing of {cov['scheduled']}; {cov['reference_challenges']} reference challenges"
    return p


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--base', required=True)
    ap.add_argument('--extension-scores', help='score file from the extension, overlaid on answers the study left unread')
    ap.add_argument('--out-name', default='supplement_results.json')
    args = ap.parse_args()
    res = analyze(Path(args.base), args.extension_scores, args.out_name)
    if res.get('extension_overlay'):
        print(f"{res['extension_overlay']['answers_added']} answer(s) read after the lock were added.")
    print(f"Supplement written to analysis/supplement/{args.out_name} (contains model labels; keep private).")
