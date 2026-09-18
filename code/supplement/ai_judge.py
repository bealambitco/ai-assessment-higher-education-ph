"""Agreement (and optional API runner) for the AI-judge package (23_AI_JUDGE_EXTENSION_PACKAGE).

All 96 DeepSeek replies were already collected manually on September 18 (04:08-04:56). Use --agree after the
human lock and after `code/process_outputs.py --write`. The runner below is only for future sets (for example Claude answers).

It sends each prepared prompt (prompts/J###_full_prompt.txt) unchanged, as one message in a fresh request,
and saves the complete reply into the matching empty raw_outputs/J###_raw.txt. It fills the run record
with what the API returns (model, provider, usage, cost). It never edits a non-empty raw file, never
re-asks for a different judgment, and never reads human scores. Parse afterwards with the package's own
code/process_outputs.py --write. This replaces manual copy and paste; the prompts and rubric are the package's.

Run it yourself. It calls OpenRouter with your key and incurs charges.

  export OPENROUTER_API_KEY=...                  # never paste the key into a file
  python3 ai_judge.py --package "<23_AI_JUDGE_EXTENSION_PACKAGE>" --first 48 --dry-run
  python3 ai_judge.py --package "<23_AI_JUDGE_EXTENSION_PACKAGE>" --first 48
  python3 -B "<23_...>/code/process_outputs.py" --write

Then, after the human scores are locked:
  python3 ai_judge.py --package "<23_...>" --agree --base "<21_EXPERIMENT_EXECUTION_PACKAGE>"
"""
import argparse, hashlib, json, os, re, sys, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
API = 'https://openrouter.ai/api/v1/chat/completions'


def now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')


def priority_order(pkg):
    text = (pkg / '01_COLLECTION_INDEX.md').read_text()
    seen = []
    for j in re.findall(r'\b([JK]\d{3})\b', text):
        if j not in seen:
            seen.append(j)
    return seen


PROVIDER = None


