# Architecture Sentinel: The Standards of the Organism

> "We are not writing scripts. We are building a Sovereign Organism."

## 1. The Prime Directives (Palantir-Level Rigor)
Every line of code written must pass these checks.

### 1.1 Structural Integrity
*   [ ] **Zero Cyclic Dependencies**: Modules must form a DAG (Directed Acyclic Graph).
*   [ ] **Layer Isolation**:
    *   `intel` (Brains) depends on `storage` (Memory).
    *   `mcp` (Interface) depends on `intel`.
    *   `storage` depends on NOTHING.
*   [ ] **Identity**: Every major component must have a globally unique URI concept.

### 1.2 Code Hygiene (The "10 Senior Devs" Rule)
*   [ ] **No "Magic"**: No global variables, no implicit state. Everything is injected.
*   [ ] **Strict Typing**: `mypy --strict` compliance. `Any` is forbidden unless wrapped in a specific adapter.
*   [ ] **Docstrings**: Functions >5 lines must explain the *Strategy* (Why), not just the *Mechanics* (How).

### 1.3 Scalability
*   [ ] **Async First**: Any I/O (Disk, DB, Network) must be `async`.
*   [ ] **Graceful Degradation**: If the DB is locked, queue the write. Do not crash.
*   [ ] **Telemetry**: Every major action must emit an *Event* to the `events` table.

## 2. Self-Audit Checklist (The Midway Check)
Before marking ANY task as "Done", run this protocol:

1.  **The Whisper**: Run `side scan <file>` (Our own tool).
2.  **The Mirror**: Does this code look like it belongs in a $10B IPO codebase?
    *   If "Maybe": **REFACTOR**.
    *   If "Yes": **COMMIT**.
