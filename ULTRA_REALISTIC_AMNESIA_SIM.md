# 🎭 Confident Drift: Ultra-Realistic Amnesia Simulations

In modern IDEs like Cursor or Antigravity, LLMs (even Opus 4.5) don't say "I don't know." Instead, they **Confidently Drift**. They update files, refactor logic, and suggest libraries that violate your hidden "Strategic North Star" because that context has fallen out of their active window.

---

## 🌪️ Scenario 1: The "Old Context" Resumption (The Persistence Hallucination)
**Trigger**: User wakes up and re-opens a high-load chat from 12 hours ago. The discussion about the **Sovereign Ledger** using raw SQLite is buried under 50 messages of UI CSS tweaks.

### ❌ The Confident Drift (Opus 4.5)
**USER**: *"We need to add a table for 'Neural Heartbeat' logs."*
**OPUS**: *"Sure! I'll update the database schema. Since we want scalability, I'll use SQLAlchemy to define the Heartbeat model and set up an Alembic migration for you."*
**RESULT**: Opus has confidently assumed the project uses a standard ORM because that's "Industry Best Practice." It just modified 3 files and added a `migrations/` folder. **It destroyed the 3ms latency mandate.**

### 🦅 The Sidelith Intervention
**USER**: `$ side recover "Model is trying to add SQLAlchemy and migrations."`
**SIDELITH**: 
```bash
🧠 [AMNESIA RECOVERY ENGAGED]
---------------------------------------------------
🦅 [SOVEREIGN DNA INJECTION]:
Codebase Standard: Raw SQLite (Zero ORM).
Mandate: <3ms Query Latency. Key-Value Settings stored in 'settings' table.
Decision dec-201: SQLAlchemy rejected due to cold-boot overhead.

⚡ [INSTRUCTION]: Reverting migrations. Use 'SimplifiedDatabase' facade only.
---------------------------------------------------
```
**OPUS (Updated State)**: *"My apologies. I see now. I will remove the SQLAlchemy models and implement the Heartbeat logs using the raw SQLite schema within the ForensicStore. Proceeding with the 3ms latency standard."*

---

## 🌩️ Scenario 2: The "Lazy Prompter" (The Naming Drift)
**Trigger**: User is exhausted. They've spent 8 hours coding. They open a new file and say: *"Add a check for token balance before every tool call."*

### ❌ The Confident Drift (Opus 4.5)
**OPUS**: *"I'll implement a decorator in a new `auth_utils.py` file to handle this."*
**RESULT**: Opus just created a new top-level file. It doesn't know that Sidelith follows a **Modular Store Architecture** (`side.storage.modules.identity`). It's creating "Code Debt" because it doesn't see the existing architecture.

### 🦅 The Sidelith Intervention
**SIDELITH (Auto-Injection via Audit)**:
*"STOP. Sidelith follows a Modular Store pattern. Token checks MUST originate from 'IdentityStore'. Do not create 'auth_utils.py'. Use 'SimplifiedDatabase.identity.debit_tokens'."*

---

## 🔄 Scenario 3: The "Cheap Model" Loop (The External Leak)
**Trigger**: User is using a faster model for "routine" fixes in `LLMClient`.

### ❌ The Confident Drift
**OPUS**: *"I'll add a health check for the API using the `requests` library."*
**RESULT**: The model is confidently adding an external dependency that violates the **Sovereign Airgap**. It's making the system vulnerable to cloud-leaks.

### 🦅 The Sidelith Intervention
**SIDELITH**: 
*"VIOATION: arch_airgap_violation. Sidelith is local-first. Use the internal 'Neural Shield' failover logic. Dependencies on 'requests' are forbidden. Force-aligning to airgap standards."*

---

## 🎭 Why this happens in Antigravity/Cursor:
1. **Context Window Saturation**: The LLM prioritizes the *last 10 messages*. Strategic decisions from file #1 (made 100 messages ago) are gone.
2. **Standardization Bias**: High-tier models are trained on ALL GitHub code. They naturally drift toward "Standard" solutions (SQLAlchemy, requests, JWTs) unless **constantly** tethered to your **Private Sovereign Reality**.

**Sidelith: The tether that stops the drift.**
