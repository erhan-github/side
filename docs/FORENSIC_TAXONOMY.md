# Forensic Taxonomy: Monitored Intelligence

This document defines the 24+ dimensions of intelligence monitored by the `Side` system and how they are visualized in your Command Center.

## 1. Categorization Rationale

| Section | Focus | Intelligence Type | Source |
| :--- | :--- | :--- | :--- |
| **Forensic Prompting** | **Strategic Scaling** | Heuristic & Strategic | Strategic Evaluator / Strategist |
| **Deep Intelligence** | **Code Sovereignty** | Semantic & Logical | Groq/Llama Deep Scans |

### Why two titles?
- **Forensic Prompting** identifies high-level "gaps" in your project's trajectory (e.g., "You have no Vision doc", "Your commit velocity is stalling"). It prods you toward **growth**.
- **Deep Intelligence** identifies low-level "flaws" in your implementation (e.g., "Your auth cookie is missing `SameSite=None`", "Your middleware has a redirection loop"). It protects your **integrity**.

---

## 2. Monitored Dimensions

### A. Deep Intelligence (Semantic Layer)
These are audited via Deep LLM analysis (Groq-powered):
- **Semantic Security**: Auth bypasses, CSRF, insecure cookie policies, hardcoded secrets.
- **Logic Consistency**: Redirection loops, state hydration sync, complex branch conflicts.
- **Intent Verification**: Does the code actually do what the comments/docs say?
- **Dead Code**: Identifying logically unreachable but syntactically valid paths.

### B. Forensic Prompting (Strategic Layer)
These are calculated via the 10-Dimension Strategic IQ:
1. **Architecture**: Project structure, monorepo health, language distribution.
2. **Velocity**: Commit frequency, PR speed, task completion rate.
3. **Resilience**: Test coverage, CI/CD integration, error handling robustness.
4. **MarketFit**: User persona simulations, product-market alignment data.
5. **Investor**: VISION.md, ROADMAP.md, Pitch clarity.
6. **Docs**: README quality, API documentation, internal wikis.
7. **Compliance**: Security policy files, audit trails, activity logging.
8. **Legal**: License files, privacy policies, data sovereignty.
9. **Community**: Contributor count, social signals (if connected).
10. **Security (Base)**: Raw vulnerability counts (CRITICAL/HIGH).

### C. Forensic Probes (Technical Layer)
Behind the scenes, the system runs 14+ technical probes:
- **Performance**: N+1 queries, slow database calls, I/O bottlenecks.
- **Cost**: Cloud spend estimation, token usage efficiency.
- **DevOps**: Dockerfile hygiene, Railway/Vercel configuration flaws.
- **API Design**: Endpoint consistency, REST/GraphQL standards.
- **Frontend**: Accessibility, bundle size, hydration errors.
- **Database**: Migration hygiene, index efficiency, schema drift.

---
*Reference: [ORGANISM_ARCHITECTURE.md](./ORGANISM_ARCHITECTURE.md)*
