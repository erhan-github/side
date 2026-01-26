# Design: The Brain (Cognitive Intelligence)

> **Objective**: Define the logic for the Feedback-Driven and Self-Healing tiers of the Side Intelligence Engine.

## 1. The Signal Ledger (Implicit Learning)
The Brain does not just "read" code; it observes human behavior to tune its relevance.

### 1.1 Decision Hashing
Every suggestion in the Monolith is tracked via a `DecisionUID`.
- **Accepted Signal**: Suggestion removed + code changed within 2 hours.
- **Ignored Signal**: Suggestion persists > 7 days.
- **Explicit Signal**: User adds `// side:ignore`.

### 1.2 Dynamic Weighting
The Brain maintains a `dimension_profile` for each project.
- **Logic**: if `accepted_count(dimension:Security)` > `accepted_count(dimension:Perf)`, increase `weight(Security)` by 0.1.
- **Outcome**: The engine prioritizes what the developer actually cares about, reducing "Linter Fatigue."

## 2. The Remediation Loop (The Hands)
The Brain's ability to act autonomously without breaking the build.

### 2.1 The "Safe-to-Execute" Filter
1. **Detection**: `ForensicEngine` identifies a violation.
2. **Strategy Check**: `Strategist` verifies if fixing the violation aligns with active `Strategic Plans`.
3. **Drafting**: Agent generates a remediation diff + a corresponding unit test.
4. **Validation**: The system runs the test in a ephemeral `side-sandbox` container.
5. **PR Generation**: Only if tests pass, a PR is opened with the label `side:autonomous-fix`.

## 3. Recursive Correction
If `Validation` fails, the Brain enters a recursion loop:
- **Input**: CI Error Log + Original Diff.
- **Attempt**: Max 3 retries to self-correct the fix.
- **Failure**: If still broken, log as a `Cognitive Gap` for human review.

---
*Reference: [ORGANISM_ARCHITECTURE.md](./ORGANISM_ARCHITECTURE.md) | [INTELLIGENCE_ROADMAP.md](./strategy/INTELLIGENCE_ROADMAP.md)*
