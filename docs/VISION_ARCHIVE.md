# The Lost Vision: Future Capabilities Archive

> **Status**: Inactive / Dormant.
> **Purpose**: This document preserves the "Soul" of the features we paused or pruned to focus on Launch V1. These are the "Step 2" innovations that will make Side a unicorn.

---

## 1. The Virtual CTO (Proactive Service)
* **File**: [proactive_service.py](../backend/src/side/services/proactive_service.py) (Dormant)
* **The Idea**: Instead of waiting for you to ask "How do I build auth?", Side watches you type `TODO: Implement Login` and *interrupts* (gently) with:
    > "💡 **Strategy Shortcut**: Don't build Auth from scratch. Use Supabase/Clerk. It saves 3 weeks."
* **Why it matters**: It shifts Side from a "Code Assistant" (who helps you dig a hole faster) to a "Strategic Partner" (who tells you to stop digging).
* **Key Mechanics**:
    *   **Friction Detection**: Scans for `HACK`, `TODO`, `FIXME`.
    *   **OSS Leverage**: Maps common wheel-reinvention patterns (Auth, Billing, Jobs) to best-in-class OSS tools.

## 2. The Telepathic Context (Context Tracker)
* **File**: [context_tracker.py](../backend/src/side/services/context_tracker.py) (Dormant)
* **The Idea**: Side should *know* what you are doing without you saying it.
* **How**: It watches your Git commits and file edits in real-time.
    *   If you edit `login.tsx` + [middleware.ts](../web/middleware.ts), it infers: **Focus: Authentication**.
    *   If you edit `docker-compose.yml`, it infers: **Focus: DevOps**.
* **Why it matters**: The Monolith dashboard can dynamically highlight "Security Risks" when you are working on Auth, or "Performance" when you are working on DB schemas. It makes the dashboard alive.

## 3. The Authority Engine (Advanced Scoring)
* **File**: [advanced_scoring.py](../backend/src/side/intel/advanced_scoring.py) (Research)
* **The Idea**: Not all advice is equal. "How to optimize Postgres" from *Martin Kleppmann* is worth 100x more than a random Medium article.
* **How**: We manually curated a "God Tier" list of experts (Julia Evans for Linux, Dan Abramov for React, Troy Hunt for Security).
* **Why it matters**: Side filters the noise. We don't just give you "an answer"; we give you **The Answer** backed by the highest authority in that specific domain.

## 4. The Graph Brain (Intelligence Kernel)
* **File**: `side/intelligence/` (Deleted Zombie)
* **The Idea**: To truly understand code, you need a Graph, not just text.
* **How**: The [GraphKernel](../backend/src/side/intel/analyzers/polyglot.py) was designed to parse code into Nodes (Functions, Classes) and Edges (Calls, Imports).
    *   `Function A` calls `Function B`.
    *   `File X` imports `File Y`.
* **Why it matters**: This allows for "Impact Analysis". If you change `User.py`, the Graph can instantly light up every API endpoint that depends on it. This is the foundation for the "Passive Hygiene Monitor" (Zombie Code Detector) we designed.

---

## How to Revive Them?
1.  **Phase 4 (The Agent)**: Enable [proactive_service.py](../backend/src/side/services/proactive_service.py) in a background thread.
2.  **Phase 5 (The Brain)**: Re-implement [GraphKernel](../backend/src/side/intel/analyzers/polyglot.py) using a modern graph DB (like SQLite with recursive queries) or a dedicated graph library, connected to the `FileWatcher`.

---
*Reference: [ORGANISM_ARCHITECTURE.md](./ORGANISM_ARCHITECTURE.md)*
