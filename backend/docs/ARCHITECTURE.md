# Sidelith Architecture

> **"AI Memory for your Codebase"** - A local-first, privacy-focused context injection engine.

## System Overview

```mermaid
graph TB
    subgraph IDE["🖥️ IDE (Cursor/VS Code)"]
        User[Developer]
        Chat[AI Chat]
    end
    
    subgraph MCP["📡 MCP Server"]
        Router[Tool Router]
        Tools[Dynamic Toolset]
    end
    
    subgraph Intel["🧠 Intelligence Layer"]
        CS[ContextService]
        LB[LogMonitor]
        SA[SystemAwareness]
    end
    
    subgraph Storage["💾 Local Storage"]
        DB[(SQLite / WAL)]
        MM[Mmap Pattern Store]
    end
    
    subgraph Dashboard["🌐 Web Dashboard"]
        API[/api/metrics]
        UI[Dashboard UI]
    end
    
    User -->|"ask code questions"| Chat
    Chat -->|"MCP protocol"| Router
    Router --> Tools
    Tools --> CS
    CS --> DB
    
    LB -->|"log events"| DB
    SA -->|"health alerts"| DB
    
    API -->|"fetch stats"| DB
    UI -->|"display"| API
```

## Layered Architecture

### Layer 1: Ingestion & Monitoring
- **FileWatcher**: Real-time detection of filesystem changes.
- **LogMonitor**: Scavenges system and application logs for error context.
- **TreeIndexer**: High-precision AST parsing using Tree-sitter to build the project structural map.

### Layer 2: Intelligence & Orchestration
- **ContextService**: The central hub for gathering and injecting project context.
- **PromptBuilder**: Constructively gathers code fragments and rules to build optimized LLM prompts.
- **SystemAwareness**: Monitors local system health and environment state.
- **PatternAnalyzer**: Identifies recurring code patterns and violations.

### Layer 3: Delivery (Adapters)
- **MCP Server**: Provides a standardized interface for AI tools via the Model Context Protocol.
- **CLI**: Standard commands (`side connect`, `side audit`) for developer interaction.
- **Web UI**: Provides visual insights into project stats and system health.

## Core Components

### ContextService (`intel/context_service.py`)
- **Purpose**: Core orchestrator for all intelligence operations.
- **Responsibility**: Delegating to specialized handlers for indexing, history analysis, and context gathering.

### TreeIndexer (`intel/tree_indexer.py`)
- **Purpose**: Fast, incremental indexing of code structure.
- **Responsibility**: Extracting classes, functions, and technological "signals" without full file parsing.

### CodeMonitor (`intel/code_monitor.py`)
- **Purpose**: Watches for structural changes and updates the index.
- **Responsibility**: Ensuring the "Project DNA" remains in sync with the live code.

### SchemaStore (`storage/modules/schema.py`)
- **Purpose**: Persistence layer for structural code maps (Ontology).
- **Responsibility**: Storing and retrieving code entities and their relationships.

## Security & Privacy
- **Local-First**: All indexing and context storage remains in the `.side/` directory.
- **Zero-Trust**: No code is transmitted to external servers for indexing.
- **Privacy Masking**: Pattern Sync anonymizes coding patterns before any optional cloud sharing.

## File Structure

```
side/
├── src/side/
│   ├── intel/              # Intelligence modules
│   │   ├── context_service.py
│   │   ├── tree_indexer.py
│   │   ├── system_awareness.py
│   │   └── ...
│   ├── storage/            # Persistence modules
│   │   ├── modules/
│   │   │   ├── strategy.py
│   │   │   ├── audit.py
│   │   │   └── schema.py
│   │   └── simple_db.py
│   ├── services/           # Background services
│   │   ├── file_watcher.py
│   │   └── ...
│   ├── server.py           # MCP Server Entry
│   └── cli.py              # CLI Entry
```
