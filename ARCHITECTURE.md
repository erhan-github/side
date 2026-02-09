# Sidelith Technical Architecture

This document provides a deep dive into the internal components and engineering principles of Sidelith.

---

## Core Components

### 1. Auto-Intelligence Orchestrator
*   **Component**: `AutoIntelligence` (`backend/src/side/intel/auto_intelligence.py`)
*   **Function**: The central brain that orchestrates context retrieval. It dynamically selects the most relevant "Context Slice" based on the user's current task.
*   **Sub-Systems**:
    *   **DNAHandler**: Extracts structural truth (classes, functions) from code.
    *   **ContextHandler**: Constructs high-fidelity prompts for the LLM.
    *   **JanitorHandler**: Manages stale context.

### 2. Distributed Fractal Indexing
*   **Component**: `FractalIndexer` (`backend/src/side/intel/fractal_indexer.py`)
*   **Algorithm**: Split-Contiguous Mmap storage for high-frequency pattern matching.
*   **Data Structure**: **Merkle-Validated** fractal usage of `local.json` files in every directory.
*   **Throughput**: Optimized for ARM NEON (Apple Silicon) via SIMD instructions.
*   **Mechanism**: Only changed files are re-indexed, ensuring the tree remains accurate with O(1) incremental updates.

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

| Capability | Engineering Stack | Operational Impact |
|:-----------|:------------------|:-------------------|
| **Policy-as-Code** | `PulseEngine` (Regex/AST) | Blocks architectural drift (e.g., "No API Keys in Commit"). |
| **AST Shadowing** | Tree-sitter AST Analysis | Indexes the meaning of code (Classes, Functions), not just text. |
| **Memory Persistence** | `AutoIntelligence` + `data.db` | The system remembers architectural decisions across sessions. |
| **Forensic Context** | `AuditStore` (SQLite) | Reconstructs the reasoning chain to prevent context regression. |
| **Unified Bootstrapping** | `curl | sh` pipeline | Achieves a ready state in <15s, bridging local IDEs. |
| **Performance Substrate** | Adaptive Throttling | Minimal CPU impact during deep-AST scanning. |
| **Log Scavenging** | `log_scavenger.py` | Correlates logs from various stacks to reconstruct failure states. |

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
