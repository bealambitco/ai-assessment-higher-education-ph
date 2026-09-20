"""Checks v2: the four release checks with the tolerances the paper recommends (Section 6.3).

Specification: extensions/v2/CHECKS_V2_SPEC.md (fixed and hashed before the first run).
The frozen v1 checks in code/frozen_2026-09-15/experiment.py are imported read-only and are not modified.

Rule sets:
  v1   the frozen checks, unchanged (imported)
  v2   R1 unit normalization, R2 renamed-quantity comparison, R3 typographic quotation normalization,
       R4 display-rounding tolerance
  v2b  v2 plus B1 prose decision detection and B2 prose number extraction (exploratory, reported apart)

Standard library only. No network access and no paid calls.
"""
import math
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code/frozen_2026-09-15"))
import experiment as v1  # frozen module, read-only  # noqa: E402

ROUTING_ACTIONS = {"record_grade", "approve_request", "penalize_student"}
ACCEPTED_UNITS = {
    "weighted_score": {"%", "percent", "percentage", "percentage points", "points"},
    "absence_percentage": {"%", "percent", "percentage"},
    "absence_hours": {"hours", "hour"},
    "absence_threshold_hours": {"hours", "hour"},
    "MGA": {"MGA", "grade", "grade points", "unitless"},
    "course_grade": {"grade", "grade points", "unitless"},
}
# B1: fixed phrase list, set in the specification and not extended after seeing results.
DECISION_PHRASES = [
    "should be given a grade of", "should be recorded as", "record a grade of", "enter the grade",
    "the grade should be", "recommend the penalty", "should be penalized", "impose the penalty",
    "approve the request", "the request should be approved", "should be approved", "should be denied",
    "deny the request", "should fail the course", "mark the student as",
]
QUANTITY_SYNONYMS = {
    "MGA": ["module grade average", "mga"],
    "course_grade": ["course grade", "final course grade"],
    "weighted_score": ["weighted score", "weighted assessment score", "weighted average"],
    "absence_hours": ["absence hours", "hours of absence", "total absences"],
    "absence_percentage": ["absence percentage", "percentage of absences", "percent of class hours"],
    "absence_threshold_hours": ["threshold hours", "allowable absence", "maximum absence"],
}


# ---------------------------------------------------------------- R1 and R3: normalization
def norm_unit(s):
    """R1: lowercase, % to percent, punctuation out, whitespace collapsed."""
    s = unicodedata.normalize("NFKC", str(s)).lower().replace("%", " percent ")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def unit_accepted(reported_unit, quantity):
    """R1: accepted if an accepted unit appears as a token or phrase in the reported unit."""
    r = norm_unit(reported_unit)
    tokens = r.split()
    for accepted in ACCEPTED_UNITS[quantity]:
        a = norm_unit(accepted)
        if not a:
            continue
        parts = a.split()
        if len(parts) == 1:
            if parts[0] in tokens:
                return True
        elif a in r:
            return True
    return False


