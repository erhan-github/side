# Sidelith: Local-First Context Middleware

> **SIMD-Accelerated Semantic Search. Zero-Leak Isolation. Deterministic Governance.**

Sidelith is a Middleware Context Engine that sits between the developer environment and AI agents (Cursor, VS Code, CLI). It functions as a **Stateful Context Provider**, responsible for:

1.  **Context Injection**: Deriving project-specific context (stack, patterns, architecture) for LLM prompts.
2.  **State Persistence**: Maintaining a local vector of user intent and architectural decisions across sessions.
3.  **Governance**: Enforcing architectural rules and secret detection via a local rule engine.
4.  **Distributed Sync**: Propagating non-sensitive architectural patterns across local repositories.

---

## Technical Architecture

### 1. Auto-Intelligence Orchestrator
*   **Component**: `AutoIntelligence` (`backend/src/side/intel/auto_intelligence.py`)
*   **Function**: The central brain that orchestrates context retrieval. It dynamically selects the most relevant "Context Slice" based on the user's current task.
*   **Sub-Systems**:
    *   **DNAHandler**: Extracts structural truth (classes, functions) from code.
    *   **ContextHandler**: Constructs high-fidelity prompts for the LLM.
    *   **JanitorHandler**: Manages neural decay and prunes stale context.

### 2. Distributed Fractal Indexing
*   **Component**: `FractalIndexer` (`backend/src/side/intel/fractal_indexer.py`)
*   **Algorithm**: Split-Contiguous Mmap storage for high-frequency pattern matching.
*   **Data Structure**: **Merkle-Validated** fractal usage of `local.json` files in every directory.
*   **Throughput**: Optimized for ARM NEON (Apple Silicon) via SIMD instructions.
*   **Mechanism**: Only changed files are re-indexed, ensuring the tree remains clinically accurate with O(1) incremental updates.

### 3. Latency-Optimized Rule Engine
*   **Component**: `PulseEngine` (`backend/src/side/pulse.py`)
*   **Implementation**: Pre-compiled regex and AST-based rule evaluation.
*   **Performance**: Low-latency execution optimized for file save events.
*   **Function**: Intercepts code modifications to block secrets (API keys) and enforce architectural invariants.
*   **Configuration**: Reads deterministic rules from `.side/rules/`.

### 4. Forensic Audit Store
*   **Component**: `AuditStore` (`backend/src/side/storage/modules/audit.py`)
*   **Storage**: SQLite (`data.db`).
*   **Schema**:
    *   `audits`: A tamper-proof log of every rule violation and AI interaction.
*   **Capabilities**: Allows for "Time-Travel Debugging" by reconstructing the exact context state that led to a specific decision.

### 5. Cryptographic Reasoning Chain
*   **Component**: `ReasoningTimeline` (`backend/src/side/intel/reasoning_timeline.py`)
*   **Function**: Manages an immutable audit trail for every verified fix.
*   **Integrity**: Each event node is cryptographically linked to its parent, ensuring the "Chain of Reasoning" cannot be tampered with.

---

## Data Topology (Runtime Artifacts)

Sidelith uses a specific set of runtime files to manage state.

| Artifact | File Type | Purpose | Source |
|:---------|:----------|:--------|:-------|
| **Intent Store** | `data.db` (SQLite) | Relational store for user intent, audits, and strategic facts. | `backend/src/side/config.py` |
| **Fractal Cache** | `local.json` | Directory-level semantic index & Merkle checksums. | `backend/src/side/intel/fractal_indexer.py` |
| **Project Anchor** | `project.json` | Verification anchor for project identity and integrity. | `backend/src/side/pulse.py` |

---

## System Capabilities Matrix

The Sidelith architecture delivers six foundational capabilities, categorized by their technical stack and operational impact.

| Capability | Engineering Stack | Operational Impact |
|:-----------|:------------------|:-------------------|
| **Policy-as-Code Governance** | `PulseEngine` (Regex/AST) | **Blocks architectural drift** before it enters the codebase (e.g., "No API Keys in Commit"). |
| **Deep Semantic Shadowing** | Tree-sitter AST Analysis | Indexes the **meaning** of code (Classes, Functions), not just text. Enables "Concept Search" vs "Grep". |
| **Memory Persistence** | `AutoIntelligence` + `data.db` | Solves **"Context Amnesia"**. The system remembers architectural decisions across sessions. |
| **Forensic-Driven Context** | `AuditStore` (SQLite) | Reconstructs the **"Reasoning Chain"** of previous sessions to prevent context regression in new LLM prompts. |
| **Unified Bootstrapping** | `curl` | `sh` pipeline | Achieves a "Zero-to-Connected" state in <15s, dynamically identifying and bridging all local IDEs. |
| **Cryptographic Audit Chains** | `ReasoningTimeline` | Every architectural maneuver is logged into an immutable chain, ensuring 100% auditability. |
| **Performance Substrate** | Virtualized List Rendering | Allows deep-AST scanning to run with minimal CPU impact, ensuring zero degradation of developer velocity. |
| **Polyglot Log Scavenging** | `log_scavenger.py` | Correlates logs from Xcode, Docker, and Node.js to reconstruct failure states ("Crime Scene Reconstruction"). |

---

## Interface Specification

Sidelith exposes a Unified CLI for all interactions.

### Core Commands

| Command | Function | Target Subsystem |
|:--------|:---------|:-----------------|
| `side connect` | Initializes the `AutoIntelligence` link for the current project. | `cli_handlers/connect.py` |
| `side profile` | Displays the "HUD" – Identity and token usage. | `cli_handlers/auth.py` |
| `side index` | Forces a `FractalIndexer` re-index of the codebase. | `cli_handlers/intel.py` |
| `side audit` | Generates a forensic report of recent violations. (Severity filtering available). | `cli_handlers/audit.py` |
| `side watch` | Starts the real-time file watcher daemon. | `cli_handlers/intel.py` |

### Configuration (`.side/config.yaml`)

Policy configuration is declarative.

```yaml
policy:
  enforce_clean_commits: true
  max_token_budget: 1000000
  secrets:
    block: true
    patterns:
      - "sk-[a-zA-Z0-9]{48}"
ignored:
  - "node_modules"
  - ".git"
```

---

## Technical Specifications

| Metric | Specification |
|:-------|:--------------|
| **Search Architecture** | SIMD-Accelerated Mmap |
| **Context Latency** | Optimized for Real-Time |
| **CPU Overhead** | Adaptive throttling (Idle/Active states) |
| **Storage Overhead** | ~36 bytes per project (UUID) + centralized SQLite |
| **Encryption** | AES-256 (Data at Rest) |
| **Transport** | TLS 1.3 + HMAC Signatures |

---

## Deployment & Pricing

| Tier | Deployment | Audience | Features |
|:-----|:-----------|:---------|:---------|
| **Hobby** | Cloud SaaS | Individual, evaluation |
| **Pro** | Cloud SaaS | Professional developers |
| **Elite** | Cloud SaaS | Power users, small teams |
| **Enterprise** | Cloud SaaS | Teams, SSO, shared pools |
| **Airgapped** | On-Premise | Regulated industries |

---

## Disclaimer

**Sidelith is technically an "Agentic IDE Middleware."**
It is not an Editor (VS Code), nor a Model (GPT-4), nor a Hosting Provider.
It is the **Context Layer** that makes all of the above actually work for complex engineering.
