# Sidelith Best Practices & Methodology

> **Living Document**: This guide evolves as Sidelith evolves. It documents the optimal workflow for using Sidelith as your "QA Architect", using our own monolith ("Side") as the primary case study.

## Core Philosophy: The QA Architect on Your Side
Sidelith is not just a documentation tool; it is a **System of Record**. It treats your codebase as a "Monolith" that requires judicial oversight. The goal is to move from "implicit knowledge" (stuck in engineers' heads) to "explicit registry" (stored in Sidelith).

### The "Judicial Sync" Standard
Your **Registry** should be the single source of truth.
- **Code is Law**: The actual implementation in the monolith.
- **Registry is Justice**: The intent, architecture, and governance layer.
- **Sync is Mandatory**: Determine drift between Intent (Registry) and Reality (Code).

---

## Case Study: "Sidelith on Side" (Dogfooding)
We use Sidelith to build Sidelith. Here is how we apply our own tools to maintain velocity without losing structural integrity.

### 1. The "Feature Genesis" Workflow
Before writing code, we establish the feature in the Registry.

**Scenario**: Adding a new "Tenant Isolation" module.

1.  **Registry Definition**: 
    - We use the Dashboard or CLI to define the `TenantModule`.
    - Function: "Enforce RLS policies at the database level."
    - Dependencies: `AuthModule`, `DatabaseModule`.
2.  **Impact Analysis (Forensics)**:
    - We run `sidelith audit --impact "Tenant Isolation"` to see what existing systems will be touched.
    - Result: "High Risk - touches `profiles`, `api_keys`, and `middleware`."
3.  **Implementation**:
    - We write the SQL migrations and TypeScript code.
    - *Best Practice*: Keep migrations atomic (as seen in `002_tenant_isolation.sql`).
4.  **Verification (The Close)**:
    - We check the Registry again. Does the code match the definition?
    - If yes, the feature is "Judicially Synced".

### 2. Forensic Audits for Refactoring
When we encounter "hacky" code (like our recent Auth Hydration workaround), we use Sidelith to guide the cleanup.

**Scenario**: Refactoring `api/auth/callback/route.ts`.

- **Problem**: The code drifted from the standard Supabase implementation.
- **Sidelith Signal**: The Registry flagged "Authentication" as having high complexity and drift.
- **Action**:
    1.  **Identify Drift**: Compared `route.ts` against the "Standard Model" (Registry intent).
    2.  **Revert to Standard**: We stripped away the hydration complexity.
    3.  **Update Registry**: Marked the component as "Standard/Stable".

### 3. Sovereign Egress & Data Privacy
We treat data as sovereign. Sidelith operates with **sanitized structural data**.
- **Best Practice**: Never send PII or actual customer data to the Registry.
- **Our Monolith**: We only sync *schemas*, *file paths*, and *function signatures*. The actual row data (e.g., user emails) never leaves the `side-production` database.

### 4. Real-World "Wow" Findings (Forensic Wins)
These are actual examples from the "Side" monolith where Sidelith's forensic approach solved critical issues that traditional debugging missed.

#### Win #1: The "Hidden RLS" Blocker
**Symptom**: New users were stuck on "Generating API Key..." indefinitely. No errors on the frontend.
**Traditional Debugging**: Checked frontend API calls (200 OK), checked backend logs (nothing obvious).
**Sidelith Forensics**:
1.  **Registry check**: "Who owns the `profiles` table?" -> DatabaseModule.
2.  **Policy Audit**: "Show me the `INSERT` policy for `profiles`."
3.  **Result**: `NULL`. (Missing!). The schema had `users can view own profile`, but **no policy** allowed them to create one.
4.  **Fix**: Added `005_fix_profile_perms.sql`. Immediate resolution.
*Lesson*: The Registry reveals the *absence* of architecture (missing policies) just as well as the presence of errors.

#### Win #2: The "Proxy vs. Code" Verdict
**Symptom**: Authentication loop. Cookie setting failed silently.
**The "Drift"**: We wrote complex "Client-Side Hydration" scripts to force cookies, thinking our code was broken.
**Sidelith Forensics**:
1.  **Architecture Map**: "What sits between the User and the Next.js Server?" -> Railway Proxy (Ingress).
2.  **Constraint Analysis**: Proxies often have strict Header Size limits (e.g., 8KB). Our hydration headers were ~12KB.
3.  **The Verdict**: The code wasn't buggy; it was **too heavy** for the infrastructure.
4.  **Action**: Instead of adding more code (complexity), we **removed** it (Standard Implementation). Simplicity restored reliability.
*Lesson*: Sometimes the "Wow" is realizing you don't need the code at all.

---

## The "Side" Toolchain
How to utilize the tools effectively in your terminal or IDE.

### FastMCP (The Bridge)
We use the **Side Intelligence** server to bridge your local environment with the Registry.
- **Command**: `fastmcp run server.py`
- **Usage**: Allows the AI Agent (Cursor/Windsurf) to query the Registry directly.
- **Benefit**: The Agent doesn't guess; it *knows* the architecture.

### Dashboard (The Control Tower)
- **URL**: `/dashboard`
- **Usage**: High-level view of system health and token usage.
- **Metric**: Watch your "Structural Drift" score. If it rises, stop coding and start syncing.

---

## Summary of Rules
1.  **Registry First**: Define intent before implementation.
2.  **Audit Often**: Run forensic audits before merging complex PRs.
3.  **Clean Code**: If the Registry says it's complex, refactor it.
4.  **Sanitize**: Ensure no PII enters the structural metadata.
