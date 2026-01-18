# CSO.ai API Reference

Complete reference for all CSO.ai MCP tools.

---

## Tools Overview

CSO.ai provides 3 core tools, each designed for a specific use case:

| Tool | Purpose | Speed | Cache |
|------|---------|-------|-------|
| `read` | Get personalized article recommendations | < 100ms | 1 hour |
| `analyze_url` | Evaluate if a URL is worth reading | < 1s | Per URL |
| `strategy` | Get strategic advice on what to focus on | < 2s | 1 hour |

---

## Tool: `read`

Get top 5 articles personalized for your tech stack.

### Description
Fetches articles from Hacker News, Lobsters, and GitHub Trending, scores them against your codebase, and returns the most relevant ones.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `refresh` | boolean | No | `false` | Force refresh from sources (bypasses cache) |

### Returns

Formatted string with:
- Top 5 articles with relevance scores (0-100)
- Reasoning for each recommendation
- Estimated read time
- Performance metrics

### Examples

**Basic Usage**:
```
User: "What should I read?"

CSO: 📰 Top Articles for Your Stack (Python + FastAPI)

     1. [95] ██████████ FastAPI Auth Best Practices
        💡 Directly relevant to your API architecture
        🔗 https://...
        ⏱️ ~8 min read

     ⚡ Analyzed in 80ms | From cache
```

**Force Refresh**:
```
User: "What should I read? (refresh: true)"

CSO: 📰 Top Articles for Your Stack (Python + FastAPI)
     🔄 Fetching fresh articles...

     [Articles...]

     🔄 Analyzed in 2.5s | Next refresh in 60 min
```

### Performance

- **Query cache hit**: < 100ms (instant)
- **Article cache hit**: < 1s (fast)
- **Fresh fetch**: < 3s (acceptable)

### Caching Strategy

1. **Query Cache** (1-hour TTL)
   - Stores complete formatted output
   - Invalidated on context change
   - Hash-based deduplication

2. **Article Cache** (1-hour TTL)
   - Stores raw articles from sources
   - Shared across queries
   - Auto-refreshed by CacheWarmer

3. **Score Cache** (Permanent)
   - Stores article scores per profile
   - Never expires (profile-specific)
   - Improves over time

---

## Tool: `analyze_url`

Evaluate if a specific URL is worth your time.

### Description
Fetches the URL, extracts title and description, and scores it against your tech stack to help you decide if it's worth reading.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | URL to analyze (auto-adds https:// if missing) |

### Returns

Formatted string with:
- Relevance score (0-100)
- Verdict (Highly Recommended / Worth Your Time / Maybe Useful / Skip)
- Reasoning
- Key takeaways (if available)

### Examples

**Highly Relevant**:
```
User: "Is this worth reading? https://fastapi.tiangolo.com/auth"

CSO: 🎯 Relevance Score: 92/100

     ✅ HIGHLY RECOMMENDED

     Why: This article covers FastAPI authentication,
     directly relevant to your current work on auth.py

     Key Takeaways:
     • OAuth2 with JWT tokens
     • Password hashing best practices
     • Dependency injection for auth

     ⚡ Analyzed in 0.9s
```

**Low Relevance**:
```
User: "Is this worth reading? https://react-tutorial.com"

CSO: 🎯 Relevance Score: 15/100

     ⏭️ SKIP THIS ONE

     Why: This is a React tutorial, but your stack is
     Python + FastAPI (backend-focused)

     ⚡ Analyzed in 0.8s
```

### Performance

- **Typical**: < 1s (network fetch + scoring)
- **Cached**: < 100ms (if URL analyzed before)

### Error Handling

- **Invalid URL**: Returns user-friendly error with example
- **Network failure**: Retries with exponential backoff (3 attempts)
- **Timeout**: 15s timeout, then graceful failure

---

## Tool: `strategy`

Get strategic advice based on your current work.

### Description
Analyzes your recent commits, detects what you're working on, and provides prioritized strategic advice with relevant reading recommendations.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `context` | string | No | `""` | Additional context about what you're working on |

### Returns

Formatted string with:
- Current focus area (auto-detected)
- Recent activity summary
- Prioritized actions (Critical / Important / Opportunity)
- Relevant reading recommendations
- Performance metrics

### Examples

