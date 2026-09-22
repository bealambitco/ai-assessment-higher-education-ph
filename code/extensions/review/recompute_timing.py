"""Recompute the timing figures after the four flagged items were clarified (docs/timing-clarifications.md).

Run by the researcher, because the assignment file that maps a timed item to its configuration and pathway is
private. This script reads it, writes aggregates only, and never prints or stores an item-to-configuration
mapping.

  python3 -B code/extensions/review/recompute_timing.py \
      --session "<21_...>/timing/completion_2026-09-17/session_as_completed.json" \
      --assignment "<21_...>/private/timing_assignment.json" \
      --out "<extension package>/analysis/timing_recomputed.json"

Two figures are produced for every condition: the earlier one, which left out all four flagged items, and the
recomputed one, which includes the three the researcher has explained and still leaves out T24. No recorded
time is altered; only which items are counted changes.
"""
import argparse
import json
import statistics
from pathlib import Path

CLARIFIED_IN = {"T02": "away from the task during the unrecorded interval",
                "T16": "away from the task after deciding",
                "T04": "no prior exposure to the answer"}
STILL_OUT = {"T24": "interruption began about a minute before the pause was pressed; reported as a range"}
RANGE_ITEMS = {"T24": 60.0}  # seconds of interruption outside the recorded pause


def conditions(assignment):
    """item id -> condition label, from whatever shape the assignment file uses."""
    out = {}
    rows = assignment if isinstance(assignment, list) else assignment.get("items") or assignment.get("assignments") or []
    if isinstance(rows, dict):
        rows = [dict(v, timing_id=k) for k, v in rows.items()]
    for r in rows:
        tid = r.get("timing_id") or r.get("item") or r.get("id")
        model = r.get("model") or r.get("configuration")
        pathway = r.get("pathway") or r.get("route")
        if tid and model and pathway:
            out[tid] = f"{model}_{pathway}"
    if not out:
        raise SystemExit("Could not read item-to-condition rows from the assignment file; check its shape.")
    return out


def stats(values):
    if not values:
        return None
    return {"median": round(statistics.median(values), 1), "min": round(min(values), 1),
            "max": round(max(values), 1), "n": len(values)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True)
    ap.add_argument("--assignment", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    items = json.loads(Path(a.session).expanduser().read_text())["items"]
    cond = conditions(json.loads(Path(a.assignment).expanduser().read_text()))
    missing = [k for k in items if k not in cond]
    if missing:
        raise SystemExit(f"{len(missing)} timed item(s) have no condition in the assignment file.")

    per_condition = {}
    for tid, rec in items.items():
        c = cond[tid]
        row = per_condition.setdefault(c, {"earlier": [], "recomputed": [], "corrections_earlier": [],
                                           "corrections_recomputed": [], "clarified": [], "left_out": []})
        c1 = float(rec.get("clock1_seconds") or 0)
        c2 = float(rec.get("clock2_seconds") or 0)
        flagged = tid in CLARIFIED_IN or tid in STILL_OUT
        if not flagged:
            row["earlier"].append(c1)
            row["recomputed"].append(c1)
            if c2:
                row["corrections_earlier"].append(c2)
                row["corrections_recomputed"].append(c2)
        elif tid in CLARIFIED_IN:
            row["recomputed"].append(c1)
            if c2:
                row["corrections_recomputed"].append(c2)
            row["clarified"].append({"item": tid, "reason": CLARIFIED_IN[tid],
                                     "decision_seconds": round(c1, 1),
                                     "correction_seconds": round(c2, 1) if c2 else 0})
        else:
            row["left_out"].append({"item": tid, "reason": STILL_OUT[tid],
                                    "decision_seconds": round(c1, 1),
                                    "correction_seconds_range": [round(max(0.0, c2 - RANGE_ITEMS[tid]), 1), round(c2, 1)]})

    out = {"source": "docs/timing-clarifications.md, 21 September 2026",
           "note": ("Two figures per condition: the earlier one left out all four flagged items; the recomputed one "
                    "includes the three the researcher explained and still leaves out T24. No recorded time was "
                    "altered. Items that rejoin are flagged as explained after the fact."),
           "conditions": {}}
    for c, row in sorted(per_condition.items()):
        out["conditions"][c] = {
            "decision_seconds_earlier": stats(row["earlier"]),
            "decision_seconds_recomputed": stats(row["recomputed"]),
            "correction_seconds_earlier": stats(row["corrections_earlier"]),
            "correction_seconds_recomputed": stats(row["corrections_recomputed"]),
            "items_rejoining": row["clarified"], "items_still_out": row["left_out"]}

    Path(a.out).expanduser().parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).expanduser().write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {a.out}")
    for c, v in out["conditions"].items():
        e, r = v["decision_seconds_earlier"], v["decision_seconds_recomputed"]
        print(f"  {c:18s} decision median {e['median']:>6} s (n={e['n']})  ->  {r['median']:>6} s (n={r['n']})")
    print("Item-to-condition mapping is not written to the output.")


if __name__ == "__main__":
    main()
