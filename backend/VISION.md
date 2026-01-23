# Sidelith Vision 🏛️

> **The System of Record for Engineering Intelligence**

## The Problem: Architectural Amnesia

Technical leaders and solo founders suffer from **Codebase Alzheimer's**.
- "Why did we choose MongoDB?"
- "Is this deployment configuration secure?"
- "What was the intent behind this weird `auth.ts` logic?"

Context is lost in Slack threads, mental notes, and fleeting chat logs with AI assistants.

## The Solution: Sidelith (Side)

**Side** is not a chatbot. It is a **Forensic Intelligence Layer** that treats your codebase as a crime scene of intent.

It operates on one core principle: **Sovereign Observability**.
1.  **Forensic Scanning**: It reads the AST (Abstract Syntax Tree), not just the text.
2.  **Intent Mapping**: It links "Business Goals" to "Code Functions".
3.  **The Monolith**: It maintains a *single*, persistent dashboard (`.side/MONOLITH.md`) that acts as the "Black Box" flight recorder for your project.

---

## Core Principles

### 1. Serious Intelligence (No Fluff)
*   **Old World**: "Hey! You have a 7-day streak! Good job!" 🤮
*   **Sidelith World**: "Warning: `auth.ts` has 3 critical vulnerabilities and 1 deployment blocker. Fix proposed." 🛑

### 2. The Value Vault
*   We do not track "Time Spent".
*   We track **Strategic Units (SUs)**: A measure of *Leverage*.
    *   Did you remove 500 lines of dead code? **+100 SUs**.
    *   Did you ship a feature with 0 tests? **-50 SUs**.

### 3. Sovereign Privacy
*   **Local-First**: Your strategy lives in `.side/local.db`.
*   **Zero Leak**: We verify your code without sending your secrets to a cloud training cluster.

---

## Architecture: The Forensic Loop

```mermaid
graph TB
    Codebase[Your Project] -->|File Watcher| Side[Sidelith Engine]
    Side -->|AST Analysis| Forensics[Forensic Findings]
    Forensics -->|Aggregation| Monolith[.side/MONOLITH.md]
    
    Monolith -->|Strategic Intel| Agents[AI Agents (Cursor/Windsurf)]
    Agents -->|Contextual Action| Codebase
```

### The "Sovereign Tools"
1.  **`run_audit`**: The Crime Scene Investigator. Finds security holes and "Deployment Gotchas" (e.g. Railway port mismatches).
2.  **`architectural_decision`**: The Judge. Renders verdicts on high-stakes technical choices.
3.  **`simulate`**: The Jury. Tests features against virtual user personas (e.g. "Tina the Teacher").
4.  **`verify_fix`**: The Executioner. Confirms if a patch *actually* solved the problem.

---

## Intelligence Domains

### 🔒 Security Forensics
*   Hardcoded secrets detection.
*   Auth flow validation (Next.js/Supabase quirks).
*   Dependency risk warnings.

### 🏗️ Deployment Intelligence
*   *Pre-Flight Checks*: "This `Dockerfile` exposes port 3000, but Railway expects $PORT. You will crash."
*   *Cookie Logic*: "You are setting a cookie but redirecting immediately. Next.js will drop this."

### 📉 Strategic Debt
*   Identifying "God Objects" (files > 500 lines).
*   Spotting "Orphaned Features" (code with no tests or active usage).
*   Calculating **Strategic IQ** (0-160 Health Score).

---

## The Monolith

The `.side/MONOLITH.md` file is our masterpiece. It is:
*   **Not a Log**: It is a *Dashboard*.
*   **Not Generated Once**: It is *Live*.
*   **Not Private**: It is meant to be checked into Git as the **System of Record**.

When a new developer (or AI Agent) joins the team, they just read the Monolith to understand *everything*.

---

## The Future: Recursive Strategy

We are building towards **Recursive Intent Verification**.
*   **Today**: "You have a security bug."
*   **Tomorrow**: "You are writing code that contradicts the Business Goal you set 3 weeks ago."

Side will be the "Circuit Breaker" that prevents AI Agents from drifting off-mission.

> **"We remember why you built it, so you don't have to."** 🏛️
