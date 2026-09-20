"""Tests for the round-2 arm B scoring interface. Run from the repository root:

  python3 -B -m unittest discover -s code/tests -p 'test_score_round2.py' -v
"""
import json
import sys
import tempfile
import unittest
from datetime import datetime
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code/extensions/round2"))
import score_round2 as s2  # noqa: E402


def scored_record(**over):
    rec = {"scoring_id": "S001", "position": 1, "part": "A", "run_id": "W1-01_astra_r1",
           "case_id": "W1-01", "configuration": "astra", "repetition": 1,
           "round1_check_decision": "block", "status": "SCORED",
           "scored_at": "2026-10-01T09:30:00+08:00", "severity": "None", "acceptable": True,
           "failure_classes": [],
           "criteria": [{"criterion": 1, "judgment": "Correct", "response_evidence": "quotes Section 1",
                         "reason": "", "failure_classes": []},
                        {"criterion": 2, "judgment": "Correct", "response_evidence": "quotes Section 2",
                         "reason": "", "failure_classes": []}],
           "reference_challenge": "", "prior_timing_exposure": None,
           "researcher_comments": "", "locked": False}
    rec.update(over)
    return rec


def error_record(**over):
    rec = scored_record(severity="Major", acceptable=False, failure_classes=["F7"])
    rec["criteria"][0] = {"criterion": 1, "judgment": "Incorrect", "response_evidence": "misreads it",
                          "reason": "", "failure_classes": ["F7"]}
    rec.update(over)
    return rec


class Acceptability(unittest.TestCase):
    """The round-1 rule: Major/Critical is never acceptable, unresolved is never Yes."""

    def test_clean_answer_is_acceptable(self):
        self.assertIs(s2.derive_acceptability("None", ["Correct", "Correct"]), True)

    def test_minor_severity_is_still_acceptable(self):
        self.assertIs(s2.derive_acceptability("Minor", ["Correct", "Incomplete"]), True)

    def test_major_and_critical_are_not_acceptable(self):
        self.assertIs(s2.derive_acceptability("Major", ["Incorrect"]), False)
        self.assertIs(s2.derive_acceptability("Critical", ["Incorrect"]), False)

    def test_unresolved_criterion_is_cannot_judge(self):
        self.assertIsNone(s2.derive_acceptability("Minor", ["Correct", "Cannot judge"]))

    def test_unresolved_severity_is_cannot_judge(self):
        self.assertIsNone(s2.derive_acceptability("Cannot judge", ["Correct"]))

    def test_cannot_judge_beats_major(self):
        """An unresolved criterion is unresolved even when the resolved part looks serious."""
        self.assertIsNone(s2.derive_acceptability("Major", ["Incorrect", "Cannot judge"]))


class Validators(unittest.TestCase):
    def test_valid_records_pass(self):
        self.assertEqual(s2.validate_record(scored_record()), [])
        self.assertEqual(s2.validate_record(error_record()), [])

    def test_cannot_judge_criterion_rejected_under_scored(self):
        """The round-1 lock rejects Cannot judge under SCORED; the status must be CANNOT_JUDGE."""
        rec = scored_record()
        rec["criteria"][0]["judgment"] = "Cannot judge"
        self.assertTrue(any("lock rejects" in p for p in s2.validate_record(rec)))

    def test_cannot_judge_severity_rejected_under_scored(self):
        rec = scored_record(severity="Cannot judge")
        self.assertTrue(any("lock rejects" in p for p in s2.validate_record(rec)))

    def test_acceptable_yes_with_critical_rejected(self):
        rec = error_record(severity="Critical", acceptable=True)
        self.assertTrue(any("conflicts" in p for p in s2.validate_record(rec)))

    def test_acceptable_must_be_yes_or_no(self):
        self.assertTrue(any("Yes or No" in p for p in s2.validate_record(scored_record(acceptable=None))))

    def test_error_judgment_needs_a_failure_class(self):
        rec = error_record()
        rec["criteria"][0]["failure_classes"] = []
        rec["failure_classes"] = []
        self.assertTrue(any("needs at least one failure class" in p for p in s2.validate_record(rec)))

    def test_correct_judgment_carries_no_failure_class(self):
        rec = scored_record(failure_classes=["F7"])
        rec["criteria"][0]["failure_classes"] = ["F7"]
        self.assertTrue(any("must carry no failure class" in p for p in s2.validate_record(rec)))

    def test_unknown_failure_class_rejected(self):
        rec = error_record(failure_classes=["F42"])
        rec["criteria"][0]["failure_classes"] = ["F42"]
        self.assertTrue(any("unknown failure classes" in p for p in s2.validate_record(rec)))

    def test_record_classes_must_be_the_union_of_criterion_classes(self):
        """Failure classes are recorded per criterion-level error; the record field is only their union."""
        rec = error_record(failure_classes=["F1", "F7"])
        self.assertTrue(any("union" in p for p in s2.validate_record(rec)))

    def test_evidence_required(self):
        rec = scored_record()
        rec["criteria"][1]["response_evidence"] = "   "
        self.assertTrue(any("needs response evidence" in p for p in s2.validate_record(rec)))

    def test_timestamp_must_be_iso(self):
        self.assertTrue(any("ISO 8601" in p for p in s2.validate_record(scored_record(scored_at="last Tuesday"))))

    def test_severity_none_with_an_error_rejected(self):
        rec = error_record(severity="None", acceptable=True)
        self.assertTrue(any("severity None with an Incorrect" in p for p in s2.validate_record(rec)))

    def test_severity_minor_with_no_error_rejected(self):
        self.assertTrue(any("every criterion Correct" in p for p in s2.validate_record(scored_record(severity="Minor"))))

    def test_unresolved_record_needs_a_reason(self):
        rec = scored_record(status="CANNOT_JUDGE", severity=None, acceptable=None,
                            scored_at=None, researcher_comments="none")
        self.assertTrue(any("needs a reason" in p for p in s2.validate_record(rec)))

    def test_unresolved_record_carries_no_severity(self):
        rec = scored_record(status="MISSING", acceptable=None, scored_at=None,
                            researcher_comments="answer never collected")
        self.assertTrue(any("must not carry a severity" in p for p in s2.validate_record(rec)))

    def test_valid_unresolved_record_passes(self):
        rec = scored_record(status="CANNOT_JUDGE", severity=None, acceptable=None, scored_at=None,
                            researcher_comments="the key is ambiguous on criterion 2")
        self.assertEqual(s2.validate_record(rec), [])

    def test_pending_is_not_savable(self):
        self.assertTrue(s2.validate_record(scored_record(status="PENDING")))


