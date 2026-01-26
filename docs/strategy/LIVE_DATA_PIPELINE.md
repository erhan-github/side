# Sidelith Strategic Intelligence Pipeline 🏛️

The Monolith and the MCP Bridge form a **High-Fidelity Evidence Pipeline**. Sidelith prioritizes **Ground Truth** over generic AI heuristics to maintain its role as the **System of Record**.

## 1. The Fidelity Tiers (Deterministic Evidence)
We only report what we can logically prove via AST and Forensic Probes.

| Tier | Name | Source | Output |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **FORENSIC EVIDENCE** | `side audit` (AST/RegEx Probes) | **Evidence Cards**. Shows exact logic violations (e.g. Circular Deadlocks). |
| **Tier 2** | **STRATEGIC INFERENCE** | LLM + Sovereign Context Graph | **Advisory Proactive Insights**. Custom warnings based on past architectural decisions. |

## 2. The "No-Speculation" Policy
Sidelith operates on a **Trust-First** methodology. If no forensic evidence exists, the system remains silent. This ensures that every alert rendered via the **MCP Bridge** is actionable and derived from ground truth.

## 3. The Validated Data Flow
1. **Collector**: The [ForensicAuditRunner](../backend/src/side/forensic_audit/runner.py) scans files locally via tree-sitter.
2. **Persistence**: Every finding is hashed and stored in the **Sovereign Registry** (SQLite).
3. **Bridge**: The **mcp_server.py** exposes these results to AI Agents (Cursor/Windsurf).
4. **Visual Proof**: Verified findings are rendered as high-contrast **Evidence Cards** in the developer interface.

## 4. Constraint Transparency
- **Fidelity Guarantee**: We provide the "Why" (Evidence) alongside the "What" (Finding).
- **History Trail**: Every finding in the Monolith is linked to a persistent structural ID, allowing for zero-hallucination context retrieval.

---
*Reference: [ORGANISM_ARCHITECTURE.md](../ORGANISM_ARCHITECTURE.md)*
