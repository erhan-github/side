# 🪦 Retired Architectures & Graveyard Manifest

**"Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away."**

This document records the architectural components that were audited, deprecated, and permanently deleted from Sidelith Prime to achieve our **1.5ms Latency** and **100% Transparency** goals.

---

## 1. The Strategic Engine (`strategic_engine.py`)
**Status**: **DELETED**
**What it was**: A complex, heuristic Python class trying to be an "AI Co-pilot" with concepts like `ConfidenceLevel`, `DecisionType`, and heuristic "Logic Gates".
**Why we killed it**: 
-   **Too Slow**: "Thinking" takes time.
-   **Too Fuzzy**: Heuristics are hard to debug.
-   **Replacement**: The **Pulse Engine** (Regex/Pattern Matching). We moved "Intelligence" to the **Cloud** (Precedents) and kept Local simple.

## 2. The Anchor Manager (`anchor_manager.py`)
**Status**: **DELETED**
**What it was**: A local script to programmatically edit the `.side/sovereign.json` file.
**Why we killed it**: 
-   **Risk**: Local scripts hacking the "Constitution" is dangerous.
-   **Replacement**: `side sync`. The Anchor is managed via the **Cloud Protocol** and downloaded as a read-only artifact.

## 3. Legacy Instrumentation (`instrumentation/`, `telemetry.py`)
**Status**: **DELETED**
**What it was**: Heavy SQLite-based logging of every user action and "Article Scoring".
**Why we killed it**: 
-   **Privacy Risk**: Users hate local spyware.
-   **Disk I/O**: Constant SQLite writes hurt IDE performance.
-   **Replacement**: **Stateless CLI**. We only capture "Decision Traces" when explicitly asked (`side fix`).

## 4. The Monolith (`local.db`, `MONOLITH.md`)
**Status**: **DELETED**
**What it was**: A single, massive state file trying to track the entire project history.
**Why we killed it**: 
-   **Bottleneck**: One file cannot scale to a Monorepo.
-   **Replacement**: **Distributed Rules** (`.side/rules/*.json`).

---

**Architecture Verdict**:
We have pivoted from a "Smart, Heavy Observer" to a "Fast, Dumb Forensic Engine". The smarts are in the Cloud; the speed is on the Metal.
