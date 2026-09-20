"""Tests for the round-2 arm F timing tool. Run from the repository root:

  python3 -B -m unittest discover -s code/tests -p 'test_timing_round2.py' -v

No collected answer, no network and no private/ directory is touched: every test uses the synthetic
materials built into the tool.
"""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code/extensions/round2"))
import timing_round2 as tr  # noqa: E402

T0 = datetime(2026, 10, 1, 9, 0, 0, tzinfo=timezone.utc)


def at(seconds):
    return (T0 + timedelta(seconds=seconds)).isoformat()


SYNTHETIC = [
    {"run_id": "S-1", "case_id": "S1-01", "model": "astra", "repetition": 1, "pathway": "direct",
     "timing_id": "R2-01"},
    {"run_id": "S-2", "case_id": "S2-01", "model": "luna", "repetition": 1, "pathway": "controlled",
     "timing_id": "R2-02"},
    {"run_id": "S-3", "case_id": "S3-01", "model": "astra", "repetition": 2, "pathway": "controlled",
     "timing_id": "R2-03"},
]


def item(**kw):
    """A completed item with both clocks and no flags, overridable field by field."""
    base = {"phase": "complete", "prior_exposure": "NO", "pauses": [], "gaps": [],
            "inspect_override": False,
            "clock1_start": at(0), "clock1_finish": at(120), "clock1_seconds": 120.0,
            "clock2_start": at(130), "clock2_finish": at(430), "clock2_seconds": 300.0,
            "decision": "minor_edit", "decision_reason": "Needed the locator.",
            "final_product": "Edited answer.", "completion_status": "usable_answer"}
    base.update(kw)
    return base


def session(tmpdir, selection=None, decisions=None, label="test"):
    return tr.Session(Path(tmpdir) / "record.json",
                      tr.SyntheticMaterials(decisions or {}),
                      selection if selection is not None else SYNTHETIC,
                      session_label=label)


def form(s, **kw):
    tid = s.current()["timing_id"]
    return dict({"timing_id": tid, "phase": s.item_state(tid)["phase"]}, **kw)


def finish_item(s, exposure="NO", decision="accept", reason="Matches the quoted rule.",
                product="Use it as it stands."):
    s.event("start", form(s, exposure=exposure))
    s.event("decide", form(s, decision=decision, reason=reason))
    s.event("no_work", form(s, product=product, completion_status="justified_disposition"))


