# Design: Orchestration & Noise Reduction

> **Objective**: Achieving "Perfect DRY" and a high signal-to-noise ratio in forensic audits.

## 1. Unified Orchestration (Absolute DRY)
To prevent "Double Storage" bugs and architectural drift, the orchestration layer follows a strict delegation pattern.

- **The Runner**: `ForensicAuditRunner` is the single source of truth for executing probes and collecting results.
- **The Wrapper**: `ForensicEngine` acts as a thin interface for the rest of the application, delegating all logic to the Runner. This ensures that every audit follows the exact same path, whether triggered by CLI, MCP, or the IDE.

## 2. Smart Noise Exclusion
A signal-to-noise ratio of >90% is maintained through contextual filtering in the `SmartExclusion` engine.

- **Test Filtering**: `test_*.py` files are automatically excluded from Performance and Complexity probes to prevent false positives in non-production code.
- **Configuration Hygiene**: `.env`, `*.json`, and `*.yaml` files are excluded from architectural checks but remain subject to Secret Scanning (if not gitignored).
- **Debug Silence**: `debug_*.py` and `*.md` files are ignored by structural and code quality probes.

## 3. Managed Credit Pool (Side Proxy)
Reliability is enforced at the LLM layer via the `ManagedCreditPool`.

- **Key Rotation**: A round-robin scheduler cycles through `SIDE_POOL_KEYS` to distribute load and stay under rate limits.
- **Circuit Breaker**: Detects `429` (Rate Limit) or `401` (Unauthorized) errors, automatically "banning" the problematic key for a cooling period and failing over to the next available key.

---
*Reference: [ORGANISM_ARCHITECTURE.md](./ORGANISM_ARCHITECTURE.md) | [UNIFIED_ARCHITECTURE.md](./UNIFIED_ARCHITECTURE.md)*
