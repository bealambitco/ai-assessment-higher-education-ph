"""Round-2 arm F: a second, outside timer handles ten already-collected answers.

Local only. No network access, no model calls, no paid calls, no student data. The tool serves an
interface on 127.0.0.1 that reproduces the round-1 timed-review conditions (two clocks, the same
decision set, explicit pauses, the withheld-answer rule) and adds the guards that round 1 needed
afterwards (see extensions/v2/second-timer/README.md).

Materials come from the public repository (benchmark/cases, benchmark/controls,
benchmark/protocol/primary_generation_order.csv) and from a local answers directory passed with
--answers. Nothing under any directory named private/ is read. The record file is written to a path
the researcher passes and may not be inside the repository.

Usage from the repository root:

  python3 -B code/extensions/round2/timing_round2.py --print-selection
  python3 -B code/extensions/round2/timing_round2.py --print-selection --show-model
  python3 -B code/extensions/round2/timing_round2.py --self-test
  python3 -B code/extensions/round2/timing_round2.py \
      --answers "<staging>/collection/primary" \
      --out "<staging>/30_ROUND2/timing_arm_f/second_timer_record.json"
"""
import argparse
import csv
import hashlib
import html
import json
import os
import re
import secrets
import sys
import tempfile
import urllib.parse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code/frozen_2026-09-15"))
import experiment as v1  # noqa: E402  (frozen round-1 code: safe_gate, active_seconds)

# ---------------------------------------------------------------- fixed parameters (see README)
SEED = "round2-armF-second-timer/2026-09-20"
N_ITEMS = 10
MODELS = ("astra", "luna")
PATHWAYS = ("direct", "controlled")
BANDS = ("W1", "W2", "W3")
# Five per configuration and five per pathway. The two cells that carry the extra item are fixed
# here, before selection, and are never chosen to suit a result.
CELL_QUOTA = {("astra", "direct"): 3, ("astra", "controlled"): 2,
              ("luna", "direct"): 2, ("luna", "controlled"): 3}
BAND_QUOTA = {"W1": 3, "W2": 3, "W3": 4}
REP_QUOTA = {1: 5, 2: 5}
DECISIONS = ["accept", "minor_edit", "major_edit", "reject", "escalate", "accept_gate"]
COMPLETION = ["usable_answer", "justified_disposition", "unresolved"]
WITHHELD = {"block", "route"}
GAP_LIMIT_SECONDS = 300
DRAFT_FIELDS = ["decision", "reason", "product", "completion_status", "pause_reason", "gap_reason"]


def now():
    return datetime.now(timezone.utc).isoformat()