# ---------------------------------------------------------------- clock arithmetic
class TestClocks(unittest.TestCase):
    def test_plain_clocks(self):
        c = tr.recompute(item())
        self.assertEqual(c["clock1_seconds"], 120.0)
        self.assertEqual(c["clock2_seconds"], 300.0)
        self.assertEqual(c["total_active_seconds"], 420.0)
        self.assertTrue(c["matches_recorded"])
        self.assertTrue(c["clean_record"])

    def test_pause_is_subtracted_from_its_own_phase_only(self):
        r = item(pauses=[{"phase": "decision", "start": at(30), "finish": at(90),
                          "reason": "Phone call.", "onset_uncertain": False}],
                 clock1_seconds=60.0)
        c = tr.recompute(r)
        self.assertEqual(c["clock1_seconds"], 60.0)      # 120 wall minus a 60 second pause
        self.assertEqual(c["clock2_seconds"], 300.0)     # untouched
        self.assertEqual(c["paused_seconds"], 60.0)
        self.assertTrue(c["matches_recorded"])

    def test_two_pauses_in_both_phases(self):
        r = item(pauses=[{"phase": "decision", "start": at(20), "finish": at(50), "reason": "a"},
                         {"phase": "decision", "start": at(60), "finish": at(70), "reason": "b"},
                         {"phase": "finalization", "start": at(200), "finish": at(320),
                          "reason": "c"}],
                 clock1_seconds=80.0, clock2_seconds=180.0)
        c = tr.recompute(r)
        self.assertEqual(c["clock1_seconds"], 80.0)      # 120 - 30 - 10
        self.assertEqual(c["clock2_seconds"], 180.0)     # 300 - 120
        self.assertEqual(c["paused_seconds"], 160.0)
        self.assertTrue(c["matches_recorded"])

    def test_overlapping_pause_is_rejected(self):
        r = item(pauses=[{"phase": "decision", "start": at(20), "finish": at(60), "reason": "a"},
                         {"phase": "decision", "start": at(40), "finish": at(80), "reason": "b"}])
        with self.assertRaises(ValueError):
            tr.recompute(r)

    def test_pause_outside_the_clock_is_rejected(self):
        r = item(pauses=[{"phase": "decision", "start": at(100), "finish": at(200), "reason": "a"}])
        with self.assertRaises(ValueError):
            tr.recompute(r)

    def test_zero_clock2_when_no_work_was_needed(self):
        r = item(no_further_work_explicit=True, clock2_seconds=0.0)
        r.pop("clock2_start"); r.pop("clock2_finish")
        c = tr.recompute(r)
        self.assertEqual(c["clock2_seconds"], 0.0)
        self.assertTrue(c["matches_recorded"])

    def test_recomputation_catches_a_disagreeing_stored_value(self):
        self.assertFalse(tr.recompute(item(clock1_seconds=11.0))["matches_recorded"])

    def test_untimed_gap_is_reported_but_never_subtracted(self):
        r = item(gaps=[{"phase": "between_clocks", "start": at(120), "finish": at(3720),
                        "seconds": 3600.0, "reason": "Went to lunch.", "before_action": "finalize_start"}])
        c = tr.recompute(r)
        self.assertEqual(c["clock1_seconds"], 120.0)
        self.assertEqual(c["clock2_seconds"], 300.0)
        self.assertEqual(c["untimed_gap_seconds"], 3600.0)
        self.assertIn("LONG_GAP_AFTER_DECISION", c["flags"])
        self.assertFalse(c["clean_record"])

    def test_each_flag_blocks_a_clean_record(self):
        cases = {
            "LONG_GAP_IN_PHASE": item(gaps=[{"phase": "decision", "start": at(0), "finish": at(400),
                                             "seconds": 400.0, "reason": "r"}]),
            "PRIOR_EXPOSURE_NOT_NO": item(prior_exposure="YES"),
            "RESTART_INTERRUPTION": item(restart_interruption=True),
            "PAUSE_ONSET_UNCERTAIN": item(pauses=[{"phase": "decision", "start": at(30),
                                                   "finish": at(90), "reason": "r",
                                                   "onset_uncertain": True}], clock1_seconds=60.0),
        }
        for flag, r in cases.items():
            with self.subTest(flag=flag):
                c = tr.recompute(r)
                self.assertIn(flag, c["flags"])
                self.assertFalse(c["clean_record"])

    def test_live_session_clocks_match_the_recomputation(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            s.event("start", form(s, exposure="NO"))
            s.event("pause", form(s, pause_reason="Door."))
            s.event("resume", form(s, onset_uncertain="NO"))
            s.event("decide", form(s, decision="minor_edit", reason="Unclear locator."))
            s.event("finalize_start", form(s))
            s.event("finish", form(s, product="Edited.", completion_status="usable_answer"))
            r = s.state["items"]["R2-01"]
            self.assertTrue(r["clean_time"]["matches_recorded"])
            self.assertTrue(r["clean_time"]["clean_record"])
            wall = tr.seconds_between(r["clock1_start"], r["clock1_finish"])
            self.assertLess(r["clock1_seconds"], wall)  # the pause came out of Clock 1


# ---------------------------------------------------------------- the exposure question
class TestExposure(unittest.TestCase):
    def test_answer_is_not_shown_before_the_question_is_answered(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            page = s.page("tok")
            self.assertIn("at any time before today", page)
            self.assertNotIn("Synthetic answer for S1-01", page)
            self.assertNotIn("Synthetic scenario", page)

    def test_blank_and_unknown_are_both_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            for bad in ("", "UNKNOWN", "maybe", None):
                with self.subTest(value=bad):
                    kw = {} if bad is None else {"exposure": bad}
                    with self.assertRaises(ValueError):
                        s.event("start", form(s, **kw))
            self.assertEqual(s.item_state("R2-01")["phase"], "not_started")

    def test_yes_and_no_are_both_recorded_and_the_order_is_stored(self):
        for value in ("YES", "NO"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                s = session(tmp)
                s.event("start", form(s, exposure=value))
                r = s.state["items"]["R2-01"]
                self.assertEqual(r["prior_exposure"], value)
                self.assertTrue(r["prior_exposure_asked_before_answer"])
                self.assertIn("Synthetic answer for S1-01", s.page("tok"))

    def test_yes_marks_the_item_as_not_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            finish_item(s, exposure="YES")
            c = s.state["items"]["R2-01"]["clean_time"]
            self.assertIn("PRIOR_EXPOSURE_NOT_NO", c["flags"])
            self.assertFalse(c["clean_record"])


# ---------------------------------------------------------------- withheld answers and Inspect
class TestWithheld(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        # R2-02 is the controlled item; block it so its answer is withheld.
        self.s = session(self.tmp.name, decisions={"R2-02": "block"})
        finish_item(self.s)  # clear R2-01 so R2-02 is current

    def tearDown(self):
        self.tmp.cleanup()

    def test_withheld_answer_is_hidden_until_inspect(self):
        self.s.event("start", form(self.s, exposure="NO"))
        page = self.s.page("tok")
        self.assertIn("withheld by the automatic check", page)
        self.assertNotIn("Synthetic answer for S2-01", page)
        self.assertIn("Open the withheld answer", page)

    def test_inspect_reveals_the_answer_and_is_logged(self):
        self.s.event("start", form(self.s, exposure="NO"))
        self.s.event("inspect", form(self.s))
        r = self.s.state["items"]["R2-02"]
        self.assertTrue(r["inspect_override"])
        self.assertIn("inspect_at", r)
        self.assertTrue(any(e["timing_id"] == "R2-02" and e["action"] == "inspect"
                            for e in self.s.state["events"]))
        page = self.s.page("tok")
        self.assertIn("Synthetic answer for S2-01", page)
        self.assertNotIn("Open the withheld answer", page)

    def test_inspect_survives_reopening_the_record(self):
        self.s.event("start", form(self.s, exposure="NO"))
        self.s.event("inspect", form(self.s))
        reopened = session(self.tmp.name, decisions={"R2-02": "block"})
        self.assertTrue(reopened.state["items"]["R2-02"]["inspect_override"])

    def test_inspect_is_refused_when_the_answer_is_not_withheld(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)  # every check releases
            s.event("start", form(s, exposure="NO"))
            with self.assertRaises(ValueError):
                s.event("inspect", form(s))

    def test_inspect_is_refused_outside_the_decision_phase(self):
        self.s.event("start", form(self.s, exposure="NO"))
        self.s.event("decide", form(self.s, decision="escalate", reason="Withheld; refer it."))
        with self.assertRaises(ValueError):
            self.s.event("inspect", form(self.s))

    def test_inspect_is_refused_while_paused(self):
        self.s.event("start", form(self.s, exposure="NO"))
        self.s.event("pause", form(self.s, pause_reason="Interrupted."))
        with self.assertRaises(ValueError):
            self.s.event("inspect", form(self.s))

    def test_a_withheld_item_can_be_completed_without_inspecting(self):
        self.s.event("start", form(self.s, exposure="NO"))
        self.s.event("decide", form(self.s, decision="escalate", reason="Refer it unread."))
        self.s.event("no_work", form(self.s, product="Referred.",
                                     completion_status="justified_disposition"))
        r = self.s.state["items"]["R2-02"]
        self.assertEqual(r["phase"], "complete")
        self.assertFalse(r["inspect_override"])
        self.assertTrue(r["clean_time"]["clean_record"])


# ---------------------------------------------------------------- resuming
class TestResume(unittest.TestCase):
    def test_reopening_continues_at_the_first_unfinished_item(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            finish_item(s)
            self.assertEqual(s.current()["timing_id"], "R2-02")
            reopened = session(tmp)
            self.assertEqual(reopened.current()["timing_id"], "R2-02")
            self.assertEqual(reopened.state["items"]["R2-01"]["phase"], "complete")
            self.assertEqual(len(reopened.state["resumed_at"]), 1)

    def test_completed_work_is_not_rewritten_on_reopening(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            finish_item(s)
            before = json.dumps(s.state["items"]["R2-01"], sort_keys=True)
            reopened = session(tmp)
            self.assertEqual(json.dumps(reopened.state["items"]["R2-01"], sort_keys=True), before)

    def test_an_item_left_mid_clock_is_paused_and_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            s.event("start", form(s, exposure="NO"))
            reopened = session(tmp)
            r = reopened.state["items"]["R2-01"]
            self.assertTrue(r["restart_interruption"])
            self.assertTrue(r["pause_start"])
            self.assertIn("Paused", reopened.page("tok"))
            self.assertNotIn("Synthetic answer for S1-01", reopened.page("tok"))
            self.assertTrue(any(e["action"] == "restart_pause" for e in reopened.state["events"]))

    def test_the_restart_flag_survives_to_the_finished_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            s.event("start", form(s, exposure="NO"))
            r2 = session(tmp)
            r2.event("resume", form(r2, onset_uncertain="YES"))
            r2.event("decide", form(r2, decision="accept", reason="Fine as it stands."))
            r2.event("no_work", form(r2, product="Use it.", completion_status="usable_answer"))
            c = r2.state["items"]["R2-01"]["clean_time"]
            self.assertIn("RESTART_INTERRUPTION", c["flags"])
            self.assertIn("PAUSE_ONSET_UNCERTAIN", c["flags"])
            self.assertFalse(c["clean_record"])

    def test_a_record_file_from_a_different_selection_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            session(tmp)
            other = [dict(SYNTHETIC[0], run_id="OTHER")] + SYNTHETIC[1:]
            with self.assertRaises(ValueError):
                session(tmp, selection=other)

    def test_a_stale_page_cannot_replay_an_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            stale = form(s)                      # captured while phase is not_started
            s.event("start", form(s, exposure="NO"))
            with self.assertRaises(ValueError):
                s.event("decide", dict(stale, decision="accept", reason="x"))

    def test_drafts_are_kept_across_a_reopen_and_cleared_when_the_item_is_done(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            s.event("start", form(s, exposure="NO"))
            s.event("draft", {"timing_id": "R2-01", "phase": "decision",
                              "reason": "half written thought"})
            reopened = session(tmp)
            self.assertEqual(reopened.state["items"]["R2-01"]["draft"]["reason"],
                             "half written thought")
            reopened.event("resume", form(reopened, onset_uncertain="NO"))
            self.assertIn("half written thought", reopened.page("tok"))
            reopened.event("decide", form(reopened, decision="accept", reason="Fine."))
            reopened.event("no_work", form(reopened, product="Use it.",
                                           completion_status="usable_answer"))
            self.assertNotIn("draft", reopened.state["items"]["R2-01"])


# ---------------------------------------------------------------- validators and guards
class TestValidators(unittest.TestCase):
    def test_the_real_selection_is_deterministic(self):
        first = tr.select()
        self.assertEqual(tr.selection_digest(first), tr.selection_digest(tr.select()))
        shuffled = list(reversed(tr.frame()))
        self.assertEqual(tr.selection_digest(tr.select(shuffled)), tr.selection_digest(first))

    def test_the_real_selection_is_balanced(self):
        sel = tr.select()
        self.assertEqual(tr.check_balance(sel), [])
        b = tr.balance(sel)
        self.assertEqual(b["n"], tr.N_ITEMS)
        self.assertEqual(b["distinct_cases"], tr.N_ITEMS)
        self.assertEqual(b["by_model"], {"astra": 5, "luna": 5})
        self.assertEqual(b["by_pathway"], {"direct": 5, "controlled": 5})
        self.assertEqual(b["by_band"], dict(tr.BAND_QUOTA))
        self.assertEqual(b["by_repetition"], dict(tr.REP_QUOTA))

    def test_the_selection_does_not_depend_on_any_answer(self):
        """The selection is built from the public generation order only."""
        sel = tr.select()
        self.assertTrue(all(set(s) == {"run_id", "case_id", "model", "repetition", "pathway",
                                       "timing_id"} for s in sel))
        self.assertTrue(all(s["case_id"] in {c["case_id"] for c in tr.frame()} for s in sel))

    def test_check_balance_reports_an_unbalanced_selection(self):
        sel = tr.select()
        broken = [dict(s, model="astra") for s in sel]
        self.assertTrue(any("configuration" in p for p in tr.check_balance(broken)))

    def test_a_record_path_inside_the_repository_is_refused(self):
        with self.assertRaises(ValueError):
            tr.assert_out_of_repo(ROOT / "extensions/v2/second-timer/record.json")
        with self.assertRaises(ValueError):
            tr.assert_out_of_repo(ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(str(tr.assert_out_of_repo(Path(tmp) / "r.json")).endswith("r.json"))

    def test_an_answers_directory_inside_private_is_refused(self):
        with self.assertRaises(ValueError):
            tr.Materials("/tmp/some/private/collection")

    def test_a_decision_needs_a_reason_and_a_listed_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            s.event("start", form(s, exposure="NO"))
            for kw in ({"decision": "accept", "reason": "   "},
                       {"decision": "accept"},
                       {"decision": "", "reason": "ok"},
                       {"decision": "looks_fine", "reason": "ok"}):
                with self.subTest(**kw):
                    with self.assertRaises(ValueError):
                        s.event("decide", form(s, **kw))
            self.assertEqual(s.item_state("R2-01")["phase"], "decision")
            self.assertNotIn("decision", s.item_state("R2-01"))

    def test_a_pause_needs_a_reason_and_a_resume_needs_the_onset_answer(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            s.event("start", form(s, exposure="NO"))
            with self.assertRaises(ValueError):
                s.event("pause", form(s, pause_reason=" "))
            s.event("pause", form(s, pause_reason="Someone came in."))
            with self.assertRaises(ValueError):
                s.event("resume", form(s))
            with self.assertRaises(ValueError):
                s.event("resume", form(s, onset_uncertain="maybe"))
            s.event("resume", form(s, onset_uncertain="NO"))
            self.assertEqual(len(s.item_state("R2-01")["pauses"]), 1)

    def test_a_final_product_and_a_completion_status_are_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            s.event("start", form(s, exposure="NO"))
            s.event("decide", form(s, decision="accept", reason="Fine."))
            with self.assertRaises(ValueError):
                s.event("no_work", form(s, product="  ", completion_status="usable_answer"))
            with self.assertRaises(ValueError):
                s.event("no_work", form(s, product="Use it.", completion_status=""))
            s.event("no_work", form(s, product="Use it.", completion_status="usable_answer"))
            self.assertEqual(s.item_state("R2-01")["phase"], "complete")

    def test_a_long_gap_forces_a_reason_and_is_then_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            s.event("start", form(s, exposure="NO"))
            s.event("decide", form(s, decision="reject", reason="Contradicts the rule."))
            r = s.item_state("R2-01")
            r["last_action_at"] = tr.shift(r["last_action_at"], -(tr.GAP_LIMIT_SECONDS + 600))
            s.save()
            with self.assertRaises(ValueError) as caught:
                s.event("finalize_start", form(s))
            self.assertIn("minutes passed", str(caught.exception))
            self.assertEqual(r["phase"], "between_clocks")
            s.event("finalize_start", form(s, gap_reason="Took a call."))
            self.assertEqual(len(r["gaps"]), 1)
            self.assertEqual(r["gaps"][0]["phase"], "between_clocks")
            self.assertEqual(r["gaps"][0]["reason"], "Took a call.")
            self.assertGreater(r["gaps"][0]["seconds"], tr.GAP_LIMIT_SECONDS)

    def test_a_short_gap_needs_no_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            s.event("start", form(s, exposure="NO"))
            r = s.item_state("R2-01")
            r["last_action_at"] = tr.shift(r["last_action_at"], -(tr.GAP_LIMIT_SECONDS - 60))
            s.save()
            s.event("decide", form(s, decision="accept", reason="Fine."))
            self.assertEqual(r["gaps"], [])

    def test_validate_record_accepts_a_complete_synthetic_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            for _ in range(3):
                finish_item(s)
            self.assertIsNone(s.current())
            self.assertEqual(tr.validate_record(s.state, expect_balance=False), [])

    def test_validate_record_names_every_kind_of_damage(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            for _ in range(3):
                finish_item(s)
            state = json.loads(json.dumps(s.state))
            state["items"]["R2-01"]["decision_reason"] = "  "
            state["items"]["R2-01"]["prior_exposure"] = "UNKNOWN"
            state["items"]["R2-02"]["decision"] = "looks_fine"
            state["items"]["R2-02"]["final_product"] = ""
            state["items"]["R2-03"]["clock1_seconds"] = 3.0
            state["items"]["R2-03"]["completion_status"] = "maybe"
            state["items"]["R2-03"]["gaps"] = [{"phase": "decision", "start": at(0),
                                                "finish": at(400), "seconds": 400.0, "reason": ""}]
            state["items"]["ROGUE"] = state["items"]["R2-01"]
            problems = tr.validate_record(state, expect_balance=False)
            joined = " | ".join(problems)
            for fragment in ("R2-01: prior exposure", "R2-01: decision recorded without a reason",
                             "R2-02: decision missing", "R2-02: no final product",
                             "R2-03: completion status missing", "R2-03: untimed gap without",
                             "R2-03: recorded clock values disagree", "ROGUE: not in the selection"):
                with self.subTest(fragment=fragment):
                    self.assertIn(fragment, joined)

    def test_validate_record_checks_the_selection_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            state = json.loads(json.dumps(s.state))
            state["selection_sha256"] = "0" * 64
            self.assertIn("selection digest does not match the stored selection",
                          tr.validate_record(state, expect_balance=False))

    def test_the_record_file_is_written_after_every_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            s.event("start", form(s, exposure="NO"))
            on_disk = json.loads(s.file.read_text())
            self.assertEqual(on_disk["items"]["R2-01"]["phase"], "decision")
            s.event("decide", form(s, decision="accept", reason="Fine."))
            on_disk = json.loads(s.file.read_text())
            self.assertEqual(on_disk["items"]["R2-01"]["phase"], "between_clocks")
            self.assertEqual(on_disk["selection_sha256"], tr.selection_digest(SYNTHETIC))

    def test_no_further_action_is_possible_once_every_item_is_done(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp)
            for _ in range(3):
                finish_item(s)
            with self.assertRaises(ValueError):
                s.event("start", {"timing_id": "R2-01", "phase": "not_started", "exposure": "NO"})
            self.assertIn("All ten items are recorded", s.page("tok"))

    def test_the_page_never_names_the_configuration_or_the_pathway(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = session(tmp, decisions={"R2-02": "block"})
            pages = [s.page("tok")]
            s.event("start", form(s, exposure="NO"))
            pages.append(s.page("tok"))
            s.event("decide", form(s, decision="accept", reason="Fine."))
            pages.append(s.page("tok"))
            s.event("finalize_start", form(s))
            pages.append(s.page("tok"))
            for page in pages:
                for leak in ("astra", "luna", "Astra", "Luna", "direct", "controlled",
                             "S-1", "rep_1", "repetition", "model"):
                    with self.subTest(leak=leak):
                        self.assertNotIn(leak, page)


if __name__ == "__main__":
    unittest.main()
