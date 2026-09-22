"""Scoring results for the answers read in the extension, joined to the release decisions.

The extension read the answers the frozen checks had withheld and never scored, plus the answers
needed to complete their cases. This script overlays those judgments on the locked join of release
decisions and recomputes every condition-level figure with the same definitions, denominators and
bootstrap seed as `code/supplement/analyze_supplement.py`, so the numbers stay comparable.

Nothing is recomputed from the frozen records themselves: the join is read as written, and only
`acceptable`, `severity` and `criterion_correct_fraction` are added for answers that had none.
Answers still unread keep their unscored status and stay in every denominator.

  python3 -B code/extensions/review/analyze_scoring.py \
      --join "<21_...>/analysis/locked_score_gate_join.json" \
      --scores "<extension package>/scores/extension_scores.json" \
      --checks "<extension package>/analysis/checks_v2_per_answer.csv" \
      --timing "<21_...>/analysis/supplement/supplement_results.json" \
      --out-private "<extension package>/analysis" \
      --out-public  "<repo>/extensions/answer-scoring"

Private output carries the masked identifiers; public output never does.
"""
import argparse
import csv
import json
import statistics
import sys
from collections import OrderedDict
from pathlib import Path

sys.dont_write_bytecode = True

MODELS = ["astra", "luna"]
PATHWAYS = ["direct", "controlled"]
RELEASED = ("release", "release_with_warning")
SERIOUS = ("Major", "Critical")
WORKFLOWS = ["W1", "W2", "W3"]

# The four flagged timing items and the condition each belongs to, as already published per condition
# in analysis/supplement/supplement_results.json (S8_timing.excluded_items). Three were explained by the
# researcher on 21 September 2026 and rejoin the figures; T24 stays out and is reported as a range.
TIMING_REJOIN = {"astra_direct": "T02", "astra_controlled": "T04", "luna_direct": "T16"}
TIMING_STILL_OUT = {"luna_controlled": "T24"}


def load_supplement_module(repo):
    sys.path.insert(0, str(Path(repo) / "code/supplement"))
    import analyze_supplement  # noqa: E402  (same definitions, same seed)
    return analyze_supplement


def extension_outcomes(scores_path):
    """run_id -> the judgment the extension recorded, from the live scoring file."""
    data = json.loads(Path(scores_path).expanduser().read_text())
    out = {}
    for r in data["records"]:
        if r["status"] != "SCORED":
            continue
        crit = r.get("criteria") or []
        judged = [c.get("judgment") for c in crit]
        correct = sum(j == "Correct" for j in judged)
        out[r["run_id"]] = {
            "scoring_id": r["scoring_id"], "part": r["part"], "case_id": r["case_id"],
            "configuration": r["configuration"], "repetition": r["repetition"],
            "round1_check_decision": r["round1_check_decision"],
            "acceptable": bool(r["acceptable"]), "severity": r["severity"],
            "criteria": len(crit), "criteria_correct": correct,
            "criterion_correct_fraction": (correct / len(crit)) if crit else 0.0,
            "failure_classes": sorted({f for c in crit for f in (c.get("failure_classes") or [])}
                                      | set(r.get("failure_classes") or [])),
            "seconds": (r.get("clock") or {}).get("seconds_clean"),
            "edits": len(r.get("edits") or []),
            "revisions": len(r.get("supersedes") or []),
            "comment": (r.get("researcher_comments") or "").strip(),
            "reference_challenge": (r.get("reference_challenge") or "").strip(),
        }
    return out, data


def overlay(join, ext):
    """Add the extension judgments to the join. An answer scored in the study is never overwritten."""
    rows, added, conflicts = [], [], []
    for r in join:
        r = dict(r)
        e = ext.get(r["run_id"])
        if e and r["acceptable"] is None:
            r["acceptable"] = e["acceptable"]
            r["severity"] = e["severity"]
            r["criterion_correct_fraction"] = e["criterion_correct_fraction"]
            r["score_source"] = "extension"
            if r["pathway"] == "direct":
                added.append(r["run_id"])
        elif e:
            r["score_source"] = "study"
            conflicts.append(r["run_id"])
        elif r["acceptable"] is not None:
            r["score_source"] = "study"
        else:
            r["score_source"] = "unscored"
        rows.append(r)
    return rows, sorted(set(added)), sorted(set(conflicts))


