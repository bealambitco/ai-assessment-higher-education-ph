"""Read a returned reviewer packet whose Word form controls were lost in saving.

Reviewers fill the packets in Word content controls, and `scoring.extract_docx` reads those controls by
tag. A packet saved through another editor can arrive with the controls flattened into ordinary text: the
answers are still there, in the same places, but there is no tag to read. This module recovers them from
the document text in the packet's own fixed layout, and produces exactly the same `fields` shape, so a
flattened return is analysed by the same code as every other return.

It never guesses. A value is recorded only when it follows the label the template prints, and a blank
label yields a blank value, which the analysis treats as not judged. Extraction stays verbatim: nothing is
corrected, normalised or adjudicated.

Tested against returns that still carry their controls, where both readings must agree exactly
(`code/tests/test_reviewer_flat_extract.py`).
"""
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
ITEM_FORM = re.compile(r"^Item\s+\d+(\s+optional)?\s+review form$", re.I)
RESPONSE = re.compile(r"^Response\s+(R\d{3})\b")
CRITERION = re.compile(r"^Criterion\s+(\d+)\s*$", re.I)
LABELS = [("JUDGMENT", re.compile(r"^Your judgment:\s*(.*)$", re.I | re.S)),
          ("SEVERITY", re.compile(r"^Overall severity:\s*(.*)$", re.I | re.S)),
          ("REFERENCE_CONCERN", re.compile(r"^Do you have a source or reference concern\?\s*(.*)$", re.I | re.S)),
          ("COMMENT", re.compile(r"^Comments or corrections \(include the criterion number\):\s*(.*)$", re.I | re.S))]
SESSION = [("SESSION_NAME", re.compile(r"^Name or agreed reviewer ID:\s*(.*)$", re.I | re.S)),
           ("SESSION_ROLE", re.compile(r"^Role and relevant experience:\s*(.*)$", re.I | re.S)),
           ("SESSION_DATE", re.compile(r"^Review date:\s*(.*)$", re.I | re.S)),
           ("SESSION_MINUTES", re.compile(r"^Approximate minutes spent on this file \(optional\):\s*(.*)$", re.I | re.S)),
           ("ACKNOWLEDGMENT", re.compile(r"^May I name you in the acknowledgments\?\s*(.*)$", re.I | re.S))]
PLACEHOLDERS = {"type here", "choose an item.", "choose an item", "select", ""}


def paragraphs(path):
    """Every paragraph's text in document order, including text inside content controls."""
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    out = []
    for p in root.iter(f"{{{W}}}p"):
        out.append("".join(t.text or "" for t in p.iter(f"{{{W}}}t")).strip())
    return out


def _clean(v):
    v = re.sub(r"\s+", " ", v or "").strip()
    return "" if v.lower() in PLACEHOLDERS else v


def extract(path):
    """-> list of {'tag','value_verbatim'} in the same shape as scoring.extract_docx."""
    paras = paragraphs(path)
    fields, seen = [], set()
    for text in paras:
        for tag, rx in SESSION:
            m = rx.match(text)
            if m and tag not in seen:
                seen.add(tag)
                fields.append({"tag": tag, "value_verbatim": _clean(m.group(1))})
    response, criterion, in_form = None, 0, False
    for text in paras:
        if ITEM_FORM.match(text):
            in_form, response, criterion = True, None, 0
            continue
        m = RESPONSE.match(text)
        if m:
            if in_form:
                response, criterion = m.group(1), 0
            continue
        if not in_form or not response:
            continue
        m = CRITERION.match(text)
        if m:
            criterion = int(m.group(1))
            continue
        for tag, rx in LABELS:
            m = rx.match(text)
            if not m:
                continue
            if tag == "JUDGMENT":
                if criterion:
                    fields.append({"tag": f"{response}_C{criterion}", "value_verbatim": _clean(m.group(1))})
            else:
                fields.append({"tag": f"{response}_{tag}", "value_verbatim": _clean(m.group(1))})
                if tag == "COMMENT":
                    in_form = False
            break
    return fields


def has_controls(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    return any(s.find("w:sdtPr/w:tag", NS) is not None for s in root.findall(".//w:sdt", NS))


if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser(); ap.add_argument("--docx", required=True); ap.add_argument("--out")
    a = ap.parse_args()
    f = extract(Path(a.docx))
    if a.out:
        Path(a.out).write_text(json.dumps({"fields": f}, indent=2) + "\n")
    for x in f:
        print(f"{x['tag']:<24} {x['value_verbatim'][:70]}")
