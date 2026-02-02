# The Perfect Login Flow (Zero-Config)

This diagram visualizes the seamless authentication sequence we have implemented.
It eliminates the need for manual API key copy-pasting by using a local ephemeral server callback.

```mermaid
sequenceDiagram
    participant User
    participant CLI as Terminal (side login)
    participant Local as Localhost:54321
    participant Browser
    participant Web as Sidelith.com
    participant GitHub

    Note over CLI: 1. User types 'side login'
    CLI->>Local: Start Ephemeral Server
    CLI->>Browser: Open https://sidelith.com/login?cli_redirect=http://localhost:54321/callback
    
    User->>Browser: Sees Login Page
    Browser->>Web: GET /login
    User->>Browser: Clicks "Login with GitHub"
    
    Browser->>GitHub: OAuth Handshake
    GitHub-->>Browser: Redirects to /api/auth/callback
    
    Browser->>Web: GET /api/auth/callback?code=...
    Note over Web: 2. Web exchanges code for Session Tokens
    
    Web-->>Browser: 302 Redirect -> http://localhost:54321/callback?access_token=xyz
    
    Browser->>Local: GET /callback?access_token=xyz
    Note over Local: 3. Captures Token
    Local-->>Browser: 200 OK (Success HTML)
    
    Local->>CLI: Pass Token to Validated Identity
    Note over CLI: 4. Saves to ~/.side/credentials
    CLI->>CLI: Update Profile (Tier: PRO)
    CLI-->>User: "Identity Verified."
    
    Note over Local: Server Shuts Down
```

## Key Architectural Decisions
1.  **Ephemeral Server**: The CLI spins up a server on port `54321` *only* for the duration of the login. It is not a permanent daemon.
2.  **Cross-Origin Redirect**: The Web App is explicitly allowed to redirect to `localhost` in the `/api/auth/callback` route.
3.  **Token Transport**: Tokens are passed via URL query parameters on the localhost redirect. This is standard practice for CLI auth (e.g., GCloud, Firebase).

## 🛡️ Is this Overengineered? (The Benchmark)
No. This is the **State of the Art** for Developer Tools.

| Tool | Login Method | Experience | Code Complexity |
| :--- | :--- | :--- | :--- |
| **AWS CLI** | Key / Secret | 🔴 Manual Copy-Paste | Low |
| **Stripe CLI** | **Localhost Callback** | 🟢 **1-Click Magic** | **Medium (This Flow)** |
| **GCloud CLI** | **Localhost Callback** | 🟢 **1-Click Magic** | **Medium (This Flow)** |
| **GitHub CLI** | Device Code | 🟡 "Type ABCD-1234" | Low |
| **Sidelith** | **Localhost Callback** | 🟢 **1-Click Magic** | **Medium** |

**Why we chose this:**
You asked for a *"Perfect natural sign up"*.
-   **Manual Keys**: High friction (Login -> Settings -> Keys -> Create -> Copy -> Terminal -> Paste).
-   **Device Code**: Medium friction (Terminal -> Browser -> Type Code).
-   **Localhost Callback**: **Zero friction** (Terminal -> Browser -> Click -> Done).

This ~50 lines of `auth_server.py` buys you the **Stripe-level** polish.