def seconds_between(a, b):
    return (datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds()


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- deterministic ten-item selection
def frame(root=ROOT):
    """Every (run, pathway) row of the primary collection, from the public generation order."""
    rows = []
    with (root / "benchmark/protocol/primary_generation_order.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            if r["model"] not in MODELS:
                continue
            for pathway in PATHWAYS:
                rows.append({"run_id": r["run_id"], "case_id": r["case_id"], "model": r["model"],
                             "repetition": int(r["repetition"]), "pathway": pathway})
    return rows


def _key(row, purpose):
    return sha256_text(f"{SEED}|{purpose}|{row['run_id']}|{row['pathway']}")


def select(rows=None, n=N_ITEMS, cell_quota=None, band_quota=None, rep_quota=None):
    """Deterministic, data-independent selection.

    Rows are ordered by SHA-256 of a fixed seed and the row identity, then the first ordering that
    satisfies every quota is taken by depth-first search: one item per case, CELL_QUOTA per
    (configuration, pathway) cell, BAND_QUOTA per case band and REP_QUOTA per repetition. The
    search is exhaustive, so the result depends only on the seed and the quotas, never on any
    answer, score or check outcome.
    """
    rows = frame() if rows is None else rows
    cell_quota = dict(CELL_QUOTA if cell_quota is None else cell_quota)
    band_quota = dict(BAND_QUOTA if band_quota is None else band_quota)
    rep_quota = dict(REP_QUOTA if rep_quota is None else rep_quota)
    ordered = sorted(rows, key=lambda r: _key(r, "select"))
    cells, bands, reps, cases, chosen = {}, {}, {}, set(), []

    def search(i):
        if len(chosen) == n:
            return True
        if i >= len(ordered):
            return False
        r = ordered[i]
        cell, band = (r["model"], r["pathway"]), r["case_id"].split("-")[0]
        rep = r["repetition"]
        if (r["case_id"] not in cases
                and cells.get(cell, 0) < cell_quota.get(cell, 0)
                and bands.get(band, 0) < band_quota.get(band, 0)
                and reps.get(rep, 0) < rep_quota.get(rep, 0)):
            cases.add(r["case_id"]); cells[cell] = cells.get(cell, 0) + 1
            bands[band] = bands.get(band, 0) + 1; reps[rep] = reps.get(rep, 0) + 1
            chosen.append(r)
            if search(i + 1):
                return True
            chosen.pop(); reps[rep] -= 1; bands[band] -= 1; cells[cell] -= 1
            cases.discard(r["case_id"])
        return search(i + 1)

    if not search(0):
        raise ValueError("no selection satisfies the fixed quotas")
    # Presentation order is a second, independent hash, so the timer does not meet the cells in
    # blocks. Configuration and pathway are never shown.
    order = sorted(chosen, key=lambda r: _key(r, "order"))
    return [dict(r, timing_id=f"R2-{i:02d}") for i, r in enumerate(order, 1)]


def selection_digest(selection):
    return sha256_text(json.dumps(
        [{k: s[k] for k in ("timing_id", "run_id", "case_id", "model", "repetition", "pathway")}
         for s in selection], sort_keys=True))


def balance(selection):
    out = {"by_model": {}, "by_pathway": {}, "by_cell": {}, "by_band": {},
           "distinct_cases": len({s["case_id"] for s in selection}), "n": len(selection)}
    for s in selection:
        out["by_model"][s["model"]] = out["by_model"].get(s["model"], 0) + 1
        out["by_pathway"][s["pathway"]] = out["by_pathway"].get(s["pathway"], 0) + 1
        cell = f"{s['model']}/{s['pathway']}"
        out["by_cell"][cell] = out["by_cell"].get(cell, 0) + 1
        band = s["case_id"].split("-")[0]
        out["by_band"][band] = out["by_band"].get(band, 0) + 1
        out.setdefault("by_repetition", {})
        out["by_repetition"][s["repetition"]] = out["by_repetition"].get(s["repetition"], 0) + 1
    return out


def check_balance(selection):
    b = balance(selection)
    problems = []
    if b["n"] != N_ITEMS:
        problems.append(f"expected {N_ITEMS} items, got {b['n']}")
    if b["distinct_cases"] != b["n"]:
        problems.append("a case appears more than once")
    for m in MODELS:
        if b["by_model"].get(m) != N_ITEMS // 2:
            problems.append(f"configuration {m}: {b['by_model'].get(m)} items, expected {N_ITEMS // 2}")
    for p in PATHWAYS:
        if b["by_pathway"].get(p) != N_ITEMS // 2:
            problems.append(f"pathway {p}: {b['by_pathway'].get(p)} items, expected {N_ITEMS // 2}")
    for (m, p), q in CELL_QUOTA.items():
        if b["by_cell"].get(f"{m}/{p}", 0) != q:
            problems.append(f"cell {m}/{p}: {b['by_cell'].get(f'{m}/{p}', 0)} items, expected {q}")
    for band, q in BAND_QUOTA.items():
        if b["by_band"].get(band, 0) != q:
            problems.append(f"band {band}: {b['by_band'].get(band, 0)} items, expected {q}")
    for rep, q in REP_QUOTA.items():
        if b.get("by_repetition", {}).get(rep, 0) != q:
            problems.append(f"repetition {rep}: {b.get('by_repetition', {}).get(rep, 0)} items, "
                            f"expected {q}")
    return problems


# ---------------------------------------------------------------- materials
class Materials:
    """Case text, answer text and the round-1 control decision. Reads no private/ directory."""

    def __init__(self, answers_dir, root=ROOT):
        self.root = Path(root)
        self.answers_dir = Path(answers_dir).expanduser().resolve()
        if "private" in self.answers_dir.parts:
            raise ValueError("--answers must not point inside a private/ directory")
        self.profiles = json.loads((self.root / "benchmark/controls/control_profiles.json").read_text())

    def case(self, case_id):
        return json.loads((self.root / f"benchmark/cases/{case_id}.json").read_text())

    def _response_file(self, item):
        return (self.answers_dir / item["model"] / f"rep_{item['repetition']}"
                / f"{item['case_id']}_response.json")

    def answer(self, item):
        f = self._response_file(item)
        if not f.exists():
            return None, "No response available."
        rec = json.loads(f.read_text())
        obj = rec.get("response")
        if rec.get("record_status") != "RECEIVED" or rec.get("quarantine") or not isinstance(obj, dict):
            return None, "No response available."
        return obj, json.dumps(obj, ensure_ascii=False, indent=2)

    def control(self, item):
        """Round-1 checks, recomputed from public materials with the frozen round-1 gate."""
        obj, _ = self.answer(item)
        if obj is None:
            return {"decision": "unavailable", "checks": []}
        return v1.safe_gate(obj, self.case(item["case_id"]), self.profiles[item["case_id"]])


class SyntheticMaterials:
    """Fixtures for --self-test and the unit tests. Touches no collected answer."""

    def __init__(self, decisions=None):
        self.decisions = decisions or {}

    def case(self, case_id):
        return {"case_id": case_id, "institution": "Example State University",
                "scenario": ["Synthetic scenario line one.", "Synthetic scenario line two."],
                "requested_task": "Synthetic task for the self-test.",
                "source_locators": [f"{case_id} Handbook, Section 1"],
                "source_excerpt": "Synthetic rule text. No real policy is quoted here."}

    def answer(self, item):
        obj = {"case_id": item["case_id"], "answer": f"Synthetic answer for {item['case_id']}.",
               "proposed_action": "explain", "citations": [], "numeric_results": []}
        return obj, json.dumps(obj, ensure_ascii=False, indent=2)

    def control(self, item):
        decision = self.decisions.get(item["timing_id"], "release")
        return {"decision": decision, "checks": [{"check": "synthetic", "status": "PASS"}]}


# ---------------------------------------------------------------- clock arithmetic and validators
def recompute(item):
    """Recompute both clocks from the stored timestamps and list the flags that bar a clean record.

    Never subtracts or adds estimated time: an untimed gap is flagged, not removed.
    """
    pauses = item.get("pauses", [])
    spans = lambda phase: [(p["start"], p["finish"]) for p in pauses if p["phase"] == phase]
    c1 = v1.active_seconds(item["clock1_start"], item["clock1_finish"], spans("decision"))
    if item.get("no_further_work_explicit"):
        c2 = 0.0
    else:
        c2 = v1.active_seconds(item["clock2_start"], item["clock2_finish"], spans("finalization"))
    flags = []
    for g in item.get("gaps", []):
        flags.append("LONG_GAP_AFTER_DECISION" if g["phase"] == "between_clocks" else "LONG_GAP_IN_PHASE")
    if item.get("prior_exposure") != "NO":
        flags.append("PRIOR_EXPOSURE_NOT_NO")
    if item.get("restart_interruption"):
        flags.append("RESTART_INTERRUPTION")
    if any(p.get("onset_uncertain") for p in pauses):
        flags.append("PAUSE_ONSET_UNCERTAIN")
    close = lambda a, b: abs(a - b) < 1e-6
    return {"clock1_seconds": c1, "clock2_seconds": c2,
            "total_active_seconds": c1 + c2,
            "paused_seconds": sum(seconds_between(p["start"], p["finish"]) for p in pauses),
            "untimed_gap_seconds": sum(g["seconds"] for g in item.get("gaps", [])),
            "flags": sorted(set(flags)), "clean_record": not flags,
            "matches_recorded": (close(c1, item.get("clock1_seconds", c1))
                                 and close(c2, item.get("clock2_seconds", c2)))}


def validate_record(state, expect_balance=True):
    """Structural validation of a finished or partial record file.

    expect_balance is False only for the synthetic fixtures, which are deliberately smaller than
    the ten real items.
    """
    problems = []
    if expect_balance:
        problems += [f"selection: {p}" for p in check_balance(state["selection"])]
    if state.get("selection_sha256") != selection_digest(state["selection"]):
        problems.append("selection digest does not match the stored selection")
    ids = {s["timing_id"] for s in state["selection"]}
    for tid, item in state["items"].items():
        if tid not in ids:
            problems.append(f"{tid}: not in the selection")
        if item["phase"] != "complete":
            continue
        if item.get("prior_exposure") not in ("YES", "NO"):
            problems.append(f"{tid}: prior exposure not recorded as YES or NO")
        if item.get("decision") not in DECISIONS:
            problems.append(f"{tid}: decision missing or not in the round-1 set")
        if not (item.get("decision_reason") or "").strip():
            problems.append(f"{tid}: decision recorded without a reason")
        if not (item.get("final_product") or "").strip():
            problems.append(f"{tid}: no final product or justified disposition")
        if item.get("completion_status") not in COMPLETION:
            problems.append(f"{tid}: completion status missing")
        for g in item.get("gaps", []):
            if not (g.get("reason") or "").strip():
                problems.append(f"{tid}: untimed gap without a reason")
        for p in item.get("pauses", []):
            if not (p.get("reason") or "").strip():
                problems.append(f"{tid}: pause without a reason")
        if item.get("pause_start"):
            problems.append(f"{tid}: completed while still paused")
        if not recompute(item)["matches_recorded"]:
            problems.append(f"{tid}: recorded clock values disagree with the timestamps")
    return problems


def assert_out_of_repo(path):
    p = Path(path).expanduser().resolve()
    if p == ROOT or ROOT in p.parents:
        raise ValueError("the record file must not be written inside the repository: " + str(p))
    return p


# ---------------------------------------------------------------- session
class Session:
    def __init__(self, record_path, materials, selection=None, session_label="", allow_in_repo=False):
        self.file = Path(record_path).expanduser().resolve() if allow_in_repo else assert_out_of_repo(record_path)
        self.materials = materials
        sel = selection if selection is not None else select()
        if self.file.exists():
            self.state = json.loads(self.file.read_text())
            if self.state.get("selection_sha256") != selection_digest(sel):
                raise ValueError("this record file was written for a different selection; "
                                 "do not mix sessions, start a new file")
            self.state["resumed_at"] = self.state.get("resumed_at", []) + [now()]
        else:
            self.state = {"tool": "timing_round2.py", "arm": "F", "round": 2, "seed": SEED,
                          "session_label": session_label, "created_at": now(), "resumed_at": [],
                          "selection_sha256": selection_digest(sel), "selection": sel,
                          "items": {}, "events": []}
        self.selection = {s["timing_id"]: s for s in self.state["selection"]}
        # An item left mid-clock by a crash or a closed laptop is never presented as uninterrupted.
        for tid, r in self.state["items"].items():
            if r.get("phase") in ("decision", "finalization"):
                r["restart_interruption"] = True
                if not r.get("pause_start"):
                    r["pause_start"] = now()
                    r["pause_reason"] = ("Interface restarted during this item; the length of the "
                                         "interruption was not recorded.")
                    self.state["events"].append({"timing_id": tid, "action": "restart_pause",
                                                 "at": r["pause_start"]})
        self.save()

    # ---- storage
    def save(self):
        self.file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.file.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        os.replace(tmp, self.file)

    # ---- progress
    def current(self):
        for s in self.state["selection"]:
            if self.state["items"].get(s["timing_id"], {}).get("phase") != "complete":
                return s
        return None

    def item_state(self, tid):
        return self.state["items"].setdefault(tid, {
            "phase": "not_started", "inspect_override": False, "pauses": [], "gaps": [],
            "prior_exposure": None})

    def withheld(self, item):
        return (item["pathway"] == "controlled"
                and self.materials.control(item)["decision"] in WITHHELD)

    def gap_seconds(self, tid, r, t):
        """Seconds since the last recorded action for this item, or 0 before it is started."""
        if r["phase"] == "not_started" or not r.get("last_action_at"):
            return 0.0
        return seconds_between(r["last_action_at"], t)

    # ---- the one place state changes
    def event(self, action, form):
        item = self.current()
        if item is None:
            raise ValueError("All ten timed items are recorded. Nothing further to do.")
        tid = item["timing_id"]
        r = self.item_state(tid)
        if action != "draft" and (form.get("timing_id") != tid or form.get("phase") != r["phase"]):
            raise ValueError("This page is out of date. Refresh to load the saved current item.")
        t = now()

        if action == "draft":
            r.setdefault("draft", {}).update({k: form[k] for k in DRAFT_FIELDS if k in form})
            r["draft_saved_at"] = t
            self.save()
            return
        r.setdefault("draft", {}).update({k: form[k] for k in DRAFT_FIELDS if k in form})

        # Guard for the round-1 untimed gaps: nothing is recorded until the gap has a reason.
        gap = self.gap_seconds(tid, r, t)
        if gap > GAP_LIMIT_SECONDS and action not in ("resume",):
            reason = (form.get("gap_reason") or "").strip()
            if not reason:
                raise ValueError(
                    f"More than {GAP_LIMIT_SECONDS // 60} minutes passed with nothing recorded "
                    f"({gap / 60:.1f} minutes). Say what happened in the interruption box before "
                    "continuing. Your typing has been saved. No time is added or removed.")
            r["gaps"].append({"phase": r["phase"], "start": r["last_action_at"], "finish": t,
                              "seconds": gap, "reason": reason, "before_action": action})

        if action == "start":
            if r["phase"] != "not_started":
                raise ValueError("This item has already been started.")
            exposure = form.get("exposure")
            if exposure not in ("YES", "NO"):
                raise ValueError("Answer the prior-exposure question with Yes or No before the "
                                 "answer is shown. There is no unknown option in round 2.")
            r.update(phase="decision", clock1_start=t, prior_exposure=exposure,
                     prior_exposure_asked_before_answer=True)
        elif action == "inspect":
            if r["phase"] != "decision" or r.get("pause_start"):
                raise ValueError("The answer can only be inspected while Clock 1 is running.")
            if not self.withheld(item):
                raise ValueError("This answer is not withheld.")
            r["inspect_override"] = True
            r["inspect_at"] = t
        elif action == "pause":
            if r["phase"] not in ("decision", "finalization") or r.get("pause_start"):
                raise ValueError("There is no running clock to pause.")
            if not (form.get("pause_reason") or "").strip():
                raise ValueError("A pause needs a reason. Your typing has been saved.")
            r["pause_start"] = t
            r["pause_reason"] = form["pause_reason"]
        elif action == "resume":
            if not r.get("pause_start"):
                raise ValueError("This item is not paused.")
            onset = form.get("onset_uncertain")
            if onset not in ("YES", "NO"):
                raise ValueError("Before resuming, say whether the interruption began before you "
                                 "pressed Pause.")
            r["pauses"].append({"phase": r["phase"], "start": r.pop("pause_start"),
                                "finish": t, "reason": r.pop("pause_reason"),
                                "onset_uncertain": onset == "YES"})
        elif action == "decide":
            if r["phase"] != "decision" or r.get("pause_start"):
                raise ValueError("Clock 1 must be running to record a decision.")
            if form.get("decision") not in DECISIONS:
                raise ValueError("Choose one of the listed decisions.")
            if not (form.get("reason") or "").strip():
                raise ValueError("A decision needs a short reason. Nothing has been recorded yet; "
                                 "your typing has been saved.")
            r.update(phase="between_clocks", clock1_finish=t, decision=form["decision"],
                     decision_reason=form["reason"])
        elif action == "finalize_start":
            if r["phase"] != "between_clocks":
                raise ValueError("Record the decision first.")
            r.update(phase="finalization", clock2_start=t)
        elif action in ("finish", "no_work"):
            if action == "finish" and (r["phase"] != "finalization" or r.get("pause_start")):
                raise ValueError("Clock 2 must be running to save the final answer.")
            if action == "no_work" and r["phase"] != "between_clocks":
                raise ValueError("Record the decision first.")
            if not (form.get("product") or "").strip():
                raise ValueError("Write the final answer, or one line saying the original is used "
                                 "unchanged. Your typing has been saved.")
            if form.get("completion_status") not in COMPLETION:
                raise ValueError("Choose how this item finished.")
            r["final_product"] = form["product"]
            r["completion_status"] = form["completion_status"]
            if action == "no_work":
                r["clock2_seconds"] = 0.0
                r["no_further_work_explicit"] = True
            else:
                r["clock2_finish"] = t
                r["clock2_seconds"] = v1.active_seconds(
                    r["clock2_start"], t,
                    [(p["start"], p["finish"]) for p in r["pauses"] if p["phase"] == "finalization"])
            r["clock1_seconds"] = v1.active_seconds(
                r["clock1_start"], r["clock1_finish"],
                [(p["start"], p["finish"]) for p in r["pauses"] if p["phase"] == "decision"])
            r["phase"] = "complete"
            r["completed_at"] = t
            r["clean_time"] = recompute(r)
            r.pop("draft", None)
        else:
            raise ValueError("Unknown action.")

        r["last_action_at"] = t
        self.state["events"].append({"timing_id": tid, "action": action, "at": t,
                                     "seconds_since_last_action": gap})
        self.save()

    # ---- presentation (configuration and pathway are never named)
    def materials_html(self, item, r):
        inp = self.materials.case(item["case_id"])
        parts = ["<h2>Scenario</h2>"]
        parts += ["<p>" + esc(s).replace("\n", "<br>") + "</p>" for s in inp["scenario"]]
        parts += ["<h2>Task</h2><p>" + esc(inp["requested_task"]) + "</p>",
                  "<h2>Policy evidence</h2><pre>"
                  + esc("\n".join(inp["source_locators"]) + "\n" + inp["source_excerpt"]) + "</pre>"]
        control = self.materials.control(item)
        if item["pathway"] == "controlled":
            parts += ["<h2>Automatic check result</h2><p>" + esc(control["decision"]) + "</p><pre>"
                      + esc(json.dumps(control.get("checks", []), ensure_ascii=False, indent=2)) + "</pre>"]
        if self.withheld(item) and not r.get("inspect_override"):
            parts += ["<h2>Answer</h2><p>The answer was withheld by the automatic check and is "
                      "hidden. You may open it, and opening it is recorded.</p>"]
        else:
            _, text = self.materials.answer(item)
            parts += ["<h2>Answer</h2><pre>" + esc(text) + "</pre>"]
        return "".join(parts)

    def page(self, token):
        item = self.current()
        done = sum(1 for s in self.state["selection"]
                   if self.state["items"].get(s["timing_id"], {}).get("phase") == "complete")
        if item is None:
            return ("<h1>All ten items are recorded</h1><p>Thank you. Tell the researcher you have "
                    "finished. You do not need to do anything else.</p>")
        tid = item["timing_id"]
        r = self.item_state(tid)
        head = (f"<h1>Item {tid} &mdash; {done} of {len(self.state['selection'])} finished</h1>"
                "<p>Times are recorded automatically. Refreshing the page does not restart a clock. "
                "Use Pause if anything interrupts you.</p>")
        if r.get("restart_interruption"):
            head += ("<p><strong>This item was interrupted by a restart.</strong> That is recorded. "
                     "Its time will not be reported as uninterrupted.</p>")
        gap = self.gap_seconds(tid, r, now())
        gapbox = ""
        if gap > GAP_LIMIT_SECONDS:
            head += (f"<p><strong>Nothing has been recorded for {gap / 60:.0f} minutes.</strong> "
                     "Please say what happened before you continue.</p>")
            gapbox = ("<p>What happened in that time?</p>"
                      "<textarea name=\"gap_reason\" rows=\"2\"></textarea>")
        form = ('<form method="post"><input type="hidden" name="token" value="' + token + '">'
                '<input type="hidden" name="timing_id" value="' + tid + '">'
                '<input type="hidden" name="phase" value="' + r["phase"] + '">' + gapbox)

        def button(action, label):
            return f'<button name="action" value="{esc(action)}">{esc(label)}</button>'

        if r["phase"] == "not_started":
            return (head + form
                    + "<p>Before the answer is shown: have you read this answer, or worked on this "
                      "scenario, at any time before today?</p>"
                      '<select name="exposure"><option value="">Choose</option>'
                      '<option value="NO">No</option><option value="YES">Yes</option></select>'
                    + button("start", "Show the materials and start Clock 1") + "</form>")
        if r.get("pause_start"):
            return (head + form + "<p>Paused. The materials are hidden while you are paused.</p>"
                    + "<p>Did the interruption begin before you pressed Pause?</p>"
                      '<select name="onset_uncertain"><option value="">Choose</option>'
                      '<option value="NO">No, I pressed Pause straight away</option>'
                      '<option value="YES">Yes, it began earlier</option></select>'
                    + button("resume", "Resume") + "</form>")

        body = self.materials_html(item, r)
        if r["phase"] == "decision":
            if self.withheld(item) and not r.get("inspect_override"):
                form += button("inspect", "Open the withheld answer (this is recorded)")
            form += ("<p>Your decision</p><select name=\"decision\"><option value=\"\">Choose</option>"
                     + "".join(f"<option>{d}</option>" for d in DECISIONS)
                     + "</select><p>Why? One or two sentences. This is required.</p>"
                       "<textarea name=\"reason\" rows=\"3\"></textarea>"
                       "<p>Reason for pausing, if you are pausing</p>"
                       "<textarea name=\"pause_reason\" rows=\"2\"></textarea>"
                     + button("decide", "Record the decision and stop Clock 1")
                     + button("pause", "Pause Clock 1"))
        elif r["phase"] == "between_clocks":
            form += ("<p>Clock 1 has stopped. If the answer needs any change, start Clock 2 before "
                     "you edit anything.</p>" + button("finalize_start", "Start Clock 2")
                     + "<p>If no change at all is needed, write one line here confirming that you "
                       "would use the answer as it stands, then press the second button.</p>"
                       "<textarea name=\"product\" rows=\"3\"></textarea>"
                       '<select name="completion_status">'
                     + "".join(f"<option>{c}</option>" for c in COMPLETION) + "</select>"
                     + button("no_work", "No change needed; record Clock 2 as zero"))
        else:
            form += ("<p>The answer you would actually use, or what you would do instead</p>"
                     "<textarea name=\"product\" rows=\"12\"></textarea>"
                     '<select name="completion_status">'
                     + "".join(f"<option>{c}</option>" for c in COMPLETION) + "</select>"
                     + "<p>Reason for pausing, if you are pausing</p>"
                       "<textarea name=\"pause_reason\" rows=\"2\"></textarea>"
                     + button("finish", "Save and stop Clock 2") + button("pause", "Pause Clock 2"))
        form += "</form>"
        for key, value in (r.get("draft") or {}).items():
            form = restore_draft(form, key, value)
        return (head + body
                + '<p id="save-status" role="status">Your typing is saved on this computer.</p>'
                + form + AUTOSAVE)


def esc(x):
    return html.escape(str(x))


def restore_draft(form, key, value):
    form = re.sub(r'(<textarea name="' + key + r'"[^>]*>).*?(</textarea>)',
                  lambda m: m[1] + esc(value) + m[2], form, flags=re.S)

    def fill(m):
        return re.sub(
            r'<option(?: value="([^"]*)")?>(.*?)</option>',
            lambda o: ("<option" + (' value="' + o[1] + '"' if o[1] is not None else "")
                       + (" selected" if (o[1] if o[1] is not None else html.unescape(o[2])) == value else "")
                       + ">" + o[2] + "</option>"), m[0])

    return re.sub(r'<select name="' + key + r'">.*?</select>', fill, form, flags=re.S)


AUTOSAVE = r"""<script>
(()=>{const f=document.querySelector('form'),s=document.getElementById('save-status');if(!f||!s)return;
const fields=['decision','reason','product','completion_status','pause_reason','gap_reason'];
let timer,chain=Promise.resolve(),busy=false;
function body(action){const p=new URLSearchParams(new FormData(f));p.set('action',action);return p;}
function save(){chain=chain.then(async()=>{try{const r=await fetch('/',{method:'POST',body:body('draft')});
 if(!r.ok)throw Error('save failed');s.textContent='Saved at '+new Date().toLocaleTimeString();}
 catch(e){s.textContent='Could not save. Keep this tab open and tell the researcher.';}});return chain;}
f.addEventListener('input',()=>{if(busy)return;clearTimeout(timer);timer=setTimeout(save,600);});
f.addEventListener('submit',async e=>{e.preventDefault();if(busy)return;const a=e.submitter&&e.submitter.value;if(!a)return;
 busy=true;clearTimeout(timer);await chain;
 try{const r=await fetch('/',{method:'POST',body:body(a)});
  if(!r.ok){let m='Error '+r.status;try{m=(await r.json()).error||m;}catch(x){}throw Error(m);}
  location.reload();}
 catch(err){busy=false;s.textContent=err.message+' Nothing was recorded; your typing is kept.';}});
window.addEventListener('pagehide',()=>{navigator.sendBeacon('/',body('draft'));});
for(const k of fields){if(f.elements[k])f.elements[k].addEventListener('change',()=>{clearTimeout(timer);save();});}
})();
</script>"""

STYLE = ("<!doctype html><meta charset=\"utf-8\"><title>Timed review</title><style>"
         "body{max-width:880px;margin:35px auto;font:17px/1.5 Arial;color:#18262e;padding:20px}"
         "pre{white-space:pre-wrap;overflow-wrap:anywhere;font:15px/1.5 Arial;background:#f4f6f7;padding:12px}"
         "textarea{display:block;width:100%;background:#fff8d8}"
         "button,select{font:16px Arial;padding:12px;margin:8px}h2{margin-top:28px}</style>")


def serve(session, port=8766):
    token = secrets.token_urlsafe(24)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            if self.path != "/":
                self.send_error(404)
                return
            b = (STYLE + session.page(token)).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(b)

        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            if length > 400000:
                self.send_error(413)
                return
            raw = self.rfile.read(length).decode()
            form = {k: v[-1] for k, v in urllib.parse.parse_qs(raw, keep_blank_values=True).items()}
            if form.get("token") != token:
                self.send_error(403)
                return
            try:
                session.event(form.get("action"), form)
            except ValueError as e:
                b = json.dumps({"error": str(e)}).encode()
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')

    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"Open http://127.0.0.1:{port} in a browser on this computer.")
    print(f"Record file: {session.file}")
    print("No network calls are made. Ctrl-C stops the server.")
    server.serve_forever()


# ---------------------------------------------------------------- self-test
def self_test():
    """Drive the whole flow on synthetic items. Touches no collected answer."""
    checks = []

    def ok(label, condition):
        checks.append((label, bool(condition)))
        print(("PASS  " if condition else "FAIL  ") + label)

    def raises(label, fn, fragment=""):
        try:
            fn()
            ok(label, False)
        except ValueError as e:
            ok(label + f"  [{str(e)[:48]}...]", fragment.lower() in str(e).lower())

    sel = select()
    ok("selection is ten items, balanced, one per case", not check_balance(sel))
    ok("selection is deterministic across calls", selection_digest(select()) == selection_digest(sel))

    # Synthetic three-item session, one withheld, with its own quotas.
    rows = [{"run_id": "S-1", "case_id": "S1-01", "model": "astra", "repetition": 1,
             "pathway": "direct"},
            {"run_id": "S-2", "case_id": "S2-01", "model": "luna", "repetition": 1,
             "pathway": "controlled"},
            {"run_id": "S-3", "case_id": "S3-01", "model": "astra", "repetition": 2,
             "pathway": "controlled"}]
    syn = [dict(r, timing_id=f"R2-{i:02d}") for i, r in enumerate(rows, 1)]
    mats = SyntheticMaterials({"R2-02": "block"})

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "self_test_record.json"
        raises("record file inside the repository is refused",
               lambda: Session(ROOT / "extensions/v2/second-timer/x.json", mats, syn), "inside the repo")

        s = Session(path, mats, syn, session_label="self-test")
        f = lambda **kw: dict({"timing_id": s.current()["timing_id"],
                               "phase": s.item_state(s.current()["timing_id"])["phase"]}, **kw)

        # Item 1: exposure must be explicit; pause; decide needs a reason; no_work path.
        raises("start without an exposure answer is refused",
               lambda: s.event("start", f(exposure="")), "Yes or No")
        raises("start with UNKNOWN exposure is refused",
               lambda: s.event("start", f(exposure="UNKNOWN")), "Yes or No")
        s.event("start", f(exposure="NO"))
        ok("exposure is asked before the answer is shown",
           s.state["items"]["R2-01"]["prior_exposure_asked_before_answer"])
        raises("pause without a reason is refused",
               lambda: s.event("pause", f(pause_reason="  ")), "needs a reason")
        s.event("pause", f(pause_reason="Someone came to the door."))
        ok("materials are hidden while paused", "Scenario" not in s.page("t"))
        raises("resume without answering the onset question is refused",
               lambda: s.event("resume", f()), "before you pressed Pause")
        s.event("resume", f(onset_uncertain="NO"))
        raises("a decision without a reason is refused",
               lambda: s.event("decide", f(decision="accept", reason="")), "short reason")
        raises("a decision outside the round-1 set is refused",
               lambda: s.event("decide", f(decision="looks_fine", reason="x")), "listed decisions")
        s.event("decide", f(decision="accept", reason="Matches the quoted rule."))
        raises("no_work without a product is refused",
               lambda: s.event("no_work", f(product=" ", completion_status="usable_answer")), "final answer")
        s.event("no_work", f(product="Use the answer as it stands.",
                             completion_status="justified_disposition"))
        one = s.state["items"]["R2-01"]
        ok("item 1 complete with Clock 2 zero", one["phase"] == "complete" and one["clock2_seconds"] == 0.0)
        ok("item 1 pause excluded from Clock 1",
           one["clock1_seconds"] < seconds_between(one["clock1_start"], one["clock1_finish"]))
        ok("item 1 recomputes clean", one["clean_time"]["clean_record"]
           and one["clean_time"]["matches_recorded"])

        # Item 2: withheld answer, Inspect, full Clock 2.
        s.event("start", f(exposure="NO"))
        page = s.page("t")
        ok("withheld answer is hidden before Inspect",
           "withheld by the automatic check" in page and "Synthetic answer for S2-01" not in page)
        s.event("inspect", f())
        ok("withheld answer is shown after Inspect and the press is logged",
           "Synthetic answer for S2-01" in s.page("t")
           and any(e["action"] == "inspect" for e in s.state["events"]))
        s.event("decide", f(decision="minor_edit", reason="Needs the locator spelled out."))
        s.event("finalize_start", f())
        s.event("finish", f(product="Edited answer.", completion_status="usable_answer"))
        two = s.state["items"]["R2-02"]
        ok("item 2 logs the Inspect override", two["inspect_override"] and "inspect_at" in two)

        # Item 3: forced reason for a long untimed gap, then resume from a reopened file.
        s.event("start", f(exposure="YES"))
        s.event("decide", f(decision="reject", reason="Contradicts the quoted section."))
        item3 = s.state["items"]["R2-03"]
        item3["last_action_at"] = shift(item3["last_action_at"], -1800)
        s.save()
        raises("a gap over five minutes forces a reason",
               lambda: s.event("finalize_start", f()), "minutes passed")
        s.event("finalize_start", f(gap_reason="Stepped out for a call."))
        ok("the untimed gap is recorded, not subtracted",
           len(item3["gaps"]) == 1 and item3["gaps"][0]["phase"] == "between_clocks"
           and item3["gaps"][0]["seconds"] > GAP_LIMIT_SECONDS)

        s2 = Session(path, mats, syn)
        ok("reopening resumes at the unfinished item", s2.current()["timing_id"] == "R2-03")
        ok("reopening mid-clock records an interruption and pauses",
           s2.state["items"]["R2-03"].get("restart_interruption")
           and s2.state["items"]["R2-03"].get("pause_start"))
        g = lambda **kw: dict({"timing_id": "R2-03",
                               "phase": s2.item_state("R2-03")["phase"]}, **kw)
        s2.event("resume", g(onset_uncertain="YES"))
        s2.event("finish", g(product="Referred to the registrar.", completion_status="unresolved"))
        three = s2.state["items"]["R2-03"]
        ok("flagged item is not a clean record", not three["clean_time"]["clean_record"])
        ok("flags name the gap, the exposure, the restart and the uncertain pause",
           set(three["clean_time"]["flags"]) == {"LONG_GAP_AFTER_DECISION", "PRIOR_EXPOSURE_NOT_NO",
                                                 "RESTART_INTERRUPTION", "PAUSE_ONSET_UNCERTAIN"})
        ok("all three synthetic items are complete", s2.current() is None)
        ok("record validates", validate_record(s2.state, expect_balance=False) == [])

        raises("a record file from another selection is refused",
               lambda: Session(path, mats, [dict(syn[0], run_id="OTHER")] + syn[1:]), "different selection")

    failed = [c for c, good in checks if not good]
    print(f"\n{len(checks) - len(failed)}/{len(checks)} self-test checks passed")
    return 0 if not failed else 1


def shift(stamp, seconds):
    from datetime import timedelta
    return (datetime.fromisoformat(stamp) + timedelta(seconds=seconds)).isoformat()


# ---------------------------------------------------------------- command line
def print_selection(selection, show_model):
    b = balance(selection)
    width = 78
    print("Round-2 arm F, second timer: the ten items")
    print(f"seed {SEED}")
    print(f"selection sha256 {selection_digest(selection)}")
    print("-" * width)
    header = f"{'item':6} {'case':7} {'pathway':11}"
    print(header + (f" {'configuration':13} {'rep':3}" if show_model else ""))
    for s in selection:
        line = f"{s['timing_id']:6} {s['case_id']:7} {s['pathway']:11}"
        if show_model:
            line += f" {s['model']:13} {s['repetition']:<3}"
        print(line)
    print("-" * width)
    print("by configuration: " + ", ".join(f"{k} {v}" for k, v in sorted(b["by_model"].items())))
    print("by pathway:       " + ", ".join(f"{k} {v}" for k, v in sorted(b["by_pathway"].items())))
    print("by cell:          " + ", ".join(f"{k} {v}" for k, v in sorted(b["by_cell"].items())))
    print("by case band:     " + ", ".join(f"{k} {v}" for k, v in sorted(b["by_band"].items())))
    print("by repetition:    " + ", ".join(f"{k} {v}" for k, v in sorted(b.get("by_repetition", {}).items())))
    print(f"distinct cases:   {b['distinct_cases']} of {b['n']}")
    problems = check_balance(selection)
    print("balance check:    " + ("OK" if not problems else "; ".join(problems)))
    return 0 if not problems else 1


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--answers", help="directory holding <model>/rep_<n>/<case>_response.json")
    p.add_argument("--out", help="record file to write; must be outside the repository")
    p.add_argument("--port", type=int, default=8766)
    p.add_argument("--session-label", default="")
    p.add_argument("--print-selection", action="store_true")
    p.add_argument("--show-model", action="store_true",
                   help="with --print-selection, also print the configuration of each item")
    p.add_argument("--validate", help="validate an existing record file and exit")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args(argv)

    if a.self_test:
        return self_test()
    if a.print_selection:
        return print_selection(select(), a.show_model)
    if a.validate:
        state = json.loads(Path(a.validate).expanduser().read_text())
        problems = validate_record(state)
        print("\n".join(problems) if problems else "record validates: no problems found")
        return 1 if problems else 0
    if not a.answers or not a.out:
        p.error("--answers and --out are both required to run a session")
    session = Session(a.out, Materials(a.answers), session_label=a.session_label)
    serve(session, a.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
