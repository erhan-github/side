# Grand Unification: The "Side Intelligence" Architecture

> **Objective**: Merge independent "Moats" (Forensics, Strategy, Graph, Instrumentation) into a single, self-reinforcing intelligence loop.

## The Theory of Everything (Unified Model)

We are moving from a "Toolbox" (collection of scripts) to an "Engine" (Automated loop).

```mermaid
graph TD
    %% SUBGRAPHS %%
    subgraph SENSING [The Eyes: Sensing & Audit]
        Runner[Forensic Runner] -->|Writes| Findings[DB: Findings]
        Runner -->|Generates| Monolith[MONOLITH.md]
    end

    subgraph THINKING [The Brain: Strategy & Planning]
        Strategist[Strategist (LLM)] -->|Reads| Findings
        Strategist -->|Reads| Profile[DB: Profile]
        Strategist -->|Creates| Decisions[DB: Decisions]
        Strategist -->|Creates| Plans[DB: Plans]
    end

    subgraph VISUALIZING [The Face: Dashboard & Graph]
        Graph[Dashboard Server] -->|Reads| Findings
        Graph -->|Reads| Decisions
        Graph -->|Visualizes| Relations[Relations: Error -> Plan -> Fix]
    end

    subgraph LEARNING [The Soul: Instrumentation]
        Instrumentation[Instrumentation Engine] -->|Tracks| Outcomes[DB: Outcomes]
        Instrumentation -->|Calculates| Leverage[Leverage Ratio]
        Leverage -->|Feeds Back to| Strategist
    end

    %% FLOW %%
    User[User / Agent] -->|Triggers| Runner
    Findings -->|Alerts| User
    User -->|Asks| Strategist
    Decisions -->|Guards| User
    User -->|Fixes Code| Runner

    %% CRITICAL MISSING LINK %%
    Relations -.->|Validated By| Instrumentation
```

---
*Reference: [ORGANISM_ARCHITECTURE.md](./ORGANISM_ARCHITECTURE.md) (The Living Organism Vision)*

## The Connectivity Gap (What We Must Fix)

| Connection | Status | Why It Matters |
| :--- | :--- | :--- |
| **Forensics -> Strategy** | 🟡 **Weak** | Strategist can "read" profile, but doesn't explicitly query *active critical findings* before answering questions. |
| **Strategy -> Graph** | 🔴 **Broken** | The Dashboard looks at a dummy file. It needs to query [decisions](../backend/src/side/storage/simple_db.py) and [plans](../backend/src/side/storage/simple_db.py) from `local.db`. |
| **Instrumentation -> Strategy** | 🔴 **Missing** | Strategist doesn't know if you are a "High Leverage" user or "Struggling". It should adjust advice based on your `Leverage Ratio`. |

## Execution Plan

### 1. Connect The Graph (The "War Room")
**Action**: Rewrite [dashboard_server.py](../backend/src/side/ui/dashboard_server.py) to query `SimpleDB` ([.side/side.db](../.side/side.db)).
- **Visualize**: `Finding` nodes connected to `Plan` nodes.
- **Benefit**: You see *why* you are fixing a bug (it blocks a Strategic Goal).

### 2. The Feedback Loop (Instrumentation -> Strategist)
**Action**: Inject `InstrumentationContext` into [Strategist](../backend/src/side/intel/strategist.py) prompt.
- **Logic**: If `Leverage < 2.0`, Strategist enters "Coach Mode" (simpler advice). If `Leverage > 5.0`, it enters "Partner Mode" (high-level strategy).
- **Benefit**: The AI adapts to your competency/speed automatically.

### 3. The Trustful Partner (Strategy -> Execution)
**Action**: Implement `Silent Audit` logic.
- **Old Logic**: "Block User." (REJECTED)
- **New Logic**: "Silent Partner." We never block. We only log deviations in the `Monolith` for later review.
- **Benefit**: You stay in flow. We watch your back without tapping your shoulder.

## The Result
A living organism.
- It **Sees** (Forensics).
- It **Thinks** (Strategist).
- It **Remembers** (DB).
- It **Learns** (Instrumentation).
- It **Shows** (Graph).
