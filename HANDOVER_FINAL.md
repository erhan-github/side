# 🦅 The Sovereign Handover: Sidelith Prime

**Welcome to the Engineering System of Record.**
If you are reading this, you have been entrusted with the "Black Box" of the software industry.

## 1. The Philosophy (The Pivot)
We do not build linters. We build **Forensic Infrastructure**.
-   **We Cut the Fat**: We killed local encryption (Fernet) to achieve **1.5ms latency**. Do not add it back without Board approval.
-   **We Sell the Data**: The regex is free. The **Precedent Card** (Netflix/Uber usage data) is the product.
-   **We Capture Intent**: `side fix` records the *reasoning* behind the code.

## 2. The Monorepo Structure (Map of the Empire)

### 🧠 The Kernel (`backend/src/side`)
This is the "Pulse Engine". It is Python today, Rust tomorrow.
-   `pulse.py`: **The Heart**. 1.5ms regex engine. No dependencies.
-   `cli.py`: **The Skin**. Premium "Precedent Card" user interface.
-   `scout.py`: **The Eyes**. Precedent verification logic.

### 🗄️ The Memory (`.side/`)
The local state of the Sovereign.
-   `rules/*.json`: Plain text invariants. (Transparency > Secrecy).
-   `sovereign.json`: The Anchor (Constitution).

### ☁️ The Interface (`web/`, `frontend/`)
(Placeholder) The Command Center dashboard. Focus on the CLI for now.

## 3. The Prime Directives (For New Hires)
1.  **Speed is the Law**. If `side pulse` exceeds 5ms, revert the PR.
2.  **Trust is the Coin**. Never hallucinate a precedent. If we say "Netflix uses this," it must be verifiable.
3.  **Intent is the Goal**. A bug fix without a "Decision Trace" is incomplete work.

---

**Current Status**:
-   **Architecture**: Fat-Trimmed & Optimized (Plain Text).
-   **Latency**: ~1.59ms.
-   **Next Objective**: Scale the "Global Mesh" (Cloud API).

*Welcome to the watch.* 🚀
