# Training Guide: Forensic Fidelity 🏛️

To ensure Sidelith remains the **System of Record** for your project, the Forensic Engine must prioritize accuracy over volume. This guide explains how to eliminate "Speculative Noise" and move from pattern matching to **Deterministic Analysis**.

## Level 1: Heuristic Refinement (Regex)
The fastest way to train the tool is to refine the regex patterns in `forensic_audit/probes/`.

- **Action**: Update regex to be more specific (e.g., matching prefixes like `db.` or `session.`).
- **Example**: I just updated `PERF-001` to ignore standard dictionary `.get()` calls by requiring specific precursors (`db.`, `session.`, etc.).

## Level 2: Semantic Awareness (The Context Graph)
For high fidelity, the tool uses the Abstract Syntax Tree (AST) to understand the *logical topology* of the project. This allows the system to distinguish between generic code and **Business Intent**.

- **Action**: Add logic to `side.intel.analyzers.python.PythonAnalyzer`.
- **Benefit**: Distinguishes between `my_dict.get()` (Safe) and `db.users.get()` (Architectural Risk) by inspecting the object type and cross-referencing with the **Sovereign Context Graph**.

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
