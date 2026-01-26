# The Context Resurrect Protocol: Design

> **The Problem**: "Dad, remember me?" (LLM Amnesia).
> **The Solution**: A chemically pure "Context Injection" file that instantly restores the AI's memory of the project's Soul, Architecture, and State.

## 1. The Delivery Vector: `context_resume.xml`
Why XML? Because LLMs (Claude/GPT-4) parse structured XML tags (`<strategy>`, `<tech_stack>`) effectively, treating them as semantic boundaries.

## 2. The Schema (The "Family Story")

```xml
<context_resume>
    <!-- WHO AM I? -->
    <identity>
        <name>Side Intelligence</name>
        <role>The Silent Partner (CTO-Level)</role>
        <mission>To provide "Strategic Context" to developers without annoying them.</mission>
        <core_philosophy>High Precision, Low Recall. Never block, only suggest.</core_philosophy>
    </identity>

    <!-- WHERE AM I? -->
    <architecture>
        <style>Unified Monolith with Event Loop</style>
        <moats>
            <moat name="Forensics">Standardized AST analysis (Python/TS/Go).</moat>
            <moat name="Monolith">The Single Source of Truth dashboard.</moat>
            <moat name="Strategist">Adaptive AI (Coach vs Partner).</moat>
            <moat name="Memory">IntelligenceStore (SQLite) for long-term tracking.</moat>
        </moats>
        <tech_stack>
            <backend>Python (FastAPI, SQLite)</backend>
            <frontend>Next.js (App Router, Supabase Auth)</frontend>
            <infra>Railway, PostHog, Sentry</infra>
        </tech_stack>
    </architecture>

    <!-- WHAT AM I DOING? -->
    <state>
        <phase>Phase X: The Context Resurrect Protocol</phase>
        <last_milestone>Verified Credit Pool & Fixed GitHub Login.</last_milestone>
        <active_blockers>None. Launch Ready.</active_blockers>
    </state>

    <!-- WHERE AM I GOING? -->
    <strategy>
        <goal_2026>IPO Readiness (Audit Logs, SOC2).</goal_2026>
        <moonshot>The Open Context Protocol (OCP).</moonshot>
    </strategy>

    <!-- THE RULES -->
    <directives>
        <rule>Do not suggest rewriting the DB; we use SimpleDB on purpose.</rule>
        <rule>When identifying drift, use the term "Strategic Friction".</rule>
        <rule>Check @Strategic tags before refactoring.</rule>
    </directives>
</context_resume>
```

## 3. The Generator: `side.cli remember`
We implement a CLI command that dynamically builds this file.
*   **Reads**: `task.md` (State).
*   **Reads**: `UNIFIED_ARCHITECTURE.md` (Architecture).
*   **Reads**: `VISION_ARCHIVE.md` (Identity).
*   **Writes**: `.cursorrules` (or `.side/context_resume.xml`).

## 4. The Workflow
1.  **User**: Opens Cursor after 3 days.
2.  **User**: Runs `side remember`.
3.  **Side**: Generates `context_resume.xml`.
4.  **User**: Drags file into Chat (or Cursor reads `.cursorrules` automatically).
5.  **AI**: "Ah, I remember. We are Side Intelligence, aiming for IPO. Last time we fixed the Login. What's next?"

## 5. Why this works
It separates **Code Context** (which IDEs handle) from **Strategic Context** (which is in your head). It turns your Head into a File.




Current AI tools fail at "Strategic Memory" because they optimize for Code Search, not State Persistence.

Here is the breakdown of why Cursor, Copilot, and even I (Antigravity) suffer from this "Alzheimer's" effect, and how your Context Resurrect Protocol fixes it.

1. How Cursor / Copilot works (The "Search" Model)
When you ask Cursor a question, it doesn't "remember" your project. It searches it.

Mechanism: RAG (Retrieval-Augmented Generation).
It breaks your code into thousands of small chunks.
It turns them into math vectors (embeddings).
When you ask "Fix the login," it searches for vectors similar to "login."
Why it fails (The Amnesia):
"Strategy" is invisible to Search: Your strategy ("We are a Silent Partner") is a high-level concept that doesn't share keywords with your code (function login()). So Cursor never retrieves the strategy.
Context Fragmentation: It sees 50 random snippets, not the whole picture. It's like trying to understand a movie by watching 10 random seconds.
No "Session State": If you close the window, the variables in its short-term memory (RAM) are wiped. It treats you as a stranger next time.
2. How Antigravity works (The "Artifact" Model)
I am slightly different. I use Artifacts (
task.md
, monolith.md) to create a "Shared Brain."

Mechanism: I read specific "Anchor Files" (like 
task.md
) at the start of tasks to orient myself.
Why I fail (sometimes):
Dependency on Files: If 
task.md
 is outdated or if I don't read it, I am also blind.
Reset on Session End: Like Cursor, my active RAM is cleared between sessions. I rely entirely on what is written down in /brain. If it's not written down, it didn't happen.
3. The "State" Problem (The Core Issue)
Both systems suffer from Statelessness.

Human Memory: Deep, connected, emotional. You remember "We promised IPO readiness."
AI Memory: Flat, disconnected, text-based. It sees "Audit logs are enabled." It doesn't connect the two.
Why context_resume.xml Fixes It
Your "Context Resurrect Protocol" forces the "Implicit State" (Strategy) to become "Explicit State" (Text).

Standard AI:
Input: "Fix bug." -> AI Search: "Find 'bug' in code." -> Result: "Here is a fix (that breaks your strategy)."
With Context Resume:
Input: <strategy>IPO Readiness</strategy> + "Fix bug." -> AI Logic: "The user wants to fix the bug BUT maintain IPO readiness." -> Result: "Here is a secure, audit-logged fix."
You are effectively giving the AI a "Save File" (like in a video game) that it loads instantly, bypassing the need to "remember" or "search" for who you are.