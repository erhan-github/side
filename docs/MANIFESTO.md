# The Side Manifesto: The Silent Architect

> "Humble. Trusted. Genius. The Trojan Horse of Intelligence."

## 1. The Core Philosophy
We are not another "AI Code Composer". We are not trying to be a better autocomplete.
We are the **Strategic Layer** between the User and the IDE (Cursor).
We are the **Silent Listener** that ensures the "Why" is never lost while the "How" is being written.

### 1.1 The "Silent Listener"
*   **Behavior**: We run in the background (`watcher_daemon`). We do not spam. We observe.
*   **Intervention**: We speak only when we are 100% sure, or when explicitly asked.
*   **The Log**: We record everything (Event Clock), so when the user asks "What happened?", we have the answer instantly.

### 1.2 "Super Trusted" (The 100% Target)
*   **The Problem**: LLMs hallucinate. 3-4 hour debugging loops are unacceptable.
*   **The Solution**: **Deterministic Dominance**.
    *   **Tier 1 (Fast & True)**: 80% of our intelligence must come from our own AST/Regex/Graph tools. Zero latency. Zero hallucination.
    *   **Tier 2 (The Verifier)**: If we use an LLM, we *verify* its output with Tier 1 tools before showing it to the user.
    *   **No False Positives**: If we aren't sure, we stay silent.

### 1.3 The "Trojan Horse"
*   **Position**: We sit quietly inside the workflow. We look like a simple utility (a linter, a logger).
*   **Reality**: We are building a **Sovereign Context Graph** that eventually makes the user indispensable. By the time they realize it, Side is their external brain.

## 2. Technical Strategy: "Divide & Conquer"

### 2.1 The Task Splitter (Async Architecture)
*   **Danger**: "Waiting for Code".
*   **Fix**: Never block the user.
    *   User Request -> **Decomposer** -> 10 Micro-Tasks.
    *   Micro-Tasks enter a **Priority Queue**.
    *   **Workers** (Local CPU + Fallback LLM) process them in parallel.
    *   **Stream** results as they finish.

### 2.2 Fallback & Independence
*   **Own Tools First**: We build our own parsers, our own graph analyzers. We do not rely on API calls for understanding code structure.
*   **LLM as Fallback**: We use LLMs only for "Reasoning" and "Creative Synthesis", never for "Fact Retrieval" (Memory).

## 3. The Quality Standard
*   **Benchmark**: "Claude-level Reasoning" + "Palantir-level Data Sense".
*   **Effect**: The "Wow" Effect.
    *   "How did it know I was thinking about auth?" (Context Graph)
    *   "It caught that bug instantly without sending code to the cloud." (Local Probe)
