# Sidelith Pre-Summit Strategic Archives
**Classification:** SOVEREIGN EYES ONLY
**Location:** Undisclosed Safehouse, Palo Alto
**Attendees:** The Architect, The Ninja, The Moderator (Simulated)

---

## 📅 Session 001: The "Uncanny Valley" of Copilots
**Date:** 2026-01-15
**Topic:** Why does 10M context feel like 0 context?

**Notes:**
*   **The Problem:** Current "Context" is static. It's a "Bag of Words".
*   **The Insight (Karpathy):** "The AI doesn't know *why* the file exists. It only knows *what* is in it."
*   **The Solution:** We need to inject **Intent**, not just Content.
    *   *Action:* Investigate `git log` mining. If we know the commit message that created the file, we know the "Why".
*   **Friction Audit:**
    *   Copy-pasting from Terminal to Chat is "Caveman behavior".
    *   Why can't the Editor see the Terminal output directly?
    *   *Decision:* MCP Resource `side://terminal/last_error` is mandatory.

## 📅 Session 002: The Moat is the Protocol
**Date:** 2026-01-20
**Topic:** Fighting the Platform vs. Being the Platform.

**Notes:**
*   **Risk:** If VS Code adds "Context" natively, do we die?
*   **Defense:** No. Microsoft will never add "Sovereignty". They are incentivized to push Cloud.
*   **Our Wedge:** Privacy & Local Control. "The Sovereign Brain".
*   **Integration Strategy:**
    *   Do NOT build a VS Code Extension UI. It's too fragile.
    *   Build a **Headless MCP Server**. Let the AI be the UI.
    *   *Quote:* "The best UI is no UI. Just a smarter cursor."

## 📅 Session 003: The 100 Dimensions Brainstorm
**Date:** 2026-02-01
**Topic:** Defining the Physics of Software 2.0

**Raw Metrics Proposed:**
1.  **Time-to-First-Token (TTFT):** Must be <200ms for local models.
2.  **Context Relevance Score (CRS):** How many lines of the prompt were actually useful?
3.  **Correction Rate:** How often does the user delete the AI's code? (The "Rejection Vector").
4.  **Silicon Pulse:** Is the fan spinning? If yes, we failed.
5.  **Memory Leakage:** Does context degrade over time? (The "Amnesia Problem").
6.  **Switching Cost:** Alt-Tab is a failure state. Everything must be in the window.

## 📅 Session 004: The "Natural" Handshake
**Date:** 2026-02-02
**Topic:** How to recruit the CTOs?

**Strategy:**
*   Don't pitch "Features". Pitch "Solved Problems".
*   **To Kevin Scott (Microsoft):** "We solve your privacy problem. Enterprise customers won't use Copilot because of IP leaks. Sidelith acts as the Local Firewall (Pulse)."
*   **To Dario (Anthropic):** "We solve your Context Window budget. We distill 1GB of repo into 100KB of 'Strategic DNA'. You save tokens, we get better answers."
*   **To Aman (Cursor):** "We are your 'Long Term Memory'. Cursor is the CPU; Sidelith is the HDD."

## 📅 Session 005: Location Logistics
**Date:** 2026-02-02
**Topic:** Where do we hold the 40-Day Summit?

**Options:**
1.  **Villa Cimbrone (Ravello):**
    *   *Pros:* Isolated, "Infinity Terrace", intense philosophical weight.
    *   *Cons:* Hard to get to.
2.  **Cap Ferrat (France):**
    *   *Pros:* Near Nice airport, extreme luxury, tech heritage (nearby Sophia Antipolis).
    *   *Cons:* Distractions (Monaco).

**Decision:** **Ravello.** The difficulty of arrival acts as a filter. Only the serious will come.

---

## 📝 The "Karpathy List" (Draft Sketches)
*   *Idea:* "Software 2.0 isn't written; it's grown."
*   *Idea:* "The IDE is the Garden. The AI is the Gardener. Sidelith is the Soil."
*   *Metric:* "Garden Health" (Code Cohesion) vs "Weed Growth" (Tech Debt).
*   *Feature:* "Pruning". Automatic removal of dead code branches.

## 🚀 Launch Protocols
1.  **The Silent Launch:** Release the pip package. Tell no one.
2.  **The Whisper:** Tweet a screenshot of "Cursor + Sidelith" doing something impossible (e.g., recalling a decision from 3 years ago).
3.  **The Summit:** Invite the leaders once the buzz is organic.

**End of Archive**
