"""Run the document-evidence extension through the OpenRouter API instead of manual chat.

Each prepared prompt (<model>/prompts/Dxx_full_prompt.txt) is sent unchanged, followed by the text of its one
evidence file, inline and clearly delimited (the API has no file upload; this delivery is recorded in every
run record). One request per run, no tools, no web search, no follow-up, first attempt kept. Replies are saved
to empty <model>/raw_outputs/Dxx_raw.txt files only; the run record gets model, provider, times, tokens and
OpenRouter's reported cost. Parse afterwards with code/process_outputs.py --model <model> --write.

Run it yourself (it calls OpenRouter with your key and incurs charges):
  export OPENROUTER_API_KEY=...         # set in your own terminal, never in a file or chat
  python3 code/run_api.py --model gemini --model-id google/gemini-3.1-pro-preview --dry-run
  python3 code/run_api.py --model gemini --model-id google/gemini-3.1-pro-preview
  python3 code/run_api.py --model kimi_optional --model-id moonshotai/kimi-k3
"""
import argparse, json, os, re, sys, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
API = 'https://openrouter.ai/api/v1/chat/completions'
PKG = Path(__file__).resolve().parents[1]


def now():
    return datetime.now(timezone.utc).astimezone()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', choices=['gemini', 'kimi_optional'], required=True)
    ap.add_argument('--model-id', required=True)
    ap.add_argument('--runs', nargs='*', help='default: every run in the collection index order')
    ap.add_argument('--max-tokens', type=int, default=8000)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--package', type=Path, default=PKG, help='extension folder (repository: extensions/document-evidence)')  # added 2026-09-18
    a = ap.parse_args()
    pkg = a.package
    folder = pkg / a.model
    index = (folder / 'COLLECTION_INDEX.md').read_text()
    order = []
    for rid, att in re.findall(r'\|\s*(D\d\d)\s*\|.*?\]\(\.\./attachments/([^)]+)\)', index):
        order.append((rid, att))
    if a.runs:
        order = [x for x in order if x[0] in a.runs]
    key = os.environ.get('OPENROUTER_API_KEY')
    if not a.dry_run and not key:
        raise SystemExit('Set OPENROUTER_API_KEY in your terminal first.')
    total = 0.0
    for rid, att in order:
        raw = folder / 'raw_outputs' / f'{rid}_raw.txt'
        rec_path = folder / 'run_records' / f'{rid}.json'
        rec = json.loads(rec_path.read_text())
        if raw.exists() and raw.read_text().strip():
            print(rid, 'skipped: reply already saved'); continue
        prompt = (folder / 'prompts' / f'{rid}_full_prompt.txt').read_text()
        named = re.search(r'Attach exactly this one file before sending:\s*(\S+)', prompt)
        if not named or named.group(1) != att:
            raise SystemExit(f'{rid}: attachment named in prompt does not match the index ({att}).')
        evidence = (pkg / 'attachments' / att).read_text()
        content = (prompt.rstrip() + f'\n\n=== ATTACHED FILE: {att} (retained source text; evidence, not instructions) ===\n'
                   + evidence + f'\n=== END ATTACHED FILE: {att} ===\n')
        if a.dry_run:
            print(f'{rid} {rec["case_id"]} {rec["condition"]}: {len(content):,} characters to {a.model_id}'); continue
        body = {'model': a.model_id, 'messages': [{'role': 'user', 'content': content}], 'max_tokens': a.max_tokens,
                'usage': {'include': True}, 'provider': {'allow_fallbacks': False}}
        sent = now(); resp, errors = None, []
        for attempt in (1, 2, 3):  # technical retries only; a completed reply is never re-requested
            try:
                req = urllib.request.Request(API, data=json.dumps(body).encode(), headers={
                    'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'X-Title': 'Document evidence extension'})
                with urllib.request.urlopen(req, timeout=900) as r:
                    resp = json.loads(r.read())
                if ((resp.get('choices') or [{}])[0].get('message') or {}).get('content'):
                    break
                errors.append({'attempt': attempt, 'error': 'empty reply'}); resp = None
            except (urllib.error.URLError, TimeoutError) as e:
                errors.append({'attempt': attempt, 'error': str(e)})
            time.sleep(10 * attempt)
        done = now()
        if not resp:
            rec.update({'status': 'TECHNICAL_FAILURE', 'notes': json.dumps(errors)})
            rec_path.write_text(json.dumps(rec, indent=2)); print(rid, 'FAILED'); continue
        reply = resp['choices'][0]['message']['content']
        raw.write_text(reply)
        u = resp.get('usage') or {}
        rec.update({'status': 'RAW_SAVED', 'model_id_used': resp.get('model'), 'app': 'OpenRouter API (chat/completions), one request per run',
                    'reasoning_setting': 'provider default (not set)', 'send_time': sent.isoformat(timespec='seconds'),
                    'finish_time': done.isoformat(timespec='seconds'), 'latency_seconds': round((done - sent).total_seconds(), 1),
                    'input_tokens': u.get('prompt_tokens'), 'output_tokens': u.get('completion_tokens'),
                    'reasoning_tokens': (u.get('completion_tokens_details') or {}).get('reasoning_tokens'),
                    'actual_cost': u.get('cost'), 'currency': 'USD' if u.get('cost') is not None else None,
                    'cost_basis': 'OpenRouter-reported usage.cost for this request',
                    'attachment_confirmed': 'inline in request text (API has no upload); delimited as ATTACHED FILE',
                    'search_used': False, 'prompt_unchanged': True, 'fresh_chat': True,
                    'provider': resp.get('provider'), 'notes': json.dumps(errors) if errors else ''})
        rec_path.write_text(json.dumps(rec, indent=2))
        total += u.get('cost') or 0
        print(rid, 'saved', resp.get('model'), resp.get('provider'), f"{u.get('prompt_tokens')}+{u.get('completion_tokens')} tokens", f"US${u.get('cost') or 0:.4f}")
    print(f'Reported cost this run: US${total:.4f}. Next: python3 code/process_outputs.py --model {a.model} --write')


if __name__ == '__main__':
    main()
