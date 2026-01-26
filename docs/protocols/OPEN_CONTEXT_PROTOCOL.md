# Open Context Protocol (OCP) v1.0 🏛️

> **"Code without context is legacy the moment it is written."**

## 1. The Philosophy (Validated)
OCP is the standard for exchanging **Strategic Context** between the **System of Record** (Sidelith) and AI Agents (Cursor/Windsurf). This protocol has been **Validated & Operational** as of Jan 26, 2026.

## 2. The Data Model: The Sovereign Context Graph
Sidelith represents the project as a directed graph $G = (V, E)$, persisted in a local-first **Registry**.

### 2.1 Nodes ($V$)
Every entity is a Node with a globally unique URI (`side://<project>/<type>/<id>`).

| Type | URI Schema | Description |
| :--- | :--- | :--- |
| **Asset** | `asset/file/<path>` | A physical file or directory. |
| **Logic** | `logic/<type>/<id>` | Abstract architectural structures (e.g. Macros). |
| **Decision** | `decision/<id>` | A recorded strategic choice (e.g., "Use SQLite"). |
| **Finding** | `finding/<id>` | A forensic logic violation (Evidence). |

## 3. The Interface: MCP Bridge (Validated)
Side implements OCP via the **Model Context Protocol (MCP)**. This bridge provides AI Agents with 100% deterministic ground truth.

### 3.1 Implemented Resources
- `side://events/recent`: The last 50 events from the local clock.
- `side://findings/active`: Unresolved forensic evidence (The Registry).
- `side://monolith/summary`: High-level health and integrity score.

### 3.2 Implemented Tools
- `query_context(query: str)`: Semantic search over the Sovereign Registry.
- `trigger_strategy(intent: str)`: Decomposes complex architectural goals.

## 4. The Event Clock: Temporal Stream
Context is a stream of **Evidence**. Each event is an immutable record in the ledger.

```json
{
  "id": "evt_forensic_7xd2",
  "timestamp": "2026-01-26T10:00:00Z",
  "actor": "forensic_engine",
  "type": "INTEGRITY_VIOLATION",
  "payload": {
    "type": "CIRCULAR_DEADLOCK",
    "file": "backend/src/macros.rs",
    "severity": "CRITICAL"
  },
  "evidence": "Macro A expands into dependency on Macro B (Line 42)."
}
```

## 5. Summary
OCP ensures that AI Agents are no longer "Vibe Coding." They are informed by the **Engineering System of Record**, resulting in high-fidelity, maintainable code.

---
> **"Protocol of Intent. Speed of Evidence."** 🏛️
