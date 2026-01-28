# 🏗️ Sidelith Sovereign Architecture (V2)

**"Vertical Integration of Intelligence."**

This document describes the "God Diagram" - the flow of data through the Sidelith System.

---

## 1. The High-Level Flow

```
[User Input] --> [Watcher Daemon] --> [Pulse Engine] --> [Context Engine] --> [LLM Client] --> [Action]
```

1.  **Watcher Daemon**: Passive observer. Triggers on file save.
2.  **Pulse Engine**: <1ms Local Guardrail. Checks regex/entropy rules. Blocks sensitive data.
### 3. The Sovereign Brain (V3 Protocol: Fractal Context)
*   **Concept**: A distributed Merkle Tree of Context.
*   **Structure**:
    *   `root/.side/sovereign.json` (The Master Index).
    *   `subfolder/.side/local.json` (The Local Context).
*   **Advantage**: "Infinite Context". An Agent working in `subfolder` only loads `local.json` + `root/invariants`.
*   **Latency**: Sub-5ms context loading for any file path.

### 4. The Sovereign Governor (Resource Defense)
*   **Role**: Resource Defense.
*   **Logic**: Background thread monitors PID.
*   **Constraints**: Max 500MB RAM, Max 95% CPU (60s).
*   **Why**: To prevent "Fan Noise" and zombie processes.
5.  **Context Engine**: Reads `STRATEGY.md`, `memory.json`. Injects "Company Wisdom".
6.  **LLM Client**: The Neural Layer. Handles Failover (Groq -> OpenAI).
7.  **Action**: CLI Output, File Modification, or Strategic Report.

---

## 2. Component Deep Dive

### A. The Context Engine (`side.intel.auto_intelligence`)
*   **Role**: State Management.
*   **Logic**: Scans project root for Markdown artifacts.
*   **Why**: To solve the "3% Knowledge Problem". Sidelith knows the *entire* strategy.

### C. The Neural Circuit Breaker (`side.llm.client`)
*   **Role**: Reliability.
*   **Logic**: 
    *   Primary: Groq (Llama 3) - fast/cheap.
    *   Failover 1: OpenAI (GPT-4o) - if Groq 500s.
    *   Failover 2: Anthropic (Claude 3.5) - if OpenAI 500s.
*   **Why**: "The Brain Never Dies."

---

## 3. Data Sovereignty
*   **Storage**: Local JSON files (`.side/memory.json`, `.side/ledger.json`).
*   **Encryption**: Optional per-project.
*   **Cloud Policy**: Only "Anonymized Traces" leave the machine (if telemetry enabled). Secrets are scrubbed by `Pulse`.

---

## 4. The "Ghost" Policy
*   We do not ship dead code.
*   We do not ship "Mock" billing (All billing is handled by `LemonSqueezy` logic or real Credits).
*   We do not ship "Fat Tools" (Legacy Forensics).

> **Version**: 2.0.0
> **Date**: 2026-01-28
