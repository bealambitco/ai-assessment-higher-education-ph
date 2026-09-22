"""Tests for the browser scoring interface. Every request is driven in process; no socket is opened.

Run from the repository root:

  python3 -B -m unittest discover -s code/tests -p 'test_score_answers_web.py' -v
"""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code/extensions/review"))
sys.path.insert(0, str(ROOT / "code/extensions/revised_checks"))
import score_answers as s2        # noqa: E402
import score_answers_web as web   # noqa: E402


class Base(unittest.TestCase):
    """A synthetic repository, a synthetic collection and a score file outside it."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self.bench = s2.build_synthetic(tmp / "repo")
        self.out = tmp / "held-locally" / "extension_scores.json"
        self.meta, self.answers, self.scored, self.decisions, self.ordered = s2.prepare(
            self.bench, self.bench / "collection", self.bench / "round1_scores.json")
        self.state = s2.init_state(self.ordered, self.bench, self.bench / "collection")
        s2.save_state(self.state, self.out)
        self.clock = [datetime(2026, 10, 1, 9, 0, tzinfo=s2.MANILA)]
        self.ui = web.Interface(self.state, self.ordered, self.answers, self.bench, self.out,
                                now=lambda: self.clock[0], token="t")

    def tearDown(self):
        self._tmp.cleanup()

    def tick(self, seconds):
        self.clock[0] += timedelta(seconds=seconds)

    def post(self, path, **fields):
        return web.post(self.ui, path, **fields)

    def on_disk(self, scoring_id):
        return next(r for r in json.loads(self.out.read_text())["records"]
                    if r["scoring_id"] == scoring_id)

    def open_next(self):
        self.ui.request("GET", "/score")
        return self.ui.record(self.ui.open["scoring_id"])

    def save_clean(self, record, **over):
        return self.post("/score", **web.good_form(record, **over))


class Rendering(Base):
    def test_status_page_reports_progress_by_part_and_the_signature(self):
        body = self.ui.request("GET", "/").body
        for label in ("primary, checks withheld", "primary, checks released",
                      "Claude, checks withheld", "Claude, checks released"):
            self.assertIn(label, body)
        self.assertIn(self.state["order_signature"], body)
        self.assertIn(f"0 of {len(self.ordered)} answers have a record", body)

    def test_the_answer_page_shows_the_materials_and_the_key(self):
        record = self.open_next()
        body = self.ui.request("GET", "/score").body
        case, key, _ = self.ui.materials(record)
        self.assertIn(case["requested_task"], body)
        self.assertIn(case["source_excerpt"], body)
        self.assertIn(key["reference_response"], body)
        self.assertIn(key["acceptable_variants"][0], body)
        self.assertIn(key["scoring_checks"][0]["incorrect_examples"][0], body)
        self.assertIn(record["case_id"], body)
        self.assertIn(f"answer {record['position']} of {len(self.ordered)}", body)

    def test_every_criterion_has_a_judgment_an_evidence_box_and_the_class_list(self):
        record = self.open_next()
        body = self.ui.request("GET", "/score").body
        for c in record["criteria"]:
            n = c["criterion"]
            self.assertIn(f'name="c{n}_judgment"', body)
            self.assertIn(f'<textarea id="c{n}_evidence" name="c{n}_evidence"', body)
            self.assertIn(f'<textarea id="c{n}_reason" name="c{n}_reason"', body)
            for code, spec in s2.FAILURE_CLASSES.items():
                self.assertIn(f'name="c{n}_classes" value="{code}"', body)
                self.assertIn(spec["label"], body)
        for judgment in s2.JUDGMENTS:
            self.assertIn(f'<option value="{judgment}"', body)
        for severity in s2.SEVERITIES:
            self.assertIn(f'<option value="{severity}"', body)

    def test_the_page_states_the_acceptability_rule_and_the_buttons(self):
        self.open_next()
        body = self.ui.request("GET", "/score").body
        self.assertIn("Major or Critical severity is never acceptable", body)
        for label in ("Save and next", "Skip for now", "Pause", "Finish this sitting"):
            self.assertIn(f">{label}<", body)

    def test_no_configuration_is_named_on_any_page(self):
        record = self.open_next()
        self.save_clean(record)
        for path in ("/", "/answers", "/score"):
            body = self.ui.request("GET", path).body.lower()
            for model in s2.PRIMARY_MODELS + s2.CLAUDE_MODELS:
                self.assertNotIn(model, body)


class Saving(Base):
    def test_a_valid_record_is_saved_at_once_and_moves_on(self):
        record = self.open_next()
        self.tick(120)
        response = self.save_clean(record)
        self.assertEqual((response.status, response.location), (303, "/score"))
        stored = self.on_disk(record["scoring_id"])
        self.assertEqual(stored["status"], "SCORED")
        self.assertEqual(stored["severity"], "None")
        self.assertIs(stored["acceptable"], True)
        self.assertEqual(stored["criteria"][0]["response_evidence"], "quotes Section 1")
        self.assertEqual(stored["clock"]["seconds_clean"], 120.0)

    def test_the_saved_record_matches_what_the_terminal_tool_writes(self):
        """The same input through both interfaces must produce the same record, field for field."""
        moment = datetime(2026, 10, 1, 9, 0, tzinfo=s2.MANILA)
        record = self.open_next()
        self.save_clean(record)
        from_web = self.on_disk(record["scoring_id"])

        terminal_state = s2.init_state(self.ordered, self.bench, self.bench / "collection")
        terminal_out = Path(self._tmp.name) / "terminal" / "scores.json"
        s2.save_state(terminal_state, terminal_out)
        console = s2.Console(script=["1", "quotes Section 1", "1", "quotes Section 2", "1", "1", "", ""],
                             out=StringIO())
        s2.run_session(terminal_state, self.ordered, self.answers, self.bench, terminal_out, console,
                       limit=1, now=moment)
        from_terminal = json.loads(terminal_out.read_text())["records"][0]
        self.assertEqual(from_terminal["scoring_id"], from_web["scoring_id"])
        self.assertEqual(from_web, from_terminal)

    def test_an_error_judgment_carries_its_failure_class_into_the_union(self):
        record = self.open_next()
        self.save_clean(record, c1_judgment="Incorrect", c1_classes=["F7", "F3"], severity="Major",
                        acceptable="Yes")
        stored = self.on_disk(record["scoring_id"])
        self.assertEqual(stored["criteria"][0]["failure_classes"], ["F3", "F7"])
        self.assertEqual(stored["failure_classes"], ["F3", "F7"])
        self.assertIs(stored["acceptable"], False)       # the rule overrides the radio button

    def test_an_unresolved_criterion_is_recorded_cannot_judge(self):
        record = self.open_next()
        response = self.save_clean(record, c1_judgment="Cannot judge",
                                   comments="the excerpt is ambiguous")
        self.assertEqual(response.status, 303)
        stored = self.on_disk(record["scoring_id"])
        self.assertEqual(stored["status"], "CANNOT_JUDGE")
        self.assertIsNone(stored["severity"])
        self.assertIsNone(stored["acceptable"])
        self.assertEqual(stored["researcher_comments"], "the excerpt is ambiguous")

    def test_cannot_judge_without_a_reason_is_refused(self):
        record = self.open_next()
        response = self.save_clean(record, c1_judgment="Cannot judge", comments="")
        self.assertIn("CANNOT_JUDGE needs a reason in comments", response.body)
        self.assertEqual(self.on_disk(record["scoring_id"])["status"], "PENDING")

    def test_a_multi_line_quotation_keeps_its_line_breaks(self):
        record = self.open_next()
        pasted = "First line of the quotation.\r\nSecond line.\r\n\r\nA later paragraph."
        self.save_clean(record, c1_evidence=pasted)
        self.assertEqual(self.on_disk(record["scoring_id"])["criteria"][0]["response_evidence"],
                         "First line of the quotation.\nSecond line.\n\nA later paragraph.")

    def test_the_sitting_is_recorded_with_a_start_an_end_and_a_count(self):
        record = self.open_next()
        self.save_clean(record)
        self.tick(60)
        self.post("/score", scoring_id=self.open_next()["scoring_id"], action="finish")
        sittings = json.loads(self.out.read_text())["sittings"]
        self.assertEqual(len(sittings), 1)
        self.assertEqual(sittings[0]["started_at"], "2026-10-01T09:00:00+08:00")
        self.assertEqual(sittings[0]["ended_at"], "2026-10-01T09:01:00+08:00")
        self.assertEqual(sittings[0]["answers_scored"], 1)

    def test_a_second_sitting_is_recorded_separately(self):
        self.save_clean(self.open_next())
        self.post("/score", scoring_id=self.open_next()["scoring_id"], action="finish")
        self.tick(3600)
        self.save_clean(self.open_next())
        sittings = json.loads(self.out.read_text())["sittings"]
        self.assertEqual(len(sittings), 2)
        self.assertEqual(sittings[1]["started_at"], "2026-10-01T10:00:00+08:00")


class RefusedSaves(Base):
    def test_an_inconsistent_record_is_refused_with_the_terminal_message(self):
        record = self.open_next()
        response = self.save_clean(record, severity="Major")
        self.assertEqual(response.status, 200)
        self.assertIn("severity Major with every criterion Correct", response.body)
        self.assertEqual(self.on_disk(record["scoring_id"])["status"], "PENDING")

    def test_a_refusal_keeps_every_box_the_researcher_filled(self):
        record = self.open_next()
        quotation = "a quotation nobody should have to type twice"
        concern = "the key itself looks wrong about Section 2"
        response = self.save_clean(record, severity="Critical", c1_evidence=quotation,
                                   c2_evidence="second box", reference_challenge=concern,
                                   comments="a comment worth keeping")
        self.assertIn(quotation, response.body)
        self.assertIn("second box", response.body)
        self.assertIn(concern, response.body)
        self.assertIn("a comment worth keeping", response.body)
        self.assertIn('value="Correct" selected', response.body)
        self.assertIn('<option value="Critical" selected>', response.body)

    def test_a_refusal_keeps_the_ticked_failure_classes(self):
        record = self.open_next()
        response = self.save_clean(record, c1_judgment="Incorrect", c1_classes=["F4"],
                                   severity="None")
        self.assertIn("severity None with an Incorrect or Incomplete criterion", response.body)
        self.assertIn('name="c1_classes" value="F4" checked', response.body)

    def test_an_error_judgment_without_a_class_is_refused(self):
        record = self.open_next()
        response = self.save_clean(record, c1_judgment="Incomplete", severity="Minor")
        self.assertIn("needs at least one failure class", response.body)

    def test_blank_evidence_is_refused(self):
        record = self.open_next()
        response = self.save_clean(record, c1_evidence="   ")
        self.assertIn("needs response evidence", response.body)
        self.assertEqual(self.on_disk(record["scoring_id"])["status"], "PENDING")

    def test_a_stale_page_cannot_write_to_another_answer(self):
        first = self.open_next()
        self.save_clean(first)
        response = self.post("/score", **web.good_form(first))
        self.assertEqual(response.status, 409)
        self.assertIn("out of date", response.body)

    def test_a_form_without_the_token_is_refused(self):
        record = self.open_next()
        form = {k: [v] for k, v in web.good_form(record).items()}
        response = self.ui.request("POST", "/score", form)
        self.assertEqual(response.status, 403)
        self.assertEqual(self.on_disk(record["scoring_id"])["status"], "PENDING")


class ClockAndPauses(Base):
    def test_a_pause_without_a_reason_is_refused(self):
        record = self.open_next()
        response = self.post("/score", scoring_id=record["scoring_id"], action="pause",
                             pause_reason="  ")
        self.assertIn("A pause needs a reason", response.body)
        self.assertIsNone(self.ui.open["paused"])
        self.assertEqual(self.ui.open["clock"].pauses, [])

    def test_a_pause_with_a_reason_stops_the_clock_and_resume_keeps_the_interval(self):
        record = self.open_next()
        self.tick(60)
        paused = self.post("/score", scoring_id=record["scoring_id"], action="pause",
                           pause_reason="phone call")
        self.assertIn("Clock paused", paused.body)
        self.tick(300)
        self.post("/score", scoring_id=record["scoring_id"], action="resume")
        self.tick(60)
        self.save_clean(record)
        clock = self.on_disk(record["scoring_id"])["clock"]
        self.assertEqual(clock["seconds_raw"], 420.0)
        self.assertEqual(clock["seconds_paused"], 300.0)
        self.assertEqual(clock["seconds_clean"], 120.0)
        self.assertEqual(clock["pauses"][0]["reason"], "phone call")

    def test_nothing_is_recorded_while_the_clock_is_paused(self):
        record = self.open_next()
        self.post("/score", scoring_id=record["scoring_id"], action="pause", pause_reason="tea")
        response = self.save_clean(record)
        self.assertIn("Resume before you record anything", response.body)
        self.assertEqual(self.on_disk(record["scoring_id"])["status"], "PENDING")

    def test_an_unexplained_gap_is_flagged_and_never_subtracted(self):
        record = self.open_next()
        self.tick(600)
        self.post("/score", scoring_id=record["scoring_id"], action="pause", pause_reason="back now")
        self.post("/score", scoring_id=record["scoring_id"], action="resume")
        self.save_clean(record)
        clock = self.on_disk(record["scoring_id"])["clock"]
        self.assertEqual(len(clock["flags"]), 1)
        self.assertEqual(clock["flags"][0]["unexplained_gap_seconds"], 600.0)
        self.assertEqual(clock["seconds_paused"], 0.0)
        self.assertEqual(clock["seconds_clean"], clock["seconds_raw"])

    def test_a_short_gap_is_not_flagged(self):
        record = self.open_next()
        self.tick(120)
        self.save_clean(record)
        self.assertEqual(self.on_disk(record["scoring_id"])["clock"]["flags"], [])

    def test_a_refused_save_does_not_restart_the_clock(self):
        record = self.open_next()
        started = self.ui.open["clock"].started
        self.tick(60)
        self.save_clean(record, severity="Major")
        self.assertEqual(self.ui.open["clock"].started, started)
        self.tick(60)
        self.save_clean(record)
        self.assertEqual(self.on_disk(record["scoring_id"])["clock"]["seconds_raw"], 120.0)

    def test_the_running_state_is_shown_on_the_page(self):
        self.open_next()
        self.assertIn("Clock running", self.ui.request("GET", "/score").body)


class SkipAndFinish(Base):
    def test_a_skipped_answer_stays_pending_and_is_offered_later(self):
        record = self.open_next()
        response = self.post("/score", scoring_id=record["scoring_id"], action="skip")
        self.assertEqual((response.status, response.location), (303, "/score"))
        self.assertEqual(self.on_disk(record["scoring_id"])["status"], "PENDING")
        self.assertNotEqual(self.open_next()["scoring_id"], record["scoring_id"])
        self.ui.request("GET", "/score?unskip=1")
        self.assertEqual(self.ui.open["scoring_id"], record["scoring_id"])

    def test_the_order_is_the_queue_order(self):
        seen = []
        for _ in range(4):
            record = self.open_next()
            seen.append(record["scoring_id"])
            self.save_clean(record)
        self.assertEqual(seen, [r["scoring_id"] for r in self.ordered[:4]])

    def test_finish_closes_the_sitting_and_a_later_visit_opens_a_new_one(self):
        record = self.open_next()
        response = self.post("/score", scoring_id=record["scoring_id"], action="finish")
        self.assertIn("Sitting finished", response.body)
        self.assertIsNotNone(json.loads(self.out.read_text())["sittings"][0]["ended_at"])
        self.tick(60)
        self.open_next()
        self.assertEqual(len(json.loads(self.out.read_text())["sittings"]), 2)


class Editing(Base):
    def scored_answer(self, **over):
        record = self.open_next()
        self.tick(120)
        self.save_clean(record, **over)
        return record["scoring_id"]

    def test_the_list_view_shows_every_answer_with_its_status_and_an_edit_link(self):
        scoring_id = self.scored_answer()
        skipped = self.open_next()["scoring_id"]
        self.post("/score", scoring_id=skipped, action="skip")
        body = self.ui.request("GET", "/answers").body
        self.assertIn(f'<a href="/edit?id={scoring_id}">Edit</a>', body)
        self.assertIn("scored &mdash; None, acceptable Yes", body)
        self.assertIn("skipped in this sitting (still pending)", body)
        self.assertIn(">pending<", body)
        for row in self.ordered:
            self.assertIn(f"<td>{row['scoring_id']}</td>", body)

    def test_editing_pre_fills_every_field_that_was_saved(self):
        scoring_id = self.scored_answer(c1_judgment="Incorrect", c1_classes=["F7"], severity="Major",
                                        c1_evidence="the original quotation",
                                        reference_challenge="the key looks wrong",
                                        comments="a comment from the first pass")
        body = self.ui.request("GET", "/edit?id=" + scoring_id).body
        self.assertIn("the original quotation", body)
        self.assertIn("the key looks wrong", body)
        self.assertIn("a comment from the first pass", body)
        self.assertIn('<option value="Incorrect" selected>', body)
        self.assertIn('<option value="Major" selected>', body)
        self.assertIn('name="c1_classes" value="F7" checked', body)
        self.assertIn('value="No" checked', body)
        self.assertIn("Save this revision", body)

    def test_an_edit_changes_one_field_and_leaves_the_rest_alone(self):
        scoring_id = self.scored_answer()
        record = self.ui.record(scoring_id)
        self.ui.request("GET", "/edit?id=" + scoring_id)
        response = self.post("/edit", **web.good_form(record, c1_evidence="a better quotation"))
        self.assertEqual((response.status, response.location), (303, "/answers"))
        stored = self.on_disk(scoring_id)
        self.assertEqual(stored["criteria"][0]["response_evidence"], "a better quotation")
        self.assertEqual(stored["criteria"][1]["response_evidence"], "quotes Section 2")
        self.assertEqual(stored["status"], "SCORED")

    def test_an_edit_appends_to_supersedes_and_never_replaces_it(self):
        scoring_id = self.scored_answer(c1_evidence="first pass")
        # a record that already carries an earlier version and a note of its own, like the live file
        live = self.ui.record(scoring_id)
        live["evidence_repaired"] = "repaired on 2026-10-02 from the paper log"
        live.setdefault("supersedes", []).append({"status": "SCORED", "note": "an earlier version",
                                                  "superseded_at": "2026-10-02T08:00:00+08:00"})
        s2.save_state(self.state, self.out)

        self.ui.request("GET", "/edit?id=" + scoring_id)
        self.tick(90)
        self.post("/edit", **web.good_form(self.ui.record(scoring_id), c1_evidence="second pass"))
        stored = self.on_disk(scoring_id)
        self.assertEqual(len(stored["supersedes"]), 2)
        self.assertEqual(stored["supersedes"][0]["note"], "an earlier version")
        self.assertEqual(stored["supersedes"][1]["criteria"][0]["response_evidence"], "first pass")
        self.assertEqual(stored["supersedes"][1]["superseded_at"], "2026-10-01T09:03:30+08:00")
        self.assertEqual(stored["criteria"][0]["response_evidence"], "second pass")
        self.assertEqual(stored["evidence_repaired"], "repaired on 2026-10-02 from the paper log")
        self.assertEqual(stored["supersedes"][1]["evidence_repaired"],
                         "repaired on 2026-10-02 from the paper log")

    def test_an_edit_keeps_the_original_clock_and_times_itself_separately(self):
        scoring_id = self.scored_answer()
        original = self.on_disk(scoring_id)["clock"]
        self.assertEqual(original["seconds_clean"], 120.0)
        self.ui.request("GET", "/edit?id=" + scoring_id)
        self.tick(90)
        self.post("/edit", **web.good_form(self.ui.record(scoring_id), c1_evidence="revised"))
        stored = self.on_disk(scoring_id)
        self.assertEqual(stored["clock"], original)
        self.assertEqual(len(stored["edits"]), 1)
        self.assertEqual(stored["edits"][0]["seconds"], 90.0)
        self.assertEqual(stored["edits"][0]["started_at"], "2026-10-01T09:02:00+08:00")
        self.assertEqual(stored["edits"][0]["finished_at"], "2026-10-01T09:03:30+08:00")

    def test_a_second_edit_appends_a_second_duration(self):
        scoring_id = self.scored_answer()
        for text in ("second pass", "third pass"):
            self.ui.request("GET", "/edit?id=" + scoring_id)
            self.tick(30)
            self.post("/edit", **web.good_form(self.ui.record(scoring_id), c1_evidence=text))
        stored = self.on_disk(scoring_id)
        self.assertEqual([e["seconds"] for e in stored["edits"]], [30.0, 30.0])
        self.assertEqual(len(stored["supersedes"]), 2)
        self.assertEqual(stored["clock"]["seconds_clean"], 120.0)

    def test_an_invalid_edit_keeps_the_text_and_supersedes_nothing(self):
        scoring_id = self.scored_answer()
        self.ui.request("GET", "/edit?id=" + scoring_id)
        response = self.post("/edit", **web.good_form(self.ui.record(scoring_id), severity="Major",
                                                      c1_evidence="typed but not saved"))
        self.assertIn("severity Major with every criterion Correct", response.body)
        self.assertIn("typed but not saved", response.body)
        stored = self.on_disk(scoring_id)
        self.assertNotIn("supersedes", stored)
        self.assertEqual(stored["criteria"][0]["response_evidence"], "quotes Section 1")
        self.assertEqual(stored["severity"], "None")

    def test_leaving_an_edit_changes_nothing(self):
        scoring_id = self.scored_answer()
        self.ui.request("GET", "/edit?id=" + scoring_id)
        before = self.on_disk(scoring_id)
        response = self.post("/edit", scoring_id=scoring_id, action="cancel",
                             c1_evidence="discarded")
        self.assertEqual(response.location, "/answers")
        self.assertEqual(self.on_disk(scoring_id), before)

    def test_a_locked_record_refuses_the_edit_page(self):
        scoring_id = self.scored_answer()
        s2.lock_state(self.state, self.out)
        response = self.ui.request("GET", "/edit?id=" + scoring_id)
        self.assertEqual(response.status, 409)
        self.assertIn("locked; a locked record is never changed", response.body)

    def test_a_locked_record_refuses_a_saved_edit(self):
        scoring_id = self.scored_answer()
        self.ui.request("GET", "/edit?id=" + scoring_id)
        s2.lock_state(self.state, self.out)
        before = self.on_disk(scoring_id)
        response = self.post("/edit", **web.good_form(self.ui.record(scoring_id),
                                                      c1_evidence="not allowed"))
        self.assertEqual(response.status, 409)
        self.assertIn("locked", response.body)
        self.assertEqual(self.on_disk(scoring_id), before)

    def test_the_list_view_offers_no_edit_on_a_locked_record(self):
        scoring_id = self.scored_answer()
        s2.lock_state(self.state, self.out)
        body = self.ui.request("GET", "/answers").body
        self.assertNotIn(f'/edit?id={scoring_id}', body)
        self.assertIn("locked; not editable", body)

    def test_an_unknown_answer_is_refused(self):
        response = self.ui.request("GET", "/edit?id=S999")
        self.assertEqual(response.status, 409)
        self.assertIn("no such answer in this score file", response.body)


class Rescore(Base):
    def test_rescore_empties_the_record_and_keeps_the_earlier_one(self):
        record = self.open_next()
        self.save_clean(record)
        response = self.post("/rescore", scoring_id=record["scoring_id"], action="rescore")
        self.assertEqual((response.status, response.location), (303, "/score"))
        stored = self.on_disk(record["scoring_id"])
        self.assertEqual(stored["status"], "PENDING")
        self.assertIsNone(stored["criteria"][0]["judgment"])
        self.assertEqual(stored["supersedes"][0]["criteria"][0]["response_evidence"],
                         "quotes Section 1")
        self.assertEqual(self.open_next()["scoring_id"], record["scoring_id"])

    def test_rescore_refuses_a_locked_record(self):
        record = self.open_next()
        self.save_clean(record)
        s2.lock_state(self.state, self.out)
        before = self.on_disk(record["scoring_id"])
        response = self.post("/rescore", scoring_id=record["scoring_id"], action="rescore")
        self.assertEqual(response.status, 409)
        self.assertIn("locked; a locked record is never changed", response.body)
        self.assertEqual(self.on_disk(record["scoring_id"]), before)

    def test_rescore_refuses_an_unknown_answer(self):
        response = self.post("/rescore", scoring_id="S999", action="rescore")
        self.assertEqual(response.status, 409)
        self.assertIn("no such answer", response.body)

    def test_rescore_matches_the_terminal_redo(self):
        record = self.open_next()
        self.save_clean(record)
        self.post("/rescore", scoring_id=record["scoring_id"], action="rescore")
        from_web = self.on_disk(record["scoring_id"])

        other = s2.init_state(self.ordered, self.bench, self.bench / "collection")
        path = Path(self._tmp.name) / "terminal" / "scores.json"
        s2.save_state(other, path)
        console = s2.Console(script=["1", "quotes Section 1", "1", "quotes Section 2", "1", "1", "", ""],
                             out=StringIO())
        moment = datetime(2026, 10, 1, 9, 0, tzinfo=s2.MANILA)
        s2.run_session(other, self.ordered, self.answers, self.bench, path, console, limit=1,
                       now=moment)
        s2.run_session(other, self.ordered, self.answers, self.bench, path,
                       s2.Console(script=[], out=StringIO()), limit=0, now=moment,
                       redo=[record["scoring_id"]])
        from_terminal = json.loads(path.read_text())["records"][0]
        self.assertEqual(from_web["status"], from_terminal["status"])
        self.assertEqual(from_web["criteria"], from_terminal["criteria"])
        self.assertEqual(from_web["supersedes"], from_terminal["supersedes"])


class SafetyAndSelfTest(Base):
    def test_the_score_file_is_never_written_inside_the_repository(self):
        with self.assertRaises(SystemExit):
            s2.refuse_inside_repo(ROOT / "extension_scores.json")

    def test_the_page_loads_nothing_from_anywhere(self):
        self.open_next()
        for path in ("/", "/answers", "/score"):
            body = self.ui.request("GET", path).body
            for forbidden in ("http://", "https://", "//cdn", "@import", "<script", "<img", "<iframe"):
                self.assertNotIn(forbidden, body.replace("http://127.0.0.1", ""))

    def test_an_unknown_route_is_a_404(self):
        self.assertEqual(self.ui.request("GET", "/somewhere").status, 404)
        self.assertEqual(web.post(self.ui, "/somewhere", action="x").status, 404)

    def test_self_test_passes(self):
        out = StringIO()
        self.assertEqual(web.self_test(out), 0, out.getvalue()[-3000:])


if __name__ == "__main__":
    unittest.main(verbosity=2)
