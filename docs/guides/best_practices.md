# Sidelith Best Practices: The Engineering System of Record 🏛️

> **Living Methodology**: This guide documents the optimal workflow for eliminating **Amnesia Drift** and capturing **Residual Wisdom**.

## 1. The Core Philosophy: The Architectural Steward
Sidelith is the **Engineering System of Record**. It treats your codebase as a "Logic Ledger" that requires deterministic oversight.

### The "Fidelity Sync" Standard
Your **Registry** should be the single source of truth for Intent.
- **Code is Reality**: The current implementation in the repository.
- **Registry is Intent**: The strategic context stored in the Sovereign Registry (SQLite).
- **Drift is the Enemy**: Any difference between Code and Registry is **Amnesia Drift**.

---

## 2. Validated "Forensic Wins" (Case Studies)
Actual examples where Sidelith's forensic approach solved critical issues that traditional linting and AI Agents missed.

#### Win #1: The Circular Deadlock (Validated Jan 26)
**Symptom**: Compilation/Build failures with cryptic "Cycle Detected" errors in Rust/C++.
**The Problem**: AI Agent introduced a macro expansion loop (`Macro A -> B -> A`). Valid syntax, but architectural suicide.
**Sidelith Forensics**:
1. **Forensic Scan**: Sidelith built the **Logical Topology** graph of the macros.
2. **Result**: Found the loop instantly via multi-pass analysis.
3. **The Fix**: Sidelith provided an **Evidence Card** before the developer even committed the code.

#### Win #2: The Amnesia Check
**Symptom**: Context lost during long AI Agent sessions. Agent starts using deprecated `auth_v1` logic.
**The Problem**: **Amnesia Drift**. The chat window lost the project context from 3 weeks ago.
**Sidelith Forensics**:
1. **MCP Query**: Agent queried the **Sovereign Registry** via the MCP Bridge.
2. **Context Retrieval**: Sidelith retrieved the "Strategic Decision" from Jan 12th: *"Use auth_v2 for all social logins."*
3. **Resolution**: Agent self-corrected without human intervention.

#### Win #3: The Secret Sniffer
**Symptom**: High security risk in an AI-generated PR.
**The Problem**: Agent accidentally committed a Stripe Test Key hidden in a base64 string.
**Sidelith Forensics**:
1. **Deep Probe**: Sidelith decoded the strings locally and identified high-entropy patterns.
2. **Action**: Rendered a **High-Contrast Evidence Card** in the terminal.

---

## 3. The "System of Record" Toolchain

### The MCP Bridge (Strategic Data)
Allows AI Agents (Cursor/Windsurf) to talk to the **Sovereign Registry**.
- **Usage**: Automatically provides Agents with ground truth. No more "guessing" about which database to use.

### The Evidence Card (Visual Proof)
The final rendering of a forensic finding.
- **Rule**: If Sidelith shows an Evidence Card, stop. Analyze the drift. Sync the Registry.

---

## 4. Summary of Rules
1.  **Registry First**: Log strategic tech decisions immediately.
2.  **Audit Often**: Use the Forensic Engine to check architectural alignment.
3.  **Capture Wisdom**: Every "Why" discovered in a chat should be recorded in the System of Record.
4.  **Local-First**: Trust the local probes; verify the cloud syntheses.

---
> **"We remember why you built it, so you don't have to."** 🏛️
