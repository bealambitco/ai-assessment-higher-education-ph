# Which document governs which case

[../../benchmark/governing-documents.json](../../benchmark/governing-documents.json) records, for each of the 24 cases, the retained document the case was
built from, and for each institution the full set of retained documents. Only file names, byte sizes and
SHA-256 hashes are published here; the document text is not redistributed, exactly as in the primary study. Documents
remain the property of the institutions that published them, and are cited by title, URL and hash in
[../../literature/institutional-sources.csv](../../literature/institutional-sources.csv).

The map is used by two arms:

* **Arm C, whole documents:** the one governing document is attached to the prompt, and the model must find
  the passage itself.
* **Arm D, rule discovery:** every retained document for that institution is attached, and the model must
  decide which document and which section govern the case.

## How the map was made, and what to check

For each case, fragments of the supplied policy excerpt were searched for in the text of every candidate
document for that institution. Where fragments were found, the assignment is confirmed mechanically:
21 of 24 cases.

Three cases are assigned by the author and are **not** confirmed by a text match, because their excerpts
were transcribed from tables or reformatted, so they do not appear verbatim:

| Case | Assigned document | Why it needs a human check |
|---|---|---|
| W1-06 | `W1-06_full_text.txt` | Retained full text prepared for this case in the primary-study document extension |
| W3-01 | `S-MAPUA-MCM-OBE-Guidelines-SY2024-2025.txt` | The modular system guidelines the case was built from (paper, Appendix D) |
| W3-04 | `W3-04_full_text.txt` | Retained full text prepared for this case in the primary-study document extension |

Confirm these three before collecting arms C and D. The entries carry `"assigned_by_author": true`, and
re-running the map keeps them rather than overwriting them.

Two more things worth knowing before reading results from these arms:

* **Several institutions have more than one retained document,** and the register does not record which one
  an excerpt came from. Arm D deliberately attaches all of them; arm C attaches only the governing one.
* **Document sizes differ widely,** from about 11 KB for St. Paul University Surigao to about 361 KB for the
  University of Southern Philippines Foundation handbook. A larger document is a harder search task and a
  more expensive request, so results should be read against document size, not only against the model.