def call(model, prompt, key, temperature, max_tokens, effort=None):
    prov = {'allow_fallbacks': False}
    if PROVIDER:
        prov['order'] = PROVIDER
    body = {'model': model, 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': max_tokens,
            'usage': {'include': True}, 'provider': prov}
    if temperature is not None:
        body['temperature'] = temperature
    if effort:
        body['reasoning'] = {'effort': effort}
    req = urllib.request.Request(API, data=json.dumps(body).encode(), headers={
        'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'X-Title': 'Assessment benchmark AI judge'})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def run(a):
    pkg = Path(a.package)
    setup = json.loads((pkg / 'protocol/JUDGE_SETUP.json').read_text())
    model = a.model or setup.get('confirmed_selected_model_id')
    if not model:
        raise SystemExit('No model ID. Pass --model.')
    ids = a.ids or priority_order(pkg)[:a.first]
    key = os.environ.get('OPENROUTER_API_KEY')
    if not a.dry_run and not key:
        raise SystemExit('Set OPENROUTER_API_KEY in your shell first.')
    import threading
    from concurrent.futures import ThreadPoolExecutor
    lock = threading.Lock(); costs = []

    def one(j):
            raw = pkg / 'raw_outputs' / f'{j}_raw.txt'
            rec_path = pkg / 'run_records' / f'{j}.json'
            rec = json.loads(rec_path.read_text())
            if raw.exists() and raw.read_text().strip():
                print(j, 'skipped: raw reply already saved'); return
            prompt = (pkg / 'prompts' / f'{j}_full_prompt.txt').read_text()
            sha = hashlib.sha256(prompt.encode()).hexdigest()
            if rec.get('prompt_sha256') and rec['prompt_sha256'] != sha:
                raise SystemExit(f'{j}: prompt hash differs from the prepared record; stop and check the package.')
            if a.dry_run:
                print(f'{j}: would send {len(prompt)} characters to {model}; prompt hash matches'); return
            reply, resp, errors = None, None, []
            for attempt in (1, 2, 3):  # technical retries only (network or empty reply)
                started = now()
                try:
                    resp = call(model, prompt, key, a.temperature, a.max_tokens, a.reasoning)
                    reply = ((resp.get('choices') or [{}])[0].get('message') or {}).get('content')
                    if reply:
                        break
                    errors.append({'attempt': attempt, 'error': 'empty reply', 'at': started})
                except (urllib.error.URLError, TimeoutError) as e:
                    errors.append({'attempt': attempt, 'error': str(e), 'at': started})
                time.sleep(5 * attempt)
            finished = now()
            if not reply:
                rec.update({'record_status': 'TECHNICAL_FAILURE', 'exception_notes': json.dumps(errors)})
                rec_path.write_text(json.dumps(rec, indent=2)); print(j, 'FAILED'); return
            raw.write_text(reply)
            usage = resp.get('usage') or {}
            rec.update({'record_status': 'RAW_SAVED', 'started_at': started, 'finished_at': finished,
                        'actual_model_id': resp.get('model'), 'interface': 'OpenRouter API, chat/completions, one request per run',
                        'reasoning_setting': f'OpenRouter reasoning effort={a.reasoning}' if a.reasoning else 'provider default (not set by the runner)',
                        'temperature_setting': a.temperature if a.temperature is not None else 'provider default',
                        'provider': resp.get('provider'), 'usage': usage, 'cost': usage.get('cost'),
                        'prompt_unchanged': True, 'fresh_chat': True, 'tools_or_attachments_used': False,
                        'exception_notes': json.dumps(errors) if errors else ''})
            rec_path.write_text(json.dumps(rec, indent=2))
            costs.append(usage.get('cost') or 0)
            print(j, 'saved', resp.get('model'), resp.get('provider'), f"US${usage.get('cost') or 0:.4f}")

    if a.dry_run or a.workers <= 1:
        for j in ids:
            one(j)
    else:
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            list(ex.map(one, ids))
    total_cost = sum(costs)
    print(f'Done. Reported cost this run: US${total_cost:.4f}. Next: python3 -B code/process_outputs.py --write')


def kappa2(pairs):
    n = len(pairs)
    if not n:
        return None
    po = sum(a == b for a, b in pairs) / n
    pa = sum(a for a, _ in pairs) / n; pb = sum(b for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else round((po - pe) / (1 - pe), 3)


def table(pairs):
    return {'n': len(pairs), 'both_yes': sum(a and b for a, b in pairs), 'human_yes_judge_no': sum(a and not b for a, b in pairs),
            'human_no_judge_yes': sum(b and not a for a, b in pairs), 'both_no': sum((not a) and (not b) for a, b in pairs),
            'raw_agreement': round(sum(a == b for a, b in pairs) / len(pairs), 3) if pairs else None, 'kappa': kappa2(pairs)}


def agree(a):
    """Agreement with the locked human scores. Reads the package's alias map (judge ID to masked ID only)."""
    pkg, base = Path(a.package), Path(a.base)
    lock = base / 'scoring/score_lock.json'
    if not lock.exists():
        raise SystemExit('Human scores are not locked.')
    amap = {r['judge_id']: r['human_masked_id'] for r in json.loads((pkg / 'private/JUDGE_TO_HUMAN_MASKED_MAP.json').read_text())}
    human = {r['masked_id']: r for r in json.loads((base / 'scoring/researcher_scores.json').read_text()) if r['status'] == 'SCORED'}
    ser, acc, crit, exact, dis = [], [], [], [], []
    for f in sorted((pkg / 'parsed_outputs').glob('J*.json')):
        d = json.loads(f.read_text()); j = f.stem
        g = d.get('judgment') if isinstance(d.get('judgment'), dict) else (d if d.get('criteria') else {})
        mid = amap.get(j)
        if not g or mid not in human:
            continue
        h = human[mid]; hs = (h.get('severity') or '').lower(); js = str(g.get('severity', '')).lower()
        if js in ('', 'cannot judge'):
            continue
        ser.append((hs in ('major', 'critical'), js in ('major', 'critical')))
        ja = str(g.get('acceptable', '')).lower() == 'yes'
        acc.append((bool(h.get('acceptable')), ja)); exact.append(hs == js)
        jc = {int(c.get('criterion')): str(c.get('judgment', '')).lower() for c in g.get('criteria', []) if str(c.get('criterion', '')).isdigit()}
        for c in h['criteria']:
            if c.get('judgment') and c['criterion'] in jc:
                crit.append((c['judgment'].lower() == 'correct', jc[c['criterion']] == 'correct'))
        if hs != js or bool(h.get('acceptable')) != ja:
            dis.append({'judge_id': j, 'masked_id': mid, 'case_id': h.get('case_id'), 'human': [h.get('severity'), h.get('acceptable')], 'judge': [g.get('severity'), g.get('acceptable')]})
    res = {'label': 'EXPLORATORY: AI judge agreement with locked human scores; a cross-check, never the decider',
           'answers_compared': len(ser), 'serious_error': table(ser), 'acceptable': table(acc), 'criterion_correct': table(crit),
           'severity_exact': round(sum(exact) / len(exact), 3) if exact else None, 'disagreements_for_review': dis}
    out = pkg / 'analysis'; out.mkdir(exist_ok=True)
    (out / 'agreement_with_human.json').write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != 'disagreements_for_review'}, indent=1))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--package', required=True); ap.add_argument('--model'); ap.add_argument('--ids', nargs='*')
    ap.add_argument('--first', type=int, default=48); ap.add_argument('--temperature', type=float, default=None)
    ap.add_argument('--max-tokens', type=int, default=6000); ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--agree', action='store_true'); ap.add_argument('--reasoning', choices=['low', 'medium', 'high'])
    ap.add_argument('--provider', nargs='*', help='OpenRouter provider order, e.g. Baidu'); ap.add_argument('--workers', type=int, default=1); ap.add_argument('--base')
    a = ap.parse_args()
    PROVIDER = a.provider
    agree(a) if a.agree else run(a)
