# CSO.ai

# sideMCP

> **The Sidecar that thinks for you.**

[![Tests](https://img.shields.io/badge/tests-65%20passing-brightgreen)]() [![Strategic IQ](https://img.shields.io/badge/Strategic%20IQ-127%2F160-blue)]() [![License](https://img.shields.io/badge/license-MIT-green)]()

## What is sideMCP?
**sideMCP is a strategic intelligence layer for your IDE.** It watches your codebase, remembers every decision you've ever made, and alerts you before you ship technical debt.

Unlike standard coding assistants (Cursor, Copilot) which only care about the *current tab*, sideMCP cares about the *project lifecycle*.

## Why sideMCP?

| | sideMCP | Cursor | Copilot | ChatGPT |
|---|---|---|---|---|
| **Memory** | **Project Lifecycle** | Session Window | Session Window | None |
| **Detects technical debt** | ✓ Real-time | ✗ | ✗ | ✗ |
| **Virtual user testing** | ✓ | ✗ | ✗ | ✗ |
| **Quantified health score** | ✓ 0-160 | ✗ | ✗ | ✗ |
| **Local-first privacy** | ✓ | ⚠ | ⚠ | ✗ |
| **IDE-native** | ✓ MCP | ✓ | ✓ | ✗ |

**Other tools write code. We make sure you're building the right thing.**

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/erhanerdogan/cso-ai.git
cd cso-ai
uv pip install -e .
```

### 2. Add to Cursor

```json
{
  "mcpServers": {
    "cso-ai": {
      "command": "python",
      "args": ["-m", "cso_ai.server"]
    }
  }
}
```

### 3. Try it

```
cso decide "PostgreSQL or MongoDB?"
```

Response:
```
┌─ 💎 STRATEGIC VERDICT ────────────────────┐
│
│  USE: PostgreSQL
│  █████████████████░░░ 87% confidence
│
│  Your data is relational. MongoDB adds
│  complexity you don't need.
│
│  ▸ Want the migration guide?
└───────────────────────────────────────────┘
```

---

## Core Tools

| Tool | Command | Purpose |
|------|---------|---------|
| **Strategic Verdict** | `cso decide "question"` | Get decisive architectural answers |
| **Strategic IQ** | `cso strategy` | Check your codebase health score |
| **Virtual User Lab** | `cso simulate "feature"` | Test on virtual personas |
| **Codebase X-Ray** | `cso run_audit` | Deep forensic code analysis |
| **Mission Control** | `cso plan "goal"` | OKR-style goal tracking |
| **Progress Sync** | `cso check "goal"` | Mark goals as complete |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Your IDE (Cursor, Windsurf, VS Code)           │
└─────────────────────────────────────────────────┘
                      ↓ MCP Protocol
┌─────────────────────────────────────────────────┐
│  CSO.ai MCP Server (Local)                      │
│  ├── Strategic Verdict Engine                   │
│  ├── Strategic IQ Calculator                    │
│  ├── Virtual User Simulator                     │
│  └── Forensic X-Ray Engine                      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Local SQLite Database                          │
│  ├── Decisions (infinite memory)                │
│  ├── Plans (OKR tracking)                       │
│  ├── Findings (forensic results)                │
│  └── Work Context (focus detection)             │
└─────────────────────────────────────────────────┘
```

**Key Principles:**
- **Local-first**: Your code never leaves your machine
- **Instant**: Sub-100ms cached responses
- **Persistent**: Decisions remembered forever
- **Proactive**: Alerts before you commit bad code

---

## Pricing

| Tier | Price | Tokens | Best for |
|------|-------|--------|----------|
| **Solo Builder** | $0/mo | 5,000 | Indie hackers, weekend projects |
| **Funded Startup** | $20/mo | 50,000 | Teams that ship fast |

**Token refills**: $20 for 50,000 tokens anytime.

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design & data flow
- [API Reference](docs/API.md) - Tool specifications
- [Contributing](docs/CONTRIBUTING.md) - Development guide

---

## License
MIT

---
*sideMCP - The Sidecar that thinks for you.*
