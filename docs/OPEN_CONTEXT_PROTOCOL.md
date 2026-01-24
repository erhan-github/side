# The Open Context Protocol (OCP): 2030 Vision

> **The Theory**: Code without context is just text. To build the "Self-Aware Commit," we must standardize how Intent is embedded in Source.

## 1. The Problem: "Context Loss"
Today, when a developer writes code, 90% of the "Why" is lost.
- **Git Commit**: "Fix auth bug" (Weak)
- **PR Description**: "Updated middleware" (Transient)
- **Slack Message**: "We need to ship this for the IPO" (Lost forever)

## 2. The Solution: "Machine-Readable Intent"
We propose a standard taxonomy of **Strategic Annotations** that `Side` (and future AI agents) can parsers.

### The Taxonomy
| Annotation | Example | AI Interpretation |
| :--- | :--- | :--- |
| **@Strategic** | `// @Strategic(Goal="IPO_Readiness"): Enforce strict audit logging` | "This code is critical. Block any changes that weaken logging." |
| **@Vision** | `// @Vision: Eventually, this should support multi-tenancy` | "When refactoring, suggest multi-tenant patterns." |
| **@Zombie** | `// @Zombie: Deprecated in v2.0, kill after 2026-06` | "If today > 2026-06, auto-suggest deletion." |
| **@Debt** | `// @Debt(Risk="High"): This is an N+1 query` | "Flag this in the Monolith as a 'High Risk' item." |
| **@Moat** | `// @Moat: Proprietary algo - do not outsource` | "If user tries to use Copilot here, warn them about IP leak." |

## 3. Integration with Side Moats
How this integrates with our existing Unified Architecture:

1.  **Forensics (The Scanner)**:
    *   The `Side.cli audit` tool scans for these `@Tags`.
    *   It builds a "Strategic Map" of the codebase, not just a dependency graph.

2.  **Monolith (The Visualization)**:
    *   The Dashboard renders a "Strategic Alignment" score.
    *   "You have 12 files marked `@Strategic` but 3 of them contain `@Debt`." -> **Conflict Alert**.

3.  **Memory (The History)**:
    *   `IntelligenceStore` persists these tags over time.
    *   We can replay the "Strategic Evolution" of a file.

4.  **MCP (The Bridge)**:
    *   We publish `side-mcp-server` that exposes these tags to Cursor/Windsurf.
    *   When the user opens a file, Cursor says: *"Warning: You are editing a `@Moat` file. Be careful."*

## 4. The Industry Standard (2030)
We don't just build this for Side. We publish the **OCP Spec**.
*   **Repo**: `open-context-protocol`
*   **Goal**: Make `@Strategic` as standard as `TODO`.

## 5. Execution: The "Side Context" Plugin
*   **Phase 1**: Support parsing these tags in `ForensicEngine`.
*   **Phase 2**: Create a VS Code extension that highlights them (Gold for Strategic, Red for Debt).
*   **Phase 3**: Release the MCP Server to feed this data to Claude/GPT-5.

---
**Why this wins**: It turns "Comments" from passive text into **Active Guardrails**.
