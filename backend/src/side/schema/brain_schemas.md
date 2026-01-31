
# 🏛️ Sovereign Schema: Strategic Event Clock

## 1. Task Ledger Schema (`task_ledger_v1`)
Optimized for `task.md` ingestion.

```json
{
  "$schema": "https://side.ai/schemas/task_ledger_v1.json",
  "project_node": "ce8bc1f3-973d-4645-9611-637a0e3daee7",
  "temporal_anchor": {
    "birth_time": "2026-01-30T10:00:00Z",
    "last_sync": "2026-01-30T22:13:00Z",
    "event_clock": "T+14h"
  },
  "summary": {
    "total_tasks": 24,
    "completed_tasks": 24,
    "completion_rate": 1.0,
    "production_score": 100
  },
  "priorities": {
    "P0": {"total": 8, "done": 8, "weight": 1.0},
    "P1": {"total": 9, "done": 9, "weight": 0.7},
    "P2": {"total": 7, "done": 7, "weight": 0.4}
  },
  "items": [
    {
      "id": "t1",
      "priority": "P0",
      "description": "Fix tier.upper() NoneType",
      "status": "completed",
      "category": "bugfix"
    }
  ]
}
```

## 2. Decision Trace Schema (`decision_trace_v1`)
Optimized for `walkthrough.md` ingestion.

```json
{
  "$schema": "https://side.ai/schemas/decision_trace_v1.json",
  "trace_id": "P0_COMPLETION",
  "event_time": "2026-01-30T13:15:00Z",
  "origin_task_birth": "2026-01-30T10:00:00Z",
  "pivots": [
    {
      "subject": "Pricing Alignment",
      "decision": "$15/mo for Pro tier",
      "rationale": "Standardized across README and PRODUCT_README",
      "impact": "Consistency"
    }
  ],
  "proofs": [
    {
      "metric": "pulse_latency",
      "value": 0.015,
      "unit": "ms",
      "status": "verified",
      "benchmark_file": "backend/benchmark_pulse.py"
    }
  ],
  "remediations": [
    {
      "bug": "tier.upper() crashing on None",
      "fix_pattern": "(tier or 'FREE').upper()",
      "file": "backend/src/side/server.py",
      "lines": [63, 159]
    }
  ]
}
```
