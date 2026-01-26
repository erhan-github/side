# Design: The Nervous System (Data Strategy)

> **Philosophy**: Your data is an asset, not a log file. It stays on your machine, evolves with your code, and is privacy-hardened by default.

## 1. The Anatomy of "Side DB"
We do not use a volatile JSON storage. We use a **Relational SQLite Engine** ([.side/side.db](../.side/side.db)) optimized for high-frequency forensics and multi-year persistence.

### Structural Intelligence (The "Smart" Part)
Unlike typical linter logs, the Side Nervous System is **Structural**:
- **Stable IDs**: Every finding is hashed from its *structure* (`Project:Check:File:Line`). If the same error appears 100 times, it is stored as **1 Record** with updated timestamps.
- **Auto-Purge (The "Checkmark")**: We don't make you manually "mark as fixed."
    - **Run Audit** -> System detects issues.
    - **Fix Code** -> System detects absence.
    - **DB Action**: Automatically marks the finding as `resolved_at = NOW`.
    - *Result*: Zero maintenance. The documentation reflects the *current truth*.

## 2. Privacy & Persistence
- **Location**: `.side/side.db`
- **Retention**: Permanent history allows for "Regression Velocity" tracking (detecting habit cycles).
- **Security**: Database files are restricted to user-only access (`chmod 600`). No other workspace or user can access your project's intelligence.

## 3. The Knowledge Graph
The Nervous System links the following tables to create the "Living Organism" memory:
- `Findings`: The "Eyes" (What we see).
- `Decisions`: The "Brain" (Why we changed it).
- `Outcomes`: The "Soul" (Value created).
- `Snapshots`: The "Memory" (Context Resurrect).

---
*Reference: [ORGANISM_ARCHITECTURE.md](./ORGANISM_ARCHITECTURE.md)*
