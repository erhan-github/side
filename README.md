# Side: The Sovereign AI Mesh 🥥

> **Status:** Arugam Bay Stable (v1.0)  
> **Architecture:** Local-First / Sovereign Mesh  
> **Philosophy:** Relentless Simplicity

**Side** is a sovereign AI engineer that lives in your codebase. It doesn't just autocomplete; it *understands* context, tracks intent, and helps you maintain strategic clarity.

It runs locally on your machine. **No cloud required.**

---

## 🚀 Quick Start

### 1. Install Credentials
Side is purely local. Usage correlates to your OS user.

```bash
# Clone the repo
git clone https://github.com/erhan-github/side.git
cd side

# Install dependencies (Lightweight)
pip install -r requirements.txt
```

### 2. Ignite the Kernel
Start the Universal Kernel (API + Brain).

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend/src
python backend/src/side/server.py
```

### 3. Connect
- **API Docs:** `http://localhost:8000/docs`
- **Dashboard:** `http://localhost:3000` (Coming soon via UI Team)
- **WebSocket:** `ws://localhost:8000/ws`

---

## 🏛️ Architecture: The Mesh

We recently completed a massive refactor ("The Monolith Purge") to strip away complexity.

*   **Universal Kernel (`server.py`)**: The single entry point. Serves API and MCP.
*   **Sovereign Ledger (`simple_db.py`)**: A transactional SQLite engine that handles memory, caching, and audit logs. 
*   **The Watcher (`watcher_daemon.py`)**: An event clock that monitors your filesystem for "Intent Drift".

👉 **Read the Full Docs:**
*   [Unified Architecture](docs/architecture/UNIFIED_ARCHITECTURE.md) - How it works.
*   [The Arugam Bay Verdict](docs/ARUGAM_BAY_FINAL_VERDICT.md) - Why it works.
*   [Frontend Handover](docs/FRONTEND_HANDOVER.md) - How to build on it.

---

## 📂 Project Structure

```
side/
├── backend/
│   └── src/side/
│       ├── server.py        # The Brain (FastAPI)
│       ├── storage/         # The Memory (SQLite)
│       └── tools/           # The Hands (MCP Tools)
├── docs/                    # The Library
└── web/                     # The Face (Next.js - In Progress)
```

---

## 🛡️ Privacy & Sovereignty

Side follows the **"Local-First"** doctrine.
*   Your code never leaves your machine unless you explicitly enable Cloud Sync.
*   All intelligence data is stored in `~/.side/local.db`.
*   You own your data. You can purge it anytime.

> **Note:** The `side sync` command currently simulates a connection to the 'Strategic Mesh' for demonstration purposes. No actual data is transmitted.

---

*Built with extensive caffeine and ocean breeze at Arugam Bay.* 🌊
