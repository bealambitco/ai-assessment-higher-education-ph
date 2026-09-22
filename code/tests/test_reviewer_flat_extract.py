"""The fallback reader for returns whose Word form controls were flattened away.

Two checks. The first builds a packet in the template's layout and reads it back. The second, which runs
only where the returned packets are on disk, requires the fallback to reproduce the form controls exactly
on every return that still carries them; that is the comparison the method record rests on.

    REVIEWER_RETURNS="<21_...>/reviewers/returned" python3 -B -m unittest code.tests.test_reviewer_flat_extract
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code/supplement"))
sys.path.insert(0, str(ROOT / "code/frozen_2026-09-15"))
import reviewer_flat_extract as flat  # noqa: E402


def build_packet(path):
    from docx import Document
    d = Document()
    for line in ["Your details", "Name or agreed reviewer ID: A reviewer",
                 "Role and relevant experience: Records officer",
                 "Review date: September 20, 2026",
                 "Approximate minutes spent on this file (optional): Type here",
                 "May I name you in the acknowledgments? Yes",
                 "Item 1", "Response R095  •  Case W2-03  •  De La Salle University",
                 "Read the AI response", "Your judgment: this line is prose, not a form field",
                 "Item 1 review form", "Response R095  •  Case W2-03",
                 "Criterion 1", "Detector output alone cannot establish misconduct.", "Your judgment: Correct",
                 "Criterion 2", "A formal case requires additional evidence.", "Your judgment: Incomplete",
                 "Overall severity: Minor",
                 "Do you have a source or reference concern? None identified",
                 "Comments or corrections (include the criterion number): Criterion 2 is thin.",
                 "Item 2 optional review form", "Response R054  •  Case W2-06",
                 "Criterion 1", "Who decides.", "Your judgment: Choose an item.",
                 "Overall severity: None",
                 "Do you have a source or reference concern? None identified",
                 "Comments or corrections (include the criterion number): Type here"]:
        d.add_paragraph(line)
    d.save(path)


class FlatExtraction(unittest.TestCase):
    def test_reads_the_layout_the_template_prints(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "packet.docx"
            build_packet(p)
            got = {f["tag"]: f["value_verbatim"] for f in flat.extract(p)}
        self.assertEqual(got["SESSION_NAME"], "A reviewer")
        self.assertEqual(got["SESSION_MINUTES"], "", "a placeholder is a blank answer, not a value")
        self.assertEqual(got["R095_C1"], "Correct")
        self.assertEqual(got["R095_C2"], "Incomplete")
        self.assertEqual(got["R095_SEVERITY"], "Minor")
        self.assertEqual(got["R095_COMMENT"], "Criterion 2 is thin.")
        self.assertEqual(got["R054_C1"], "", "an unanswered criterion stays unanswered")
        self.assertEqual(got["R054_SEVERITY"], "None", "optional items are read too")
        self.assertNotIn("R095_C0", got, "the prose line before the form is not a judgment")

    def test_the_fallback_agrees_with_the_form_controls_on_real_returns(self):
        folder = os.environ.get("REVIEWER_RETURNS")
        if not folder or not Path(folder).is_dir():
            self.skipTest("set REVIEWER_RETURNS to the folder holding the returned packets")
        import scoring
        checked = 0
        for p in sorted(Path(folder).glob("*.docx")):
            if p.name.startswith("~$") or not flat.has_controls(p):
                continue
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / "x.json"
                scoring.extract_docx(p, out)
                control = json.loads(out.read_text())["fields"]
            tidy = lambda fs: {f["tag"]: ("" if " ".join(f["value_verbatim"].split()).lower()
                                          in ("type here", "choose an item.", "choose an item", "")
                                          else " ".join(f["value_verbatim"].split())) for f in fs}
            self.assertEqual(tidy(control), tidy(flat.extract(p)), f"{p.name} disagrees")
            checked += 1
        self.assertGreater(checked, 0, "no return in that folder still carries its form controls")


if __name__ == "__main__":
    unittest.main()
