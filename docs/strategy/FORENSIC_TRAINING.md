# Training Guide: Forensic Accuracy

To "train" the Side Forensic Engine and eliminate false positives, we follow a three-level strategy. This moves the tool from simple pattern matching to deep logic awareness.

## Level 1: Heuristic Refinement (Regex)
The fastest way to train the tool is to refine the regex patterns in `forensic_audit/probes/`.

- **Action**: Update regex to be more specific (e.g., matching prefixes like `db.` or `session.`).
- **Example**: I just updated `PERF-001` to ignore standard dictionary `.get()` calls by requiring specific precursors (`db.`, `session.`, etc.).

## Level 2: Semantic Awareness (AST)
For high accuracy, we "train" the tool to use the Abstract Syntax Tree (AST). This allows the tool to understand the *intent* and *context* of code rather than just its text.

- **Action**: Add logic to `side.intel.analyzers.python.PythonAnalyzer` (or other language analyzers).
- **Benefit**: Distinguishes between `my_dict.get()` (Safe) and `db.users.get()` (Risky N+1) by inspecting the object type.

## Level 3: Regression Testing (The "Training Set")
The most powerful way to train the engine is to build a "Training Set" of positive and negative examples.

- **Action**: Add test cases to `backend/tests/forensic_audit/test_probes.py`.
- **Negative Tests**: Add code patterns that are *currently* causing false positives and assert they result in `AuditStatus.PASS`.
- **Positive Tests**: Add real-world bugs you want to catch and assert they result in `AuditStatus.FAIL`.

### How to add a new "Training Case":
1. Open `backend/tests/forensic_audit/test_probes.py`.
2. Add a new test function:
```python
@pytest.mark.asyncio
async def test_my_new_rule(tmp_path, probe_context):
    probe = MyProbe()
    test_file = tmp_path / "test.py"
    test_file.write_text("risky_code()")
    probe_context.files = [str(test_file)]
    results = await probe.run(probe_context)
    assert any(r.status == AuditStatus.FAIL for r in results)
```
3. Run `pytest backend/tests/forensic_audit/test_probes.py`.

By adding these tests, you are effectively "teaching" the tool exactly what you want it to find and what you want it to ignore.

---
*Reference: [ORGANISM_ARCHITECTURE.md](../ORGANISM_ARCHITECTURE.md)*
