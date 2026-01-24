# Strategic Observability Blueprint (Sidelith)

This document defines the "Truth Engine" observability standards for a CTO-level AI tool.

## 1. Philosophies
- **Silent Observability**: No popups, no clutter. Telemetry must be background noise until a threshold is crossed.
- **Outcome Tracking**: We don't just track "errors"; we track "Missed Strategic Opportunities."
- **Full Traceability**: A user click in the IDE must be traceable to an LLM token usage and a DB commit.

## 2. Event Taxonomy

### Product (PostHog)
| Event | Metadata | Trigger |
| :--- | :--- | :--- |
| `forensic_scan_started` | project_id, files_count | User initiates scan. |
| `finding_discovered` | severity, type, file_type | New finding saved to DB. |
| `strategic_leverage_delta` | previous_iq, new_iq | Score increases after resolution. |

### Error (Sentry)
- **Tagging**: Every error must be tagged with `side_version`, `project_path_hash`, and `mcp_transport`.
- **Breadcrumbs**: Automated breadcrumbs for every MCP tool call.

## 3. Implementation Checklist

### Backend
- [ ] Install `sentry-sdk` and `posthog-python`.
- [ ] Refactor `logging_config.py` for JSON production logs.
- [ ] Add a `@telemetry` decorator to `server_fast.py`.

## 4. The Unified Feedback Loop (Implemented)

The `InstrumentationEngine` now drives the "Brain".

### Leverage Ratio Calculation
> **Formula**: `(Strategic Decisions + Plans Completed) / (Hours Spent)` (Simplified)

### Adaptive Modes
The `Strategist` reads the Leverage Ratio on every prompt:
1.  **Coach Mode (< 2.0x)**: User is exploring or stuck.
    *   *AI Persona*: Explicit, verbose, teaching-oriented.
    *   *Goal*: Unblock and educate.
2.  **Partner Mode (> 5.0x)**: User is executing at speed.
    *   *AI Persona*: Concise, strategic, assumption-heavy.
    *   *Goal*: Maintain velocity, don't explain basics.

This closes the loop: **Better Observability -> Better AI Assistance.**
