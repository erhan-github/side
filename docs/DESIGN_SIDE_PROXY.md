# Managed Credit Pool: "Side Proxy" Engineering Plan

To support 10,000 users tomorrow without BYOK, we are implementing a **Side Proxy** - a high-velocity, round-robin load balancer for enterprise LLM keys.

## 1. Architectural Blueprint (Palantir Level)

The Side Proxy acts as a **Global Credit Buffer**. It abstracts the individual rate limits of $N$ enterprise keys into a single, high-throughput "Virtual Key" for the entire fleet.

### Key Components:
- **ManagedCreditPool**: A stateful registry of available keys, their provider types, and their health status (Rate Limit Tripwires).
- **Entropy-Based Round Robin**: Instead of linear cycling, we use weighted distribution to prevent "Hot-Key" patterns and API throttling.
- **Fail-Fast Circuit Breaker**: If a key returns a `429`, it is automatically placed in "Cool-Down" for $T$ minutes, and the request is retried on the next available tier.

---

## 2. Proposed Changes

### [Component] LLM Infrastructure

#### [MODIFY] [client.py](file:///Users/erhanerdogan/Desktop/side/backend/src/side/llm/client.py)
Update `LLMClient` to support `ManagedCreditPool`. If a single `GROQ_API_KEY` is not found, it will look for `SIDE_POOL_KEYS` - a comma-separated list of enterprise assets.

#### [NEW] [managed_pool.py](file:///Users/erhanerdogan/Desktop/side/backend/src/side/llm/managed_pool.py)
Implement the `ManagedCreditPool` class:
- `get_next_key(provider)`: Circular buffer for key rotation.
- `mark_as_cooling(key)`: Temporary exclusion from rotation.

---

## 3. Minimal Engineering version (10k Ready)

We will use a **Static Environment Pool** for tomorrow's launch.
1. Add `SIDE_POOL_KEYS="key1,key2,key3..."` to the production environment.
2. The `LLMClient` will rotate through these on every forensic request.
3. This adds **0 server-side complexity** while providing $N \times$ throughput.

## 4. Verification Plan

### Automated Tests
- `pytest tests/llm/test_pooling.py`: Verify that sequential requests utilize different keys from the pool.
- `diag_pool.py`: A stress test script that triggers 100 concurrent requests to simulate user spike.