**With Auto-Detected Context**:
```
User: "What should I focus on?"

CSO: 🎯 Strategic Focus (Python + FastAPI)

     📊 Recent Activity: 15 commits in last 7 days
     🔍 Working on: Authentication

     🔴 CRITICAL
     • Fix authentication flow (3 FIXMEs in auth.py)
     • Your recent commits show auth is unstable

     🟡 IMPORTANT
     • Add API tests (0% coverage in /api/endpoints)

     💡 OPPORTUNITY
     • Consider FastAPI 0.110 upgrade (just released)

     📚 Relevant Reading:
     • "FastAPI Auth Best Practices" (HN, 156 pts)

     ⚡ Generated in 1.8s
```

**With User Context**:
```
User: "What should I focus on? I'm planning to add OAuth2"

CSO: 🎯 Strategic Focus (Python + FastAPI)

     📊 Context: Planning OAuth2 implementation

     🔴 CRITICAL
     • Review security best practices first
     • Read: "OAuth2 Security Pitfalls"

     🟡 IMPORTANT
     • Choose library (authlib vs python-jose)
     • Set up token refresh strategy

     💡 OPPORTUNITY
     • Consider social login (Google, GitHub)

     📚 Relevant Reading:
     • "OAuth2 with FastAPI" (comprehensive guide)
     • "JWT Best Practices" (security-focused)

     ⚡ Generated in 2.1s
```

### Performance

- **With LLM** (Groq API): < 2s
- **Without LLM** (fallback): < 500ms

### LLM Integration

**With Groq API**:
- Uses Llama 3.3 70B for intelligent analysis
- Considers codebase context + recent commits
- Provides nuanced, actionable advice

**Without Groq API** (fallback):
- Uses heuristic-based analysis
- Still provides value (pattern detection)
- Recommends relevant articles

---

## Common Patterns

### Morning Routine
```
1. Open Cursor
2. "What should I read?"
3. Skim top 5 articles
4. Bookmark interesting ones
5. "What should I focus on?"
6. Prioritize your day
```

### Before Reading an Article
```
1. Find interesting article
2. "Is this worth reading? [URL]"
3. Check score & reasoning
4. Decide: read now / later / skip
```

### Strategic Planning
```
1. "What should I focus on?"
2. Review critical items
3. "What should I read?" (for research)
4. Make informed decisions
```

---

## Error Handling

All tools include robust error handling:

### Network Errors
- **Retry Logic**: 3 attempts with exponential backoff (1s → 2s → 4s)
- **Timeout**: 30s default, graceful failure
- **User Message**: "Network error. Please try again."

### Invalid Input
- **URL Validation**: Auto-fixes common issues (missing https://)
- **User Message**: Clear explanation + example

### LLM Errors
- **Graceful Degradation**: Falls back to heuristics
- **User Message**: "Using fallback analysis (no LLM)"

---

## Performance Optimization

### Caching Layers

1. **Query Cache** (L1)
   - Fastest: < 100ms
   - Stores complete formatted output
   - 1-hour TTL

2. **Article Cache** (L2)
   - Fast: < 1s
   - Stores raw articles
   - 1-hour TTL

3. **Score Cache** (L3)
   - Permanent storage
   - Per profile-article pair
   - Never expires

### Background Services

- **CacheWarmer**: Pre-fetches articles every 30 min
- **ContextTracker**: Updates work context on file changes
- **CleanupScheduler**: Removes old data daily at 3 AM

---

## Best Practices

### 1. Use Query Cache
```
# Good: Let cache work
"What should I read?"

# Avoid: Unnecessary refreshes
"What should I read? (refresh: true)"
```

### 2. Provide Context for Strategy
```
# Better
"What should I focus on? I'm adding OAuth2"

# Good
"What should I focus on?"
```

### 3. Batch URL Analysis
```
# Efficient: Analyze before reading
1. Find 5 interesting URLs
2. Analyze each
3. Read top 2-3

# Inefficient: Read everything
1. Read all 5 articles
2. Realize 3 weren't relevant
```

---

## Troubleshooting

See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) for common issues and solutions.

---

## Future API Features

Planned for future releases:

- **Custom Sources**: Add your own RSS feeds
- **Team Sharing**: Share recommendations with team
- **Webhooks**: Get notified of breaking changes
- **Export**: Save articles to Notion, Obsidian, etc.

See [ROADMAP.md](ROADMAP.md) for details.