def coverage(rows, ext):
    answers = {r["run_id"]: r for r in rows if r["pathway"] == "direct"}
    by_source = OrderedDict((k, sum(a["score_source"] == k for a in answers.values()))
                            for k in ("study", "extension", "unscored"))
    cases = sorted({a["case_id"] for a in answers.values()})
    complete = [c for c in cases
                if all(a["score_source"] != "unscored" for a in answers.values() if a["case_id"] == c)]
    parts = OrderedDict()
    for e in ext.values():
        parts[e["part"]] = parts.get(e["part"], 0) + 1
    return {"answers": len(answers), "by_source": by_source, "scored": len(answers) - by_source["unscored"],
            "cases_total": len(cases), "cases_complete": len(complete), "cases_complete_list": complete,
            "extension_answers_by_part": parts,
            "note": "An answer counts as scored once any criterion-level judgment exists for it; "
                    "unscored answers stay in every denominator."}


def withheld_audit(rows, ext, checks_by_run):
    """Every answer the frozen checks withheld, with what reading it later showed."""
    out = []
    for r in rows:
        if r["pathway"] != "controlled" or r["decision"] in RELEASED:
            continue
        e = ext.get(r["run_id"])
        chk = checks_by_run.get(r["run_id"], {})
        fired = sorted({c["check"] for c in r.get("trace", []) if c.get("status") in ("FAIL", "TRIGGERED", "ERROR")})
        out.append({
            "run_id": r["run_id"], "case_id": r["case_id"], "model": r["model"],
            "repetition": r["repetition"], "decision": r["decision"],
            "checks_that_fired": fired,
            "outcome": ("acceptable" if r["acceptable"] is True
                        else "serious" if r["severity"] in SERIOUS
                        else "other unacceptable" if r["acceptable"] is False else "still unread"),
            "severity": r["severity"],
            "read_in": "extension" if e else ("study" if r["acceptable"] is not None else "not read"),
            "revised_checks_decision": chk.get("decision_v2"),
            "revised_checks_release": chk.get("withheld_v2") == "False",
        })
    return sorted(out, key=lambda x: (x["model"], x["case_id"], x["repetition"]))


def condition_tables(A, rows):
    return {f"{m}_{p}": A.condition_block([r for r in rows if r["model"] == m and r["pathway"] == p])
            for m in MODELS for p in PATHWAYS}


def workflow_tables(A, rows):
    return {w: {f"{m}_{p}": A.condition_block([r for r in rows if r["case_id"].startswith(w)
                                               and r["model"] == m and r["pathway"] == p])
                for m in MODELS for p in PATHWAYS} for w in WORKFLOWS}


def criterion_correctness(rows):
    out = {}
    for m in MODELS:
        answers = [r for r in rows if r["model"] == m and r["pathway"] == "direct"]
        cases = sorted({a["case_id"] for a in answers})
        per_case_sched, per_case_scored = [], []
        for c in cases:
            xs = [a for a in answers if a["case_id"] == c]
            per_case_sched.append(statistics.mean([a["criterion_correct_fraction"] if a["score_source"] != "unscored" else 0.0 for a in xs]))
            read = [a["criterion_correct_fraction"] for a in xs if a["score_source"] != "unscored"]
            if read:
                per_case_scored.append(statistics.mean(read))
        out[m] = {"scheduled_case_mean": round(statistics.mean(per_case_sched), 4),
                  "scored_case_mean": round(statistics.mean(per_case_scored), 4),
                  "cases_with_any_scored_answer": len(per_case_scored)}
    return out


def repetition_consistency(rows):
    out = {}
    for m in MODELS:
        pairs = []
        for c in sorted({r["case_id"] for r in rows}):
            a = {r["repetition"]: r["acceptable"] for r in rows
                 if r["model"] == m and r["case_id"] == c and r["pathway"] == "direct"}
            if a.get(1) is not None and a.get(2) is not None:
                pairs.append((a[1], a[2]))
        out[m] = {"cases_with_both": len(pairs), "same_label": sum(x == y for x, y in pairs),
                  "acceptable_both": sum(x and y for x, y in pairs),
                  "acceptable_neither": sum((not x) and (not y) for x, y in pairs)}
    return out


def baselines(rows):
    """The three comparison policies, on the same answers and the same denominators."""
    judgment_cases = sorted({r["case_id"] for r in rows if r["case_id"].startswith(("W1", "W2"))})
    out = {}
    for m in MODELS:
        answers = [r for r in rows if r["model"] == m and r["pathway"] == "direct"]
        ok = lambda a: a["acceptable"] is True
        ser = lambda a: a["severity"] in SERIOUS
        withhold_all = {"useful": 0, "serious_released": 0}
        format_only = {"useful": sum(ok(a) for a in answers), "serious_released": sum(ser(a) for a in answers)}
        route_judgment = {"useful": sum(ok(a) for a in answers if a["case_id"] not in judgment_cases),
                          "serious_released": sum(ser(a) for a in answers if a["case_id"] not in judgment_cases)}
        out[m] = {"withhold_everything": withhold_all, "block_format_failures_only": format_only,
                  "route_all_judgment_cases": route_judgment, "answers": len(answers)}
    out["note"] = ("No answer failed the format check, so blocking format failures only is identical to direct "
                   "release. Judgment cases are the W1 and W2 groups.")
    return out


