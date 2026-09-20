"""Send prepared extension prompts to OpenRouter. THE RESEARCHER RUNS THIS; it costs money.

The key is read from the environment and is never written to a file, a record or the screen.

  export OPENROUTER_API_KEY=...            # in your own terminal, never in a file or in chat
  python3 -B code/extensions/collection/run_openrouter.py --work ~/extension-work --arm access \
      --model-id openai/gpt-oss-20b --dry-run
  python3 -B code/extensions/collection/run_openrouter.py --work ~/extension-work --arm access \
      --model-id openai/gpt-oss-20b --label gptoss20b

One request per run, no tools, no web search, no follow-up, first reply kept. A run whose reply is already
saved is skipped, so the command can be repeated safely. Technical failures (network error, 5xx, empty
reply) are retried up to three times within 900 seconds, as in the primary study; a reply that arrives is never
retried, whatever it contains. Every run record holds the model, provider, timings, token counts and the
cost OpenRouter reports, so costs come from the provider rather than an estimate.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://openrouter.ai/api/v1/chat/completions"
MAX_ATTEMPTS = 3
RETRY_WINDOW_S = 900


def now():
    return datetime.now(timezone.utc).astimezone()


def post(payload, key, timeout):
    req = urllib.request.Request(
        API, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://github.com/bealambitco/ai-assessment-higher-education-ph",
                 "X-Title": "ai-assessment-higher-education-ph extension"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def usable(raw_path, record_path):
    """A saved reply we can still use: not truncated at the cap and parseable as one JSON object."""
    import json as _json
    try:
        record = _json.loads(record_path.read_text())
    except Exception:
        record = {}
    if record.get("finish_reason") == "length" or record.get("native_finish_reason") == "MAX_TOKENS":
        return False
    text = raw_path.read_text().strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        _json.loads(text)
        return True
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, help="working directory used by prepare_prompts.py")
    ap.add_argument("--arm", required=True, choices=["documents", "discovery", "access"])
    ap.add_argument("--model-id", required=True, help="OpenRouter model id, e.g. openai/gpt-oss-20b")
    ap.add_argument("--label", help="short folder name for this configuration (default: model id, slashes out)")
    ap.add_argument("--runs", nargs="*", help="run ids; default every run in the manifest")
    ap.add_argument("--max-tokens", type=int, default=4000)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--sleep", type=float, default=2.0, help="pause between runs, seconds")
    ap.add_argument("--limit", type=int, help="stop after this many runs (a safety valve for a first try)")
    ap.add_argument("--dry-run", action="store_true", help="print what would be sent; no request, no cost")
    ap.add_argument("--redo-unusable", action="store_true",
                    help="re-send only runs whose saved reply is missing, empty, truncated at the token cap, "
                         "or unparseable; the superseded reply is kept beside the new one")
    a = ap.parse_args()

    work = Path(a.work).expanduser() / a.arm
    manifest = json.loads((work / "MANIFEST.json").read_text())
    label = a.label or a.model_id.replace("/", "_").replace(":", "_")
    out = work / "by_model" / label
    for sub in ("raw_outputs", "run_records"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    runs = [r for r in manifest["runs"] if not a.runs or r["run_id"] in a.runs]
    if a.limit:
        runs = runs[:a.limit]
    key = os.environ.get("OPENROUTER_API_KEY")
    if not a.dry_run and not key:
        raise SystemExit("Set OPENROUTER_API_KEY in your terminal first. Never put it in a file.")

    total_cost, sent, skipped, failed = 0.0, 0, 0, []
    for r in runs:
        rid = r["run_id"]
        raw = out / "raw_outputs" / f"{rid}_raw.txt"
        if raw.exists() and raw.read_text().strip():
            if not a.redo_unusable or usable(raw, out / "run_records" / f"{rid}.json"):
                skipped += 1
                continue
            keep = raw.with_name(f"{rid}_raw_superseded_{int(time.time())}.txt")
            raw.replace(keep)
            print(f"{rid}: previous reply kept as {keep.name}")
        prompt = (work / "prompts" / f"{rid}_full_prompt.txt").read_text()
        if a.dry_run:
            print(f"{rid}: would send {len(prompt):,} chars (~{len(prompt)//4:,} tokens) to {a.model_id}")
            continue
        payload = {"model": a.model_id, "temperature": a.temperature, "max_tokens": a.max_tokens,
                   "messages": [{"role": "user", "content": prompt}]}
        started, attempt, reply, error = now(), 0, None, None
        deadline = time.monotonic() + RETRY_WINDOW_S
        while attempt < MAX_ATTEMPTS and reply is None and time.monotonic() < deadline:
            attempt += 1
            try:
                body = post(payload, key, a.timeout)
                text = (body.get("choices") or [{}])[0].get("message", {}).get("content")
                if text and text.strip():
                    reply = (text, body)
                else:
                    error = "empty reply"
            except urllib.error.HTTPError as e:
                detail = e.read().decode(errors="replace")[:300]
                error = f"HTTP {e.code}: {detail}"
                if 400 <= e.code < 500 and e.code not in (408, 429):
                    break  # a request the provider refuses is not a technical retry
            except Exception as e:  # network, timeout, malformed body
                error = f"{type(e).__name__}: {e}"
            if reply is None and attempt < MAX_ATTEMPTS:
                time.sleep(min(30, 5 * attempt))
        finished = now()
        record = {"run_id": rid, "case_id": r["case_id"], "arm": a.arm, "model_id": a.model_id, "label": label,
                  "started_at": started.isoformat(), "finished_at": finished.isoformat(),
                  "seconds": round((finished - started).total_seconds(), 3), "attempts": attempt,
                  "temperature": a.temperature, "max_tokens": a.max_tokens,
                  "prompt_sha256": r["prompt_sha256"], "prompt_chars": r["prompt_chars"],
                  "evidence_delivery": manifest["evidence_delivery"], "error": None if reply else error}
        if reply:
            text, body = reply
            raw.write_text(text)
            usage = body.get("usage") or {}
            record.update({"provider": body.get("provider"), "generation_id": body.get("id"),
                           "native_finish_reason": (body.get("choices") or [{}])[0].get("native_finish_reason"),
                           "finish_reason": (body.get("choices") or [{}])[0].get("finish_reason"),
                           "usage": usage, "cost_usd_reported": usage.get("cost"),
                           "reply_chars": len(text)})
            total_cost += float(usage.get("cost") or 0)
            sent += 1
            print(f"{rid}: {len(text):,} chars, {record['seconds']}s, cost {usage.get('cost')}")
        else:
            failed.append((rid, error))
            print(f"{rid}: FAILED after {attempt} attempt(s): {error}", file=sys.stderr)
        (out / "run_records" / f"{rid}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        time.sleep(a.sleep)

    print(f"\n{label}: sent {sent}, skipped {skipped}, failed {len(failed)}; "
          f"cost reported by OpenRouter {total_cost:.4f} USD")
    if failed:
        print("failed runs:", ", ".join(rid for rid, _ in failed))
        print("re-run the same command to retry only those runs.")


if __name__ == "__main__":
    main()
