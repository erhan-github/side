# The Dream User Journey: "Alice's Day with Side"

**Objective**: Simulate the complete lifecycle of a new user ("Alice") from Product Hunt discovery to Power User.
**Actor**: Alice (Freelance Python Dev).
**Platform**: macOS.
**IDE**: Cursor.

---

## 🎭 Act I: The Discovery (Onboarding)
**Context**: Alice finds "Side" on Product Hunt. "The Silent Architect for your IDE."
**Action 1**: Simulating `pip install side-cli` (Virtual).
**Action 2**: Alice runs `side init`.
*   **System Event**: `watcher_daemon.py` starts.
*   **DB Event**: `SimpleDB` initializes. `profile` table created.
*   **Profile**: Tier = `Free`, Tokens = `50`.

## 🎭 Act II: The "Aha!" Moment (Value Realization)
**Context**: Alice starts coding her MVP (`mvp_auth.py`).
**Action 3**: Alice writes a file with a hidden anti-pattern (Arrow Pattern).
*   **System Event**: Watcher detects file modification.
*   **Audit**: `CodeQualityProbe` runs (FastAST).
*   **Telemetry**: `OP_SUCCESS` logged.
*   **Outcome**: Side silently records "Cognitive Complexity Critical" in `events`.

**Action 4**: Alice asks Cursor "Is my code clean?".
*   **System Event**: `MCP.query_context("Is my code clean?")` triggers.
*   **Result**: Side injects the finding: "Critical Arrow Pattern in mvp_auth.py:20".
*   **User Reaction**: "Wow, it knew before I pushed."

## 🎭 Act III: The Wall (Constraints)
**Context**: Alice loves it. She triggers a "Deep Audit" on her legacy codebase.
**Action 5**: Alice runs `side audit --deep`.
*   **System Cost**: 100 Tokens.
*   **Current Balance**: 50.
*   **System Event**: `InsufficientTokensError`.
*   **User UI**: "Deep Audit requires 100 SUs. You have 50. Upgrade to Pro?"

## 🎭 Act IV: The Upgrade (Revenue)
**Context**: Alice pays $29.
**Action 6**: Simulate Stripe Webhook -> `side.api.add_tokens(500)`.
*   **DB Event**: `update_token_balance(+500)`.
*   **New Balance**: 550.
*   **Profile**: Tier = `Pro`.

## 🎭 Act V: The Power User (Retention)
**Context**: Alice is unblocked.
**Action 7**: Alice re-runs `side audit --deep`.
*   **System Event**: `TaskDecomposer` splits the job.
*   **Execution**: 4 Parallel Workers process the audit.
*   **Outcome**: Full report generated.

**Action 8**: Gamification Check.
*   **System Event**: Check `xp_ledger`.
*   **Result**: "Level Up! You are now a Code Guardian."

---

## 🎬 Simulation Script Structure (`simulate_dream_journey.py`)
The script will programmatically execute these steps, printing "🎬 SCENE X" headers and verifying the DB state at each checkpoint.