def effort(ext):
    xs = [e["seconds"] for e in ext.values() if e["seconds"]]
    return {"answers_read": len(ext), "seconds_median": round(statistics.median(xs), 1) if xs else None,
            "seconds_min": round(min(xs), 1) if xs else None, "seconds_max": round(max(xs), 1) if xs else None,
            "seconds_total": round(sum(xs), 1) if xs else None,
            "answers_revised_after_first_entry": sum(1 for e in ext.values() if e["revisions"]),
            "note": "Reading time per answer, clock running only while the answer was open, pauses excluded. "
                    "It measures scoring against a written key, not the checking a user would do."}


def timing_recomputed(supp):
    """The timing figures once the three explained items rejoin; T24 stays out (docs/timing-clarifications.md)."""
    by = supp["S8_timing"]["by_condition"]
    out = {}
    for cond, v in by.items():
        rejoin = TIMING_REJOIN.get(cond)
        if rejoin:
            out[cond] = {"decision_seconds": v["clock1"], "items_with_correction": f"{v['items_with_clock2_work']}/{v['clock1']['n']}",
                         "correction_seconds_among_corrected": v["clock2_among_worked_items"],
                         "item_rejoining": rejoin, "item_still_out": None}
        else:
            out[cond] = {"decision_seconds": v["primary_clock1"],
                         "items_with_correction": v["primary_items_with_correction"],
                         "correction_seconds_among_corrected": v["primary_clock2_among_corrected"],
                         "item_rejoining": None, "item_still_out": TIMING_STILL_OUT.get(cond)}
        out[cond]["as_published_excluding_all_four"] = v["primary_clock1"]
    n_items = sum(o["decision_seconds"]["n"] for o in out.values())
    corrected = sum(int(o["items_with_correction"].split("/")[0]) for o in out.values())
    out["totals"] = {"timed_items_counted": n_items, "items_needing_correction": corrected}
    out["note"] = ("Each flagged item's condition is already published per condition in the study's "
                   "supplementary results; no private assignment file was opened. Three items rejoin because "
                   "the researcher stated on the record what the unrecorded intervals were, four days after "
                   "the event; each is flagged as explained after the fact. T24 stays out.")
    return out


