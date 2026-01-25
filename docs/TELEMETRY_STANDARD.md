# Telemetry Standard (The All-Seeing Eye)

> "What gets measured, gets managed. What gets logged, gets learned."

## 1. The Core Principle
Every operational unit in the organism must emit telemetry signals.
We do not use `print()`. We generally avoid raw `logging.info()`.
We use **Structured Events** stored in the Monolith.

## 2. The Implementation: `@monitor`
The `side.common.telemetry.monitor` decorator is the standard instrument.

### Usage
```python
from side.common.telemetry import monitor

@monitor("component_action_name")
def my_critical_function(data):
    # logic
    pass
```

### What it Captures
1.  **OP_SUCCESS**: If the function returns (includes duration_ms).
2.  **OP_ERROR**: If the function raises (includes trace and error msg).
3.  **Context**: The operation name is the primary key for aggregation.

## 3. Coverage Map
We have instrumented the following "Moving Parts":
*   **The Eyes**: `WatcherDaemon._process_event` -> `watcher_audit_cycle`
*   **The Bridge**: `MCP.trigger_strategy` -> `mcp_trigger_strategy`
*   **The Muscle**: `Worker.handle_security_scan` -> `worker_security_scan`

## 4. Querying Health
To see the health of the organism:
```sql
SELECT context FROM events WHERE type LIKE 'OP_%' ORDER BY id DESC;
```
