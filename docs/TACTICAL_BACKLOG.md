# Tactical Backlog: Pending Strategic Actions

This document tracks granular tactical tasks derived from previous strategic synthesis sessions (Jan 2026). These are **High Priority** implementation details required to fulfill the [MASTER_ROADMAP.md](./MASTER_ROADMAP.md).

## 🧩 1. Unified Architecture & Orchestration
- [ ] **Finalize Diagram**: Complete the high-fidelity SVG/Mermaid diagram for the unified engine.
- [ ] **Runner Unification**: Complete the full refactor of `ForensicEngine` to delegate 100% to `ForensicAuditRunner`.
- [ ] **Finding ID Stabilization**: Implement the new hashing logic (`project_id:check_id:file:line`) across all probes.
- [ ] **Dynamic Strategy Calibration**: Connect `InstrumentationEngine` output directly to the `Strategist` prompt for "Coach/Partner" mode switching.
- [ ] **AST Training (Level 2)**: Enhance language analyzers to use AST context for object-type verification (N+1 precision).
- [ ] **Regression Training (Level 3)**: Establish a permanent "Training Set" of false positives in `test_probes.py`.

## 🧠 2. The Context Resurrect Protocol (Memory)
- [ ] **XML Schema Definition**: Finalize the `context_resume.xml` format for maximum token efficiency.
- [ ] **`side remember` CLI**: Implement the command and clipboard integration.
- [ ] **Strategic Tag Miner**: Add logic to scan for `// @Strategic` tags and inject them into the memory resume.
- [ ] **Time Machine Implementation**: Build the SQLite delta engine to track "Strategic Velocity" over time.
- [ ] **Supabase Sync Design**: Define the encrypted push-button schema for cloud backups.

## 🤝 3. Feedback-Driven & Autonomous IQ
- [ ] **Event Tracker**: Build the implicit signal ledger (Track Accepted/Ignored findings).
- [ ] **Adaptive Weights**: Implement the mathematical recalibration of `DIMENSION_WEIGHTS` based on focus.
- [ ] **Sandbox Beta**: Deploy the first autonomous remediation loop for low-risk formatting drift.
- [ ] **PR Rationalizer**: Build the automation for generating PR decision logs.

## 🛡️ 4. Infrastructure & Security
- [ ] **Managed Pool Scaling**: Add multi-key rotation and auto-banning to the managed proxy.
- [ ] **Regression Velocity**: Implement the "He-Fixed-This-Before" detection to flag habit cycles.

---
*Reference: [ORGANISM_ARCHITECTURE.md](./ORGANISM_ARCHITECTURE.md) | [MASTER_ROADMAP.md](./MASTER_ROADMAP.md)*
