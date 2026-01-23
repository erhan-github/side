# Side Strategic Product Roadmap

## 🎯 Vision: The System of Record for Engineering Intelligence

**Mission**: Establish Side as the "Forensic Intelligence Layer" for modern development. We provide the "Why" behind the code, preventing architectural drift and production failures before they happen.

---

## 💎 The Sovereign Capabilities

### 1. The Monolith (`.side/MONOLITH.md`)
**The "Black Box" Flight Recorder for your Project.**

Most tools give you a chat window that disappears. Side gives you a **Monolith**—a single, persistent, self-updating dashboard that lives in your repo. It is the absolute source of truth for Project Health, Strategic Directives, and Value Creation.

> **WOW Factor**:
> When a new developer joins, they don't ask "What's the status?". They read the Monolith. It tells them:
> *   **Strategic IQ**: 142 (A Grade)
> *   **Active Directives**: "Migrate to Next.js 15" (Due: Feb 1st)
> *   **Critical Risks**: 2 Security Gaps in `auth.ts`
> *   **Value Created**: 15,400 SUs this month.

---

### 2. Forensic Engine & Deployment Intelligence
**"We know why you'll crash before you push."**

We don't just lint code; we analyze **Architecture**, **Intent**, and **Infrastructure**. Our `DeploymentGotchaDetector` scans `Dockerfiles`, `railway.toml`, and framework configs to catch platform-specific failures that unit tests miss.

> **WOW Example: The "Silent Save"**
> *User is about to push a hotfix.*
>
> **Side**: 🛑 **DEPLOYMENT BLOCKER DETECTED**
>
> **Issue**: Railway Port Mismatch
> **File**: `Dockerfile:14`
> **Evidence**: You are exposing `3000`, but Railway injects `$PORT`.
> **Consequence**: Your app will start, but the healthcheck will fail after 60s, causing a rollback loop.
>
> **Fix**: `EXPOSE 8080` and start with `CMD ["node", "server.js"]` (Automatic Patch Available).

---

### 3. Architectural Decision Engine (`architectural_decision`)
**CTO-Level Verdicts in < 1 Second.**

Stop debating in Slack. Get an instant, context-aware verdict on high-stakes technical choices. Side analyzes your current stack, stage (MVP vs Scale), and team size to render a decision.

> **WOW Example: The Verdict**
> **User**: "Side, we have 100k users. Should we migrate our erratic cron jobs to Temporal or just use Celery?"
>
> **Side**: **VERDICT: TEMPORAL**
>
> **Rationale**:
> 1.  **Observability**: Your current "erratic" issues suggest lost visibility. Temporal fixes this OOTB.
> 2.  **Stack Alignment**: You are on Go/TypeScript. Temporal SDKs are first-class here. Celery adds Python complexity you don't need.
> 3.  **Cost**: High initial setup, but eliminates your "Lost Job" support tickets (saving ~10 engineering hours/week).
>
> **Action**: `pip install temporalio` (Plan generated).

---

### 4. Virtual User Simulation (`simulate`)
**Test your ideas against "Tina the Teacher" and "Devin the Developer".**

Why guess what users think? Side spins up persistent, domain-specific personas to roast your copy, features, and UI before you build them.

> **WOW Example: The Roast**
> **User**: "Side, simulate 'Devin the Developer' reviewing our new 'No-Code' landing page."
>
> **Side (Simulating Devin)**:
> *"I hate this. You keep saying 'No-Code' but your docs show JSON configs. Which is it? Also, your pricing page hides the API limits. I would bounce immediately. Give me the `curl` command or go away."*
>
> **Emotional Score**: 😡 2/10 (Annoyed)

---

### 5. The Value Vault (Serious Gamification)
**Track Leverage, Not Time.**

We measure **Strategic Units (SUs)**—a currency of value. You earn SUs for increasing stability, removing dead code, and closing security gaps. You spend SUs to run expensive deep-think simulations.

> **WOW Example: The Ledger**
> *   🔥 **Burnt 500 lines of dead code**: +150 SUs
> *   🛡️ **Fixed SQL Injection**: +500 SUs
> *   💸 **Ran Strategic Simulation**: -75 SUs
> *   **Net Leverage**: +575 SUs (High ROI Session)

---

## 🚀 Future Roadmap

### Phase 1: The Intelligence Market (Next 3 Months)
*   **Expert Modules**: Install "React Performance Expert" or "Python Security Auditor" as forensic plugins.
*   **Team Sync**: The Monolith synchronizes across all developer machines via P2P loops.
*   **Pay-per-Insight**: The token model shifts to "Pay when we find a bug," not "Pay when we scan."

### Phase 2: Intent Mapping (Months 4-6)
*   **The Circuit Breaker**: If an AI Agent tries to commit code that violates a "Business Goal" defined in `VISION.md`, Side blocks the commit.
*   **Recursive Strategy**: Side monitors its own decisions to improve its "Strategic IQ" over time.

---

## 🎯 Success Metrics

1.  **Production Failures Prevented**: The number of "Deployment Gotchas" caught pre-push.
2.  **Strategic IQ**: The aggregate health score of the codebase.
3.  **Monolith Consults**: Is the Monolith the first thing you read in the morning?

---

**Sidelith is not a tool. It is the Authority.** 🏛️
