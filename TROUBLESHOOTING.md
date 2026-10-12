# Troubleshooting Report

Keep adding to this as you build — it becomes one of your required
capstone deliverables. Use one entry per problem you hit.

## Entry template

**Problem:**
_(What broke, and what you saw — error message, wrong output, etc.)_

**Investigation:**
_(What you checked to find the cause — logs, print statements, docs.)_

**Root cause:**
_(The actual reason it was happening.)_

**Fix:**
_(What you changed.)_

**Prevention:**
_(How you'd stop this happening again — a test, a check, better error handling.)_

---

## Example entry (delete once you have your own)

**Problem:** `data_validator.py` crashed with `KeyError` on a CSV missing
a column.

**Investigation:** Added a print of `reader.fieldnames` before processing
rows and noticed the CSV was missing the `email` header entirely.

**Root cause:** No check for required columns before reading rows —
the code assumed the CSV always matched the expected format.

**Fix:** Added a `validate_csv` check that compares `reader.fieldnames`
against `required_fields` and raises a clear `ValueError` before
processing starts.

**Prevention:** Added a unit test that passes a CSV with a missing
column and asserts the correct error is raised.