def public_rows(rows, ext):
    """One row per answer, no masked identifier."""
    out = []
    for r in rows:
        if r["pathway"] != "direct":
            continue
        ctrl = next((x for x in rows if x["run_id"] == r["run_id"] and x["pathway"] == "controlled"), None)
        e = ext.get(r["run_id"])
        out.append({"run_id": r["run_id"], "case_id": r["case_id"], "configuration": r["model"],
                    "repetition": r["repetition"],
                    "check_decision": ctrl["decision"] if ctrl else "",
                    "withheld_by_checks": bool(ctrl and ctrl["decision"] not in RELEASED),
                    "read": r["score_source"] != "unscored", "read_in": r["score_source"],
                    "acceptable": "" if r["acceptable"] is None else r["acceptable"],
                    "severity": r["severity"] or "",
                    "criteria_correct_share": "" if r["score_source"] == "unscored" else round(r["criterion_correct_fraction"], 3),
                    "failure_classes": ";".join(e["failure_classes"]) if e else ""})
    return sorted(out, key=lambda x: (x["configuration"], x["case_id"], x["repetition"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--join", required=True)
    ap.add_argument("--scores", required=True)
    ap.add_argument("--checks", required=True)
    ap.add_argument("--timing", required=True)
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[3]))
    ap.add_argument("--out-private", required=True)
    ap.add_argument("--out-public", required=True)
    ap.add_argument("--compare", help="supplement results computed with the same overlay; the two must agree")
    a = ap.parse_args()

    A = load_supplement_module(a.repo)
    join = json.loads(Path(a.join).expanduser().read_text())
    ext, score_file = extension_outcomes(a.scores)
    checks_by_run = {r["run_id"]: r for r in csv.DictReader(Path(a.checks).expanduser().open())}
    supp = json.loads(Path(a.timing).expanduser().read_text())

    rows, added, conflicts = overlay(join, ext)
    if conflicts:
        raise SystemExit(f"{len(conflicts)} answer(s) already scored in the study also appear in the extension "
                         f"score file: {conflicts[:5]}. Study scores are never revised; stopping.")
    unmatched = sorted(set(ext) - {r["run_id"] for r in join})
    if unmatched:
        raise SystemExit(f"extension scores with no matching answer: {unmatched}")

    conds = condition_tables(A, rows)
    res = {
        "label": "Answer scoring, extension round; definitions, denominators and bootstrap seed from the "
                 "study's supplementary analysis",
        "scoring_stopped_at": score_file.get("locked_at") or "not locked",
        "answers_read_in_extension": len(ext),
        "coverage": coverage(rows, ext),
        "conditions": conds,
        "conditions_text": {k: {"useful_release": v["useful_release"]["text"],
                                "useful_release_ci": A.fmt_ci(v["useful_release_ci"]),
                                "serious_released": v["serious_released"]["text"],
                                "acceptable": v["acceptable"]["text"],
                                "unscored": v["unscored"]["text"],
                                "acceptable_withheld": v["unnecessary_withholding"]["text"],
                                "routed": v["withheld_acceptable_routed"],
                                "blocked": v["withheld_acceptable_blocked"]} for k, v in conds.items()},
        "withheld_audit": withheld_audit(rows, ext, checks_by_run),
        "by_workflow": workflow_tables(A, rows),
        "criterion_correctness": criterion_correctness(rows),
        "repetition_consistency": repetition_consistency(rows),
        "checks_by_outcome": A.checks_table(rows),
        "baselines": baselines(rows),
        "reading_effort": effort(ext),
        "timing_recomputed": timing_recomputed(supp),
        "failure_classes_used": sorted({f for e in ext.values() for f in e["failure_classes"]}),
        "reference_challenges": [e["scoring_id"] for e in ext.values() if e["reference_challenge"]],
    }
    wa = res["withheld_audit"]
    res["headline"] = {
        "answers_withheld_by_the_checks": len(wa),
        "now_read": sum(w["read_in"] != "not read" for w in wa),
        "acceptable": sum(w["outcome"] == "acceptable" for w in wa),
        "serious": sum(w["outcome"] == "serious" for w in wa),
        "still_unread": sum(w["outcome"] == "still unread" for w in wa),
        "released_by_the_revised_checks": sum(bool(w["revised_checks_release"]) for w in wa),
    }

    if a.compare:
        # Two routes to the same table: this script overlays the judgments on the published join, and the
        # supplement overlays them on its own join of the locked files. They must agree.
        other = json.loads(Path(a.compare).expanduser().read_text())["S2_conditions"]
        for k, v in conds.items():
            for field in ("useful_release", "serious_released", "acceptable", "unscored", "unnecessary_withholding"):
                if v[field]["text"] != other[k][field]["text"]:
                    raise SystemExit(f"{k} {field}: {v[field]['text']} here, {other[k][field]['text']} in the "
                                     f"supplement. The two routes disagree; stopping.")
        res["agrees_with_supplement"] = Path(a.compare).name

    priv = Path(a.out_private).expanduser(); priv.mkdir(parents=True, exist_ok=True)
    pub = Path(a.out_public).expanduser(); pub.mkdir(parents=True, exist_ok=True)
    (priv / "scoring_results.json").write_text(json.dumps(res, indent=2) + "\n")
    rowsp = public_rows(rows, ext)
    for target in (priv / "scoring_per_answer.csv", pub / "answers_scored.csv"):
        with target.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rowsp[0]))
            w.writeheader(); w.writerows(rowsp)
    public = {k: v for k, v in res.items() if k != "withheld_audit"}
    public["withheld_audit"] = [{k: v for k, v in w.items()} for w in wa]
    (pub / "scoring_results.json").write_text(json.dumps(public, indent=2) + "\n")

    h = res["headline"]
    print(f"read in the extension: {len(ext)}; scored overall: {res['coverage']['scored']} of {res['coverage']['answers']}"
          f" ({res['coverage']['cases_complete']} complete cases)")
    print(f"withheld by the checks: {h['answers_withheld_by_the_checks']}; read {h['now_read']}; "
          f"acceptable {h['acceptable']}; serious {h['serious']}; still unread {h['still_unread']}")
    for k, v in res["conditions_text"].items():
        print(f"  {k:18s} useful {v['useful_release']:>6}  acceptable withheld {v['acceptable_withheld']:>6} "
              f"(routed {v['routed']}, blocked {v['blocked']})")


if __name__ == "__main__":
    main()
