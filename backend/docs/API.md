# Side API Reference

> **The System of Record for Engineering Intelligence.**

This document details the 8 Sovereign Tools exposed by the Side MCP Server. These tools allow IDEs and Agents to access forensic intelligence, strategic reasoning, and virtual user simulation.

---

## 🛠️ Tool Index

| Tool | Purpose | Speed | Cost (SUs) |
|------|---------|-------|------------|
| `run_audit` | **Forensic Audit**: Scan code for security, quality, and deployment risks. | < 5s | 50 |
| `verify_fix` | **The Verifier**: Confirm if a fix actually resolved a specific finding. | < 2s | 10 |
| `architectural_decision` | **The Decider**: Get CTO-level verdicts on high-stakes choices. | < 1s | 25 |
| `strategic_review` | **The Audit**: High-level strategic sanity check (Expensive). | < 2s | 100 |
| `simulate` | **Virtual Users**: Test ideas against persistent persona simulations. | < 3s | 75 |
| `plan` | **Roadmap**: Read or update the Monolith's strategic directives. | < 1s | 0 |
| `check` | **Progress**: Mark directives as completed. | < 0.5s | 0 |
| `welcome` | **Onboarding**: Initialize Side for a new project. | < 5s | 0 |

---

## 🔍 Forensic Tools

### `run_audit`
**"The Scanner"**
Runs a full forensic scan of the codebase. Detects architectural violations, security holes, and "Deployment Gotchas" (e.g. Next.js auth cookies, Railway ports).

**Triggers**:
- "Audit my code"
- "Check for issues"
- "Security scan"

**Returns**:
- List of `Finding` objects with severity (CRITICAL, HIGH, etc.) and specific line numbers.
- Updates `.side/MONOLITH.md` automatically.

---

### `verify_fix`
**"The Gatekeeper"**
Critically verifies if a fix works. Agents MUST call this after applying a patch.

**Parameters**:
- `finding_type` (required): The ID or type of issue (e.g., "SEC-001").
- `file_path` (optional): Scope verification to a specific file.

**Returns**:
- ✅ **PASS**: The issue is gone.
- ❌ **FAIL**: The issue persists (with updated evidence).

---

## 🧠 Strategic Tools

### `architectural_decision`
**"The CTO"**
Provides instant, highly-contextual strategic decisions. Do NOT use for basic syntax help.

**Parameters**:
- `question` (required): High-stakes question (e.g., "Postgres vs Mongo?", "Microservices?").
- `context`: Additional background.

**Returns**:
- **Verdict**: YES / NO / DEFER.
- **Reasoning**: Economic and technical trade-off analysis.

---

### `strategic_review`
**"The Deep Thinker"**
Executes a comprehensive strategic audit of the *direction* rather than the code.

**Triggers**:
- "What should I focus on?"
- "Audit my strategy"

**Returns**:
- Prioritized list of Strategic Units (SUs) to capture.
- Alignment score against the `VISION.md`.

---

## 🔮 Simulation Tools

### `simulate`
**"The Virtual Users"**
Runs features or copy past a panel of simulated users (e.g., "Tina the Teacher", "Devin the Developer").

**Parameters**:
- `feature`: The idea or feature to test.
- `target_audience`: `teachers`, `developers`, `general`, `designers`.
- `content`: The text/code to evaluate.

**Returns**:
- Raw, unfiltered feedback from specific personas.
- "Emotional Response" score.

---

## 📋 Planning Tools

### `plan`
**"The Roadmap"**
Manages the Strategic Directives in the Monolith.

**Triggers**:
- "Add a goal: [goal]"
- "What's my plan?"

**Returns**:
- Current active plan from `.side/plan.md` or Monolith.

---

### `check`
**"The Ledger"**
Marks a strategic directive as complete, crediting the user's Value Vault.

**Parameters**:
- `goal`: The goal ID or title.
- `status`: `done` (default).

---

## 🚀 Setup Tools

### `welcome`
**"The Initiator"**
Runs automatically on first use. Detects stack, creates `.side` directory, and establishes baseline health.

---

## 🔒 Security & Privacy

- **Local-First**: All data stored in `.side/local.db`.
- **Fuzz-Resistant**: Rejects large payloads (>1MB).
- **Environment Isolation**: Subprocesses run *without* sensitive env vars to prevent leaks.
