# The Perfect Integration Strategy: Natural, Organic, Sovereign
**Status:** DRAFT (Summit V1)
**Constraint:** No Hidden APIs. No Hierarchy. Official Channels Only.

## The Core Philosophy
> "The best integration is the one you don't notice until you turn it off, and suddenly feel blind."

We do not build "Plugins" that fight for screen real estate.
We build **Context Servers** that feed the native intelligence of the editor.

## The Strategy: "Interface Parity" via MCP

We utilize the **Model Context Protocol (MCP)** as the Trojan Horse for deep integration.
*   **Why?** It is the *official*, sanctioned route for Claude, Cursor, and soon VS Code.
*   **How?** Sidelith exposes `side://` resources that the Editor *asks* for.

### 1. The Setup (The 5ms Handshake)
*   **Mechanism:** `side connect`
*   **Action:**
    1.  Detects the Editor (Cursor/VS Code/Claude).
    2.  Injects the `sidelith-serve` config into standard JSON (e.g., `claude_desktop_config.json`).
    3.  **Result:** Zero-click integration. The user installs the Python package, runs one command, and the Editor "Wakes Up".

### 2. The Context Injection (The Brain)
*   **User Action:** User types prompts in Composer/Chat.
*   **Sidelith Action:**
    *   **Resource:** `side://context/sovereign`
    *   **Protocol:** usage of `@sidelith` (or implicit context if configured).
    *   **Payload:** We don't just dump files. We inject **Strategic DNA**:
        *   "Last time you tried X, you failed because of Y." (Ledger)
        *   "The Project Mandate is Z." (Sovereign Rules)
*   **DevEx:** The AI suddenly "knows" things it shouldn't be able to know. "It feels like magic."

### 3. The Guardrails (The Pulse)
*   **User Action:** User saves a file or attempts to commit.
*   **Sidelith Action:**
    *   **Tool:** `check_safety(diff)` (Exposed to the Agent).
    *   **Protocol:** The Editor's Agent *chooses* to call Sidelith to verify its own code.
    *   **DevEx:** "Self-Correction". The Agent says: *"Wait, Sidelith Pulse rejected this because of a Secret Leak. Rewriting..."*
    *   **Why it wins:** It shifts the burden from the User (Linting error) to the Agent (Self-Refinement).

### 4. The Data Flow (Zero-Leak)
*   **Standard:** All traffic stays local (`localhost:stdio`).
*   **Airgap:** We utilize the official "Command" transport of MCP. No HTTP servers if not needed.
*   **Trust:** Because we use official pipes, we inherit the trust of the Platform.

## The Roadmap (40 Days)
*   **Day 1-10:** **MCP Server Hardening** (`backend/src/side/server.py`). Ensure 100% stability.
*   **Day 11-20:** **LSP "Ghost" Layer**. (Research Phase). Can we use Language Server Protocol to display "Strategic Diagnostics" (Blue Squiggles) for architectural drift?
*   **Day 21-30:** **The Universal Mesh**. Enabling multi-project context via the same MCP server instance.
*   **Day 31-40:** **The Launch**. Release `sidelith` on PyPI with "One-Line Integration".

## Conclusion
We don't need to ask Kevin Scott or Dario Amodei for permission.
We simply become the **Best Provider of Context** in their ecosystem.
When their users ask, "Why is Cursor so much smarter with Sidelith?", they will come to South Italy to shake *our* hands.
