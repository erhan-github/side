# Sidelith Backend

The **Intelligence Kernel** of the Sidelith system.
This module handles the heavy lifting of:
1.  **Code Analysis** (Parsing, AST traversals).
2.  **Vectorization** (Embedding generation via `EmbeddingService`).
3.  **Storage** (SQLite management via `simple_db`).
4.  **Forensics** (Security & Quality Audits).

## Directory Structure
```
src/side/
├── ai/                 # LLM & Vector Logic (The Brain)
├── storage/            # SQLite Persistence (The Memory)
├── forensic_audit/     # Security Probes (The Immune System)
├── services/           # Business Logic Layer
└── utils/              # Hardened Utilities
```

## Key Capabilities
*   **Unit of Work**: The `StrategicUnit` (SU) - Atomic currency of compute.
*   **Memory Model**: XML-based Context Injection (`<SovereignContext>`).
*   **Indexing**: Real-time file watching + Hybrid indexing.

## Development
```bash
# Run the Daemon
python3 -m side.watcher_daemon

# Run an Audit
side audit --deep
```
