# Open Context Protocol (OCP) v0.1

> "Code without context is legacy the moment it is written."

## 1. The Philosophy
OCP is a standard for exchanging **Strategic Context** between Development Environments (IDEs), Agents (AI), and Humans.
It rejects the "Files-only" view of software development.
It asserts that **Decisions, Intent, and History** are first-class citizens.

## 2. The Data Model: The Context Graph
The world is represented as a directed graph $G = (V, E)$.

### 2.1 Nodes ($V$)
Every entity is a Node with a globally unique URI (`side://<project>/<type>/<id>`).

| Type | URI Schema | Description |
| :--- | :--- | :--- |
| **Asset** | `asset/file/<path>` | A physical file or directory. |
| **Concept** | `concept/auth/logic` | An abstract architectural concept. |
| **Plan** | `plan/<id>` | A task, goal, or objective (from `task.md` or DB). |
| **Decision** | `decision/<id>` | A recorded choice (e.g., "Use SQLite"). |
| **Person** | `agent/<id>` | A human or AI contributor. |

### 2.2 Edges ($E$)
Relationships define the meaning.

| Relationship | Direction | Meaning |
| :--- | :--- | :--- |
| `IMPLEMENTS` | Asset -> Plan | This file exists to fulfill this plan. |
| `ENFORCES` | Asset -> Concept | This test ensures this concept works. |
| `AUTHORED` | Person -> Decision | Who made the call. |
| `MODIFIED` | Event -> Asset | Temporal causality. |

## 3. The Event Clock: Temporal Stream
Context is not static. It is a stream of **Events**.
Each event is an immutable record in the `events` ledger.

```json
{
  "id": "evt_12345",
  "timestamp": "2026-01-25T10:00:00Z",
  "actor": "user_erhan",
  "type": "CODE_MODIFICATION",
  "payload": {
    "file": "auth.py",
    "diff_summary": "+50 lines"
  },
  "outcome": {
    "status": "VIOLATION",
    "rule": "no_arrow_pattern"
  }
}
```

## 4. The Interface: MCP (Model Context Protocol)
Side implements OCP via the **Model Context Protocol**.

### 4.1 Resources
- `side://graph/summary`: Current high-level status.
- `side://graph/node/{uri}`: Detailed context for a specific node.
- `side://stream/recent`: Last 50 events.

### 4.2 Prompts
- `query_context(query: str)`: Semantic search over the Monolith.
- `get_decision_history(file: str)`: Why did this file change?

## 5. Implementation Strategy
1.  **Store**: SQLite (`SimpleDB`) holds the Graph and Events.
2.  **Server**: `side-mcp` exposes SQLite via MCP.
3.  **Client**: Cursor/Windsurf connects to `side-mcp`.
