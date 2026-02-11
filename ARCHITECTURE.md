# Sidelith Technical Architecture

This document provides a deep dive into the internal components and engineering principles of Sidelith.

---

## Core Components

*   **Component**: `ContextService` (`backend/src/side/intel/context_service.py`)
*   **Function**: The central service that orchestrates context retrieval. It dynamically selects the most relevant "Context Snapshot" based on the user's current task.
*   **Sub-Systems**:
    *   **StructureParser**: Extracts classes and functions from code.
    *   **PromptBuilder**: Constructs clear prompts for the LLM.
    *   **ContextJanitor**: Manages stale or irrelevant context.

### 2. Code Indexing
*   **Component**: `TreeIndexer` (`backend/src/side/intel/tree_indexer.py`)
*   **Algorithm**: Incremental Tree-sitter parsing for high-frequency pattern matching.
*   **Data Structure**: **Checksum-validated** structure using `local.json` files in every directory.
*   **Throughput**: Optimized for Apple Silicon (ARM NEON) via SIMD instructions.
*   **Mechanism**: Only changed files are re-indexed, ensuring the index remains accurate with O(1) incremental updates.

### 3. Verification Engine
*   **Component**: `RuleEngine` (`backend/src/side/pulse.py`)
*   **Implementation**: Pre-compiled regex and AST-based rule evaluation.
*   **Performance**: Low-latency execution optimized for file save events.
*   **Function**: Intercepts code modifications to block secrets (API keys) and enforce architectural patterns.
*   **Configuration**: Reads rules from `.side/rules/`.

### 4. Activity Ledger Store
*   **Component**: `LedgerStore` (`backend/src/side/storage/modules/audit.py`)
*   **Storage**: SQLite (`data.db`).
*   **Schema**:
    *   `audits`: A log of every rule violation and AI interaction.
*   **Capabilities**: Allows for history tracking by reconstructing the exact context state that led to a specific decision.

### 5. Reasoning Logs
*   **Component**: `SessionAnalyzer` (`backend/src/side/intel/session_analyzer.py`)
*   **Function**: Manages a log for every verified fix.
*   **Integrity**: Each event node is linked to its parent, ensuring the history of decisions is preserved.

---

## Data Topology (Runtime Artifacts)

Sidelith uses a specific set of runtime files to manage state.

| Artifact | File Type | Purpose | Source |
|:---------|:----------|:--------|:-------|
| **Goal Tracker** | `data.db` (SQLite) | Relational store for user goals, audits, and facts. | `backend/src/side/config.py` |
| **Index Cache** | `local.json` | Directory-level semantic index & checksums. | `backend/src/side/intel/tree_indexer.py` |
| **Project Anchor** | `project.json` | Identity anchor for project connectivity. | `backend/src/side/pulse.py` |

---

## System Capabilities Matrix

| Capability | Engineering Stack | Operational Impact |
|:-----------|:------------------|:-------------------|
| **Policy-as-Code** | `RuleEngine` (Regex/AST) | Blocks architectural drift (e.g., "No API Keys in Commit"). |
| **AST Analysis** | Tree-sitter AST Analysis | Indexes the meaning of code (Classes, Functions), not just text. |
| **Context Persistence** | `ContextService` + `data.db` | The system remembers architectural decisions across sessions. |
| **History Tracking** | `LedgerStore` (SQLite) | Reconstructs the reasoning chain to prevent context regression. |
| **Ready-to-Use** | `curl | sh` pipeline | Achieves a ready state in <15s, bridging local IDEs. |
| **Performance** | Adaptive Throttling | Minimal CPU impact during background scanning. |
| **Log Management** | `log_scavenger.py` | Correlates logs from various stacks to reconstruct failure states. |

---

## Technical Specifications

| Metric | Specification |
|:-------|:--------------|
| **Search Architecture** | SIMD-Accelerated Mmap |
| **Context Latency** | Optimized for Real-Time |
| **CPU Overhead** | Adaptive throttling (Idle/Active states) |
| **Storage Overhead** | Minimal per-project footprints |
| **Security** | AES-256 (Data at Rest) |
| **Transport** | TLS 1.3 + HMAC Signatures |