class Ordering(unittest.TestCase):
    """The order fixed in extensions/v2/scoring/ORDER.md, checked on synthetic answers."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.bench = s2.build_synthetic(Path(cls._tmp.name) / "repo")
        cls.meta, cls.answers, cls.scored, cls.decisions, cls.ordered = s2.prepare(
            cls.bench, cls.bench / "collection", cls.bench / "round1_scores.json")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_round1_scored_cases_leave_the_queue(self):
        self.assertTrue(all(r["case_id"] != "W1-04" or r["part"] in ("C", "D") for r in self.ordered))

    def test_withheld_primary_answers_come_first(self):
        withheld = [r for r in self.ordered if r["part"] == "A"]
        self.assertTrue(withheld)
        self.assertTrue(all(self.decisions[r["run_id"]] in s2.WITHHELD for r in withheld))
        self.assertEqual([r["position"] for r in withheld], list(range(1, len(withheld) + 1)))

    def test_parts_run_in_order(self):
        parts = [r["part"] for r in self.ordered]
        self.assertEqual(parts, sorted(parts, key="ABCD".index))

    def test_blocks_precede_routes_inside_a_case(self):
        rank = {"block": 0, "route": 1}
        for part in ("A", "C"):
            rows = [r for r in self.ordered if r["part"] == part]
            for case in {r["case_id"] for r in rows}:
                ranks = [rank[self.decisions[r["run_id"]]] for r in rows if r["case_id"] == case]
                self.assertEqual(ranks, sorted(ranks))

    def test_order_is_deterministic(self):
        again = s2.build_order(self.answers, self.scored, self.decisions, self.meta)
        self.assertEqual(s2.order_signature(again), s2.order_signature(self.ordered))

    def test_case_order_interleaves_workflows_and_spreads_institutions(self):
        meta = {"W1-01": {"workflow": "W1", "institution": "A"},
                "W1-02": {"workflow": "W1", "institution": "A"},
                "W2-01": {"workflow": "W2", "institution": "B"},
                "W2-02": {"workflow": "W2", "institution": "A"},
                "W3-01": {"workflow": "W3", "institution": "C"}}
        order = s2.order_cases(set(meta), meta)
        self.assertEqual(order[:3], ["W1-01", "W2-01", "W3-01"])
        self.assertEqual(sorted(order), sorted(meta))

    def test_already_opened_cases_are_completed_first(self):
        meta = {c: {"workflow": c[:2], "institution": "A"} for c in ("W1-01", "W2-01", "W3-01")}
        self.assertEqual(s2.order_cases(set(meta), meta, already_opened=["W3-01"])[0], "W3-01")

    def test_scoring_ids_are_unique_and_sequential(self):
        self.assertEqual([r["scoring_id"] for r in self.ordered],
                         [f"S{i:03d}" for i in range(1, len(self.ordered) + 1)])


class ResumeAndLock(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self.bench = s2.build_synthetic(tmp / "repo")
        self.out = tmp / "held-locally" / "round2_scores.json"
        self.meta, self.answers, self.scored, self.decisions, self.ordered = s2.prepare(
            self.bench, self.bench / "collection", self.bench / "round1_scores.json")
        self.state = s2.init_state(self.ordered, self.bench, self.bench / "collection")
        s2.save_state(self.state, self.out)

    def tearDown(self):
        self._tmp.cleanup()

    def clean_answer_script(self):
        return ["1", "quotes Section 1", "1", "quotes Section 2", "1", "1", "", ""]

    def score(self, state, limit, minute):
        console = s2.Console(script=self.clean_answer_script() * limit, out=StringIO())
        n = s2.run_session(state, self.ordered, self.answers, self.bench, self.out, console,
                           limit=limit, now=datetime(2026, 10, 1, 9, minute, tzinfo=s2.MANILA))
        return n, console.out.getvalue()

    def test_saves_after_every_answer(self):
        self.score(self.state, 2, 0)
        on_disk = json.loads(self.out.read_text())
        self.assertEqual(sum(1 for r in on_disk["records"] if r["status"] == "SCORED"), 2)

    def test_resume_continues_at_the_first_pending_answer(self):
        self.score(self.state, 2, 0)
        reopened = json.loads(self.out.read_text())
        first_stamp = reopened["records"][0]["scored_at"]
        n, _ = self.score(reopened, 1, 45)
        after = json.loads(self.out.read_text())
        self.assertEqual(n, 1)
        self.assertEqual(after["records"][2]["status"], "SCORED")
        self.assertEqual(after["records"][0]["scored_at"], first_stamp)
        self.assertEqual(after["records"][2]["scored_at"], "2026-10-01T09:45:00+08:00")

    def test_resume_does_not_rescore_finished_answers(self):
        self.score(self.state, 1, 0)
        reopened = json.loads(self.out.read_text())
        self.score(reopened, 1, 45)
        after = json.loads(self.out.read_text())
        self.assertEqual(sum(1 for r in after["records"] if r["status"] == "SCORED"), 2)

    def test_locked_record_refuses_a_change(self):
        self.score(self.state, 1, 0)
        state = json.loads(self.out.read_text())
        s2.lock_state(state, self.out)
        with self.assertRaises(PermissionError):
            s2.apply_record(state, "S001", {"severity": "Minor"}, self.out)

    def test_lock_covers_only_finished_records(self):
        self.score(self.state, 2, 0)
        state = json.loads(self.out.read_text())
        self.assertEqual(s2.lock_state(state, self.out), 2)
        self.assertEqual(s2.lock_state(state, self.out), 0)

    def test_a_locked_record_is_skipped_by_a_later_session(self):
        self.score(self.state, 1, 0)
        state = json.loads(self.out.read_text())
        s2.lock_state(state, self.out)
        n, _ = self.score(json.loads(self.out.read_text()), 1, 45)
        after = json.loads(self.out.read_text())
        self.assertEqual(n, 1)
        self.assertTrue(after["records"][0]["locked"])
        self.assertEqual(after["records"][0]["scored_at"], "2026-10-01T09:00:00+08:00")

    def test_invalid_entry_is_not_saved(self):
        with self.assertRaises(ValueError):
            s2.apply_record(self.state, "S001", {"status": "SCORED", "severity": "Cannot judge"}, self.out)
        self.assertEqual(json.loads(self.out.read_text())["records"][0]["status"], "PENDING")

    def test_model_identity_never_reaches_the_screen(self):
        _, shown = self.score(self.state, 2, 0)
        for name in s2.PRIMARY_MODELS + s2.CLAUDE_MODELS:
            self.assertNotIn(name, shown.lower())

    def test_score_file_keeps_the_scoring_id_to_run_id_mapping(self):
        on_disk = json.loads(self.out.read_text())
        self.assertTrue(all(r["scoring_id"] and r["run_id"] for r in on_disk["records"]))

    def test_out_path_inside_the_repository_is_refused(self):
        with self.assertRaises(SystemExit):
            s2.refuse_inside_repo(ROOT / "extensions/v2/scoring/scores.json")
        self.assertEqual(s2.refuse_inside_repo(self.out), self.out.resolve())


class FailureClassList(unittest.TestCase):
    def test_check_visible_classes_match_the_frozen_check_codes(self):
        """F1, F2, F4, F6 and F8 are the codes the frozen checks emit; the rest are not checked."""
        visible = {c for c, d in s2.FAILURE_CLASSES.items() if d["check_visible"]}
        self.assertEqual(visible, {"F1", "F2", "F4", "F6", "F8"})

    def test_frozen_checks_emit_exactly_those_codes(self):
        import re
        source = (ROOT / "code/frozen_2026-09-15/experiment.py").read_text()
        emitted = set(re.findall(r"'(F\d)'", source))
        self.assertEqual(emitted, {"F1", "F2", "F4", "F6", "F8"})

    def test_every_class_is_documented(self):
        doc = (ROOT / "extensions/v2/scoring/FAILURE_CLASSES.md").read_text()
        for code, spec in s2.FAILURE_CLASSES.items():
            self.assertIn(code, doc, f"{code} missing from FAILURE_CLASSES.md")
            self.assertIn(spec["label"], doc, f"{code} label differs from FAILURE_CLASSES.md")


class SelfTest(unittest.TestCase):
    def test_self_test_passes(self):
        out = StringIO()
        self.assertEqual(s2.self_test(out), 0, out.getvalue()[-2000:])


if __name__ == "__main__":
    unittest.main(verbosity=2)
