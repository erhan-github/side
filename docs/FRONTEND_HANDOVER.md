# 🎨 Frontend Handover Protocol: The Sovereign Mesh

**To:** UI/UX Team  
**From:** Backend Engineering (Arugam Bay Council)  
**Date:** Jan 27, 2026  
**Status:** READY FOR INTEGRATION

---

## 🚀 Quick Start

The backend is a **Universal Kernel**. It runs locally and serves a high-speed JSON API.

1.  **Start Backend:**
    ```bash
    python src/side/server.py
    ```
2.  **API Docs:**
    *   Open `http://localhost:8000/docs` (Swagger UI)
    *   Open `http://localhost:8000/redoc` (Alternative)

---

## 🔑 Authentication (The "No-Auth" Auth)

**Philosophy:** We are **Local-First**.
*   There is no "Login Screen".
*   The user *is* the OS user.
*   **API Logic:** The backend automatically identifies the user based on the machine scope.
*   **UI Logic:** Just call the API. You will get a `profile` object back. If `profile.tier` is 'free', show the upgrade button.

---

## 📡 Core Data Hooks (Mapping API -> UI)

### 1. The Dashboard (Home)
This is the "Mission Control".

| UI Component | API Endpoint | Data Needed |
| :--- | :--- | :--- |
| **Profile Card** | `GET /api/profile` | `name`, `tier`, `token_balance` |
| **Context Banner** | `GET /api/context` | `focus_area`, `current_task` |
| **Recent Activity** | `GET /api/activity` | `[Action Log]` (for Forensic Ledger) |

### 2. The Work Surface (Context Aware)
When the user is coding.

| UI Component | API Endpoint | Data Needed |
| :--- | :--- | :--- |
| **Pulse** | `WS /ws/pulse` | Real-time `status: "DRIFT" | "FLOW"` |
| **Intelligence** | `POST /api/chat` | streaming: `true` (MCP Protocol) |

### 3. Settings (Sovereignty)
Where the user controls their data.

| UI Component | API Endpoint | Data Needed |
| :--- | :--- | :--- |
| **Consents** | `GET /api/consents` | `cloud_sync`, `telemetry`, `auto_training` |
| **Data Purge** | `POST /api/purge` | **WARNING:** Red Button UI required. |

---

## 🔌 WebSocket Events (Real-Time)

We expose a single WebSocket stream for the "Living UI".

**Endpoint:** `ws://localhost:8000/ws`

**Events:**
*   `{"type": "token_update", "balance": 45}` -> Animate the coin counter.
*   `{"type": "drift_alert", "file": "..."}` -> Show a subtle toast/notification.
*   `{"type": "audit_complete", "score": 98}` -> Update the health score graph.

---

## 🎨 Design Guidelines (Backend Constraints)

1.  **Optimistic UI:** The backend is fast (<5ms), but local disk I/O can spike. Use skeletons, then swap.
2.  **Error Handling:** The backend throws `402 Payment Required` if they run out of tokens. **Handle this gracefully** (Show "Top Up" modal).
3.  **Offline State:** The app *is* offline capable. If `localhost:8000` is down, show "Connecting to Neural Core..." (do not show "Network Error").

---

**Ready to Build.**
