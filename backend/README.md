# Side

> **The Strategic Partner that thinks for you.**

[![Tests](https://img.shields.io/badge/tests-65%20passing-brightgreen)]() [![Strategic IQ](https://img.shields.io/badge/Strategic%20IQ-127%2F160-blue)]() [![License](https://img.shields.io/badge/license-MIT-green)]()

## What is Side?

**Side is a strategic intelligence layer for your IDE.** It runs a virtual **Boardroom** of AI experts that review every line of code — security architects, performance leads, UX specialists.

Unlike standard coding assistants (Cursor, Copilot) which only care about the *current tab*, Side cares about the *project lifecycle*.

---

## The Boardroom

When you run `side audit`, you're convening a board of experts:

| Expert | Role | Tier |
|--------|------|------|
| 🛡️ **Sentinel** | Security Architect | DEEP |
| 👨‍💻 **The Architect** | Code Quality Lead | DEEP |
| ⚡ **The Scaler** | Performance Lead | DEEP |
| 👷 **Builder** | Senior Engineer | DEEP |
| 🔧 **The Operator** | SRE / DevOps | DEEP |
| 🔍 **Secret Scanner** | Credential Detector | FAST |
| 📋 **GitIgnore Guard** | Config Checker | FAST |
| 👥 **Focus Group** | Virtual Users | DEEP |

**FAST tier**: Instant, regex-based (free)  
**DEEP tier**: AI-powered analysis (uses your LLM key)

---

## Why Side?

| | Side | Cursor | Copilot | ChatGPT |
|---|---|---|---|---|
| **Memory** | **Project Lifecycle** | Session Window | Session Window | None |
| **Virtual Boardroom** | ✓ 8 Experts | ✗ | ✗ | ✗ |
| **Detects technical debt** | ✓ Real-time | ✗ | ✗ | ✗ |
| **Virtual user testing** | ✓ | ✗ | ✗ | ✗ |
| **Quantified health score** | ✓ 0-100% | ✗ | ✗ | ✗ |
| **Local-first privacy** | ✓ | ⚠ | ⚠ | ✗ |
| **IDE-native** | ✓ MCP | ✓ | ✓ | ✗ |

**Other tools write code. We make sure you're building the right thing.**

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/erhan-github/side.git
cd side/backend
uv pip install -e .
```

### 2. Add Your LLM Key (any provider)

```bash
# Pick one:
export GROQ_API_KEY="your-key"       # Groq (Llama 3)
export OPENAI_API_KEY="your-key"     # OpenAI (GPT-4)
export ANTHROPIC_API_KEY="your-key"  # Anthropic (Claude)
```

### 3. Add to Cursor

```json
{
  "mcpServers": {
    "side": {
      "command": "python",
      "args": ["-m", "side.server"]
    }
  }
}
```

### 4. Run The Boardroom

```bash
side audit
```

Output:
```
🏛️ The Boardroom is reviewing /your/project...
📁 Found 127 files.

⚡ FAST Tier (instant checks)...
   └─ Secret Scanner
   └─ GitIgnore Guard

🔬 DEEP Tier (AI review)...
   └─ Sentinel
   └─ The Scaler

📝 Generating report...
Score: 87%
```

---

## Core Tools

| Tool | Command | Purpose |
|------|---------|---------|
| **The Boardroom** | `side audit` | Run all experts on your codebase |
| **Strategic Verdict** | `side decide "question"` | Get decisive architectural answers |
| **Virtual User Lab** | `side simulate "feature"` | Test on virtual personas |
| **Mission Control** | `side plan "goal"` | OKR-style goal tracking |
| **Progress Sync** | `side check "goal"` | Mark goals as complete |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Your IDE (Cursor, Windsurf, VS Code)           │
└─────────────────────────────────────────────────┘
                      ↓ MCP Protocol
┌─────────────────────────────────────────────────┐
│  Side MCP Server (Local)                        │
│  ├── The Boardroom (8 Virtual Experts)          │
│  │   ├── FAST Tier (Regex, instant)             │
│  │   └── DEEP Tier (LLM, targeted)              │
│  ├── Strategic Verdict Engine                   │
│  └── Virtual User Simulator                     │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Local SQLite Database                          │
│  └── Decisions, Plans, Findings                 │
└─────────────────────────────────────────────────┘
```

**Key Principles:**
- **Local-first**: Your code never leaves your machine
- **Multi-Provider**: Use any LLM (Groq, OpenAI, Claude)
- **Tiered**: FAST checks free, DEEP checks use your key
- **Instant**: Sub-100ms for FAST tier

---

## Pricing

| Tier | Price | What You Get |
|------|-------|--------------|
| **Free** | $0 | FAST tier + DEEP (bring your own key) |
| **Pro** | $20/mo | DEEP tier via Side Cloud (no key needed) |

---

## Privacy: One Simple Rule

> **We never see, read, or store your code.**

### How It Works

```
Your Machine          Side API           LLM
┌──────────┐         ┌──────────┐       ┌──────────┐
│ Side MCP │────────▶│ Stateless│──────▶│ Analysis │
│          │◀────────│ Proxy    │◀──────│          │
└──────────┘         └──────────┘       └──────────┘
    │                     │
    │                     │
 Reads your           Zero retention.
 local files.         We don't care
                      who you are.
```

| What Happens | Privacy |
|--------------|---------|
| Code snippets pass through Side API | ✅ Stateless, zero retention |
| LLM analyzes the code | ✅ No human ever sees it |
| Results returned to you | ✅ Nothing stored |
| Your identity | ✅ We only know your email for billing |

### What We Store

| Data | Stored? |
|------|---------|
| Your code | ❌ Never |
| File paths | ❌ Never |
| Git history | ❌ Never |
| Secrets/credentials | ❌ Never |
| Your email | ✅ For account |
| Token usage | ✅ For billing |

**That's it.** We're an intelligence layer, not a surveillance layer.

---

## License
MIT

---
*Side - The Strategic Partner that thinks for you.*
