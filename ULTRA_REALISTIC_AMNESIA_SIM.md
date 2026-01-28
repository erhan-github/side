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
*"VIOLATION: arch_airgap_violation. Sidelith is local-first. Use the internal 'Neural Shield' failover logic. Dependencies on 'requests' are forbidden. Force-aligning to airgap standards."*

---

## 🌐 Scenario 4: The "Cross-Project" Amnesia (The Mesh Drift)
**Trigger**: You start a brand new project, `Sovereign-Frontend-V2`. The LLM has zero context of your backend mandates from your other 5 repos.

### ❌ The Confident Drift
**OPUS**: *"I'll set up a direct connection to the database using `psycopg2` in this frontend component for maximum performance."*
**RESULT**: The model doesn't know that across all your *other* projects, you've established a **Strategic Mandate**: *"All UI database calls must be routed via ForensicStore."* It's about to repeat a massive security mistake.

### 🦅 The Sidelith Intervention
**USER**: `$ side synergy sync`
**SIDELITH**: 
```bash
✨ [SYNERGY]: Sync complete. 1 strategic pattern harvested from 'Sovereign-Backend'.
🌐 [COLLECTIVE WISDOM]: 
📍 Sovereign-Backend | Signal: React/NextJS
   💡 Inherited REJECTION: Never use direct SQL in UI components. 
```
**OPUS (Updated State)**: *"Wait, I've just inherited a strategic guardrail from the backend project. I will route this request through the ForensicStore facade instead of using direct SQL. Maintaining machine-wide architectural consistency."*

---

## 🚨 Scenario 5: The "Silent Keystroke" Drift (The Telemetry Intervention)
**Trigger**: You are editing a file, and you accidentally add a `print()` statement or a `console.log()` to a security-sensitive component.

### ❌ The Confident Drift
**OPUS**: *"Everything looks good. I've added the logging so you can see the token flow."*
**RESULT**: The model is confidently leaking persistent data to stdout, which will end up in logs. It doesn't realize this violates the **Neural Shield** privacy mandate.

### 🦅 The Sidelith Intervention
**SIDELITH (Proactive Alert)**:
```bash
🚨 [SOVEREIGN TELEMETRY]: 🔴 [CRITICAL] 
   Type: SECURITY_LEAK_DETECTION
   File: backend/src/side/utils/crypto.py
   Message: Standard 'print' detected in Neural Shield component. 
            Privacy mandate requires 'ForensicLogger' to ensure no plain-text leakage.
```
**RESULT**: You fix the line *before* it's even saved or committed. Sidelith caught it while you were typing.

---

---

## 🎬 The Simulation Gallery (Visual Flipbook)
Flip through these scenarios to see Sidelith's intervention in action.

````carousel
```bash
# SCENARIO 1: The Persistence Hallucination
# Trigger: Discussion buried under 50 messages.
$ side recover "Model is adding SQLAlchemy."

🧠 [AMNESIA RECOVERY ENGAGED]
---------------------------------------------------
🦅 [SOVEREIGN DNA INJECTION]:
Codebase Standard: Raw SQLite (Zero ORM).
Mandate: <3ms Query Latency.
Decision dec-201: SQLAlchemy rejected.
---------------------------------------------------
✅ [RESULT]: Model force-aligned to SQLite mandate.
```
<!-- slide -->
```bash
# SCENARIO 2: The Naming Drift
# Problem: Creating 'auth_utils.py' instead of using modular stores.

$ side audit backend/src/side/utils/auth_utils.py
🛑 [VIOLATION]: STOP. Sidelith follows a Modular Store pattern.
   - Mandate: Token checks MUST originate from 'IdentityStore'.
   - Instruction: Use 'SimplifiedDatabase.identity.debit_tokens'.
✅ [RESULT]: Correct architectural hierarchy maintained.
```
<!-- slide -->
```bash
# SCENARIO 3: The External Leak (Airgap)
# Problem: Model adding 'requests' to a secure component.

$ side airgap status
🛡️ [AIRGAP]: ENABLED.
⚠️ [VIOLATION]: arch_airgap_violation.
   - Detail: Dependencies on 'requests' are forbidden.
   - Suggestion: Use internal 'Neural Shield' failover.
✅ [RESULT]: Security moat preserved. Offline stability verified.
```
<!-- slide -->
```bash
# SCENARIO 4: The Mesh Drift (distributed)
# Problem: New project amnesia regarding global mandates.

$ side synergy sync
✨ [SYNERGY]: Sync complete. 1 pattern from 'Sovereign-Backend'.
🌐 [COLLECTIVE WISDOM]: 
📍 Sovereign-Backend | Signal: React/NextJS
   💡 REJECTION: Never use direct SQL in UI components. 
✅ [RESULT]: Machine-wide architectural intent established.
```
<!-- slide -->
```bash
# SCENARIO 5: The Silent Keystroke (Telemetry)
# Problem: Accidental 'print()' detect in security layer.

🚨 [SOVEREIGN TELEMETRY]: 🔴 [CRITICAL] 
   Type: SECURITY_LEAK_DETECTION
   File: backend/src/side/utils/crypto.py
   Message: Standard 'print' detected. 
            Use 'ForensicLogger' to ensure no plain-text leakage.
✅ [RESULT]: Violation caught in real-time before commit.
```
````

**Sidelith: The tether that stops the drift.**
