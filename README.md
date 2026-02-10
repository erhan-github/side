# Sidelith

> Give your AI coding assistants memory of your codebase.

Sidelith indexes your project structure so AI tools (Cursor, VS Code, Claude) understand your architecture, not just generic patterns.

[![Install](https://img.shields.io/badge/install-curl-blue)](https://sidelith.com/install)
[![Docs](https://img.shields.io/badge/docs-sidelith.com-green)](https://sidelith.com/docs)

---

## The Problem

AI coding assistants don't remember your project structure. They suggest:
- Generic code that breaks your patterns
- File locations that don't match your architecture  
- Solutions that ignore your conventions

## The Solution

Sidelith indexes your codebase locally and injects context into AI tools via the Model Context Protocol (MCP). Your AI assistant now "sees" your actual project structure.

---

## Quick Start

Install and connect to your project:

```bash
curl -sL sidelith.com/install | sh
cd your-project
side connect
```

Test it in Cursor or VS Code:
```
Ask your AI: "What's the structure of this project?"
```

If it describes your actual folders, Sidelith is working.

[Full documentation →](https://sidelith.com/docs)

---

## How It Works

1. **Indexes your code** using Tree-sitter AST parsing
2. **Stores locally** in `.side/` directory (never leaves your machine)
3. **Injects context** into AI tools via MCP when you code

### What Gets Indexed

✅ Project structure (folders, files)  
✅ Code patterns (classes, functions, modules)  
✅ Architecture decisions (from `.side/rules/`)  

---

## CLI Reference

| Command | Description |
|---------|-------------|
| `side connect` | Connect current project to AI tools |
| `side index` | Re-index project structure |
| `side watch` | Auto-reindex on file changes |
| `side audit` | View rule violations |
| `side profile` | Check account status |

[Full CLI documentation →](https://sidelith.com/docs/cli)

---

## Features

### Local-First
Your code never leaves your machine. Index stored in `.side/` directory.

### Fast Indexing
Optimized for large codebases with incremental updates.

### Rule Enforcement
Block secrets in commits and enforce architectural patterns via `.side/rules/`.

---

## Configuration

Create `.side/config.yaml` in your project:

```yaml
policy:
  enforce_clean_commits: true
  secrets:
    block: true
    patterns:
      - "sk-[a-zA-Z0-9]{48}"  # Block API keys

ignored:
  - "node_modules"
  - ".git"
  - "dist"
```

---

## Architecture

Sidelith consists of:

- **Core Indexer** - Parses code structure using Tree-sitter
- **Context Service** - Manages context injection via MCP
- **Rule Engine** - Enforces security and architecture rules
- **Audit Store** - Tracks usage and operations

Built with: Python, SQLite, Tree-sitter, MCP

[Read full architecture →](./ARCHITECTURE.md)

---

## Pricing

| Tier | Price | Audience |
|------|-------|----------|
| Hobby | Free | Single developer |
| Pro | $12/mo | Individual creators |
| Team | $25/user | Teams & Orgs |
| Enterprise | Custom | On-premise |

[View pricing details →](https://sidelith.com/pricing)

---

## Requirements

- macOS, Linux, or WSL2
- Cursor, VS Code, or Claude Desktop
- Python 3.8+

---

## License

[View license](./LICENSE)

---

**Sidelith** - AI memory for your codebase.