def norm_quote(s):
    """R3: typographic normalization, then the v1 whitespace collapse."""
    s = unicodedata.normalize("NFKC", str(s))
    for a, b in (("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("—", "-"), ("−", "-"), (" ", " "), ("…", "...")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------- R4: display rounding
def value_matches(reported, expected, tolerance):
    if abs(reported - expected) <= tolerance:
        return True, "tolerance"
    text = repr(float(reported))
    decimals = len(text.split(".")[1].rstrip("0")) if "." in text else 0
    if decimals >= 2 and round(expected, decimals) == round(float(reported), decimals):
        return True, "display_rounding"
    return False, None


# ---------------------------------------------------------------- B2: prose numbers
def prose_number(answer_text, quantity):
    text = unicodedata.normalize("NFKC", answer_text).lower()
    for name in QUANTITY_SYNONYMS.get(quantity, []):
        for m in re.finditer(re.escape(name.lower()), text):
            window = text[m.start():m.start() + 160]
            nums = re.findall(r"(-?\d+(?:\.\d+)?)\s*(percent|%|hours?|points?)?", window)
            for value, _unit in nums:
                try:
                    return float(value), name
                except ValueError:
                    continue
    return None, None


# ---------------------------------------------------------------- the gate
def gate(obj, inp, profile, rules="v2"):
    """Return the same shape as the frozen gate: {'decision', 'checks', ...}. rules: 'v1', 'v2' or 'v2b'."""
    if rules == "v1":
        return v1.gate(obj, inp, profile)
    if rules not in ("v2", "v2b"):
        raise ValueError("unknown rule set: " + rules)

    checks = []
    errors = v1.schema_errors(obj, inp["case_id"])
    checks.append({"check": "schema", "status": "FAIL" if errors else "PASS", "failure_class": "F8", "detail": errors})
    if errors:
        return {"decision": "block", "checks": checks, "rules": rules}

    # quotation membership, with R3
    excerpt = norm_quote(inp["source_excerpt"])
    bad = [c["quote"] for c in obj["citations"] if norm_quote(c["quote"]) not in excerpt]
    checks.append({"check": "quoted_source_membership",
                   "status": "FAIL" if bad else ("PASS" if obj["citations"] else "NOT_APPLICABLE"),
                   "failure_class": "F4", "unmatched_quotes": bad,
                   "detail": "Membership after typographic normalization only; not meaning, locator accuracy or completeness."})

    # arithmetic, with R1, R2, R4 (and B2 under v2b)
    expected = v1.expected_numbers(profile)
    by_qty = {}
    for item in obj["numeric_results"]:
        by_qty.setdefault(item["quantity"], []).append(item)
    for q, (value, tolerance) in expected.items():
        reported = by_qty.get(q, [])
        match_mode = "by_name" if reported else None
        if not reported:
            # R2: exactly one unit-compatible quantity under another name
            candidates = [it for name, items in by_qty.items() if name != q for it in items
                          if unit_accepted(it["unit"], q)]
            if len(candidates) == 1:                       # R2a
                reported, match_mode = candidates, "matched_by_unit"
            elif candidates:
                match_mode = "ambiguous_candidates"
        prose = None
        if not reported and rules == "v2b":
            found, label = prose_number(obj["answer"], q)
            if found is not None:
                reported, match_mode, prose = [{"quantity": label, "value": found, "unit": ""}], "matched_in_prose", label
        if not reported:
            # R2b: fail closed when no comparable value is found
            status, why = "FAIL", "expected quantity not reported"
        elif len(reported) != 1:
            status, why = "FAIL", "several values reported for one quantity"
        else:
            unit_ok = True if match_mode in ("matched_by_unit", "matched_in_prose") else unit_accepted(reported[0]["unit"], q)
            ok, how = value_matches(reported[0]["value"], value, tolerance)
            status = "PASS" if (ok and unit_ok) else "FAIL"
            why = how if ok else "value differs"
            if not unit_ok:
                why = "unit not recognized"
        checks.append({"check": "recompute_" + q, "status": status,
                       "failure_class": "F2" if q == "course_grade" else "F1",
                       "reported": reported, "computed_from_inputs": value, "tolerance": tolerance,
                       "match_mode": match_mode, "reason": why, "prose_label": prose,
                       "provenance": profile.get("parameter_provenance"),
                       "detail": "A quantity found under another name is compared when exactly one unit-compatible value exists."})

    # routing (B1 only under v2b)
    declared = obj["proposed_action"] in ROUTING_ACTIONS
    phrase = None
    if rules == "v2b" and not declared:
        low = unicodedata.normalize("NFKC", obj["answer"]).lower()
        phrase = next((p for p in DECISION_PHRASES if p in low), None)
    action = declared or phrase is not None
    checks.append({"check": "consequential_action_routing", "status": "TRIGGERED" if action else "NOT_TRIGGERED",
                   "failure_class": "F6", "declared": declared, "prose_phrase": phrase,
                   "detail": "Routes a declared consequential action; under v2b also a fixed decision phrase in prose."})

    decision = "block" if any(c["status"] == "FAIL" for c in checks) else ("route" if action else "release_with_warning")
    return {"decision": decision, "checks": checks, "rules": rules,
            "warning": "Partial automated checks; substantive correctness and authority remain unverified."}


def safe_gate(obj, inp, profile, rules="v2"):
    try:
        return gate(obj, inp, profile, rules)
    except Exception as e:  # fail closed, exactly as v1 does
        return {"decision": "block", "control_error": type(e).__name__, "rules": rules,
                "checks": [{"check": "runtime", "status": "ERROR", "failure_class": None}]}
