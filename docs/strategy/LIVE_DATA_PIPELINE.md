# The Side Strategic Intelligence Pipeline

The Monolith is a **multi-tier display engine** designed for high-fidelity engineering governance. It prioritizes **Active Evidence** over generic heuristics to maintain a "System of Record" trust level.

## 1. The Fidelity Tiers (Pure Evidence Model)

To ensure maximum accuracy, Side has removed all "industry-standard" generic fallbacks (formerly Tier 3). We only report what we can prove.

| Tier | Name | Source | Behavior |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **LIVE EVIDENCE** | `side audit` / [ForensicAuditRunner](../backend/src/side/forensic_audit/runner.py) | **High Fidelity**. Shows exact file paths, line numbers, and logic flaws found in your specific code via RegEx and AST. |
| **Tier 2** | **STRATEGIC INFERENCE** | [Strategist](../backend/src/side/intel/strategist.py) (LLM) | **Intelligent**. The LLM analyzes your Project Profile and Grade to generate custom "Provocations" unique to your stage. |

## 2. The "No-Fallback" Policy
Side operates on a **Trust-First** methodology. If no forensic evidence exists (e.g., before the first `side audit`), the Monolith will remain empty of findings rather than showing generic "Industry Standard" placeholders. This ensures that every alert is actionable and derived from ground truth.

## 3. How to enable "Full Fidelity"
When you start working:
1. **Collector**: The [ForensicAuditRunner](../backend/src/side/forensic_audit/runner.py) scans your files via RegEx and Deep LLM probes.
2. **Persistence**: Every finding is hashed and stored in your local `side.db` (The Nervous System).
3. **Synthesis**: The `MonolithService` pulls these hashes and renders them into the conversational "Hey Side!" prompt format for IDE-native interaction.

## 4. Constraint Transparency
- **Fidelity Guarantee**: We use `TechnicalAnalyzer` (TreeSitter) and `DeepSecurity` (Llama-3.3-70B) to ensure zero speculation.
- **Evidence Trail**: Every finding in the Monolith is linked to a structural ID in the database, allowing for a verifiable audit trail of project history.

---
*Reference: [ORGANISM_ARCHITECTURE.md](../ORGANISM_ARCHITECTURE.md) | [FORENSIC_TAXONOMY.md](../FORENSIC_TAXONOMY.md)*
