# Side Intelligence System
> Real-time intelligence from 200+ curated sources. Zero storage, always fresh.

---

## Overview

Side's Intelligence System provides real-time insights from curated technical sources using smart query analysis and multi-source fetching.

**Key Features**:
- 🎯 **Smart Query Analysis** - Detects intent and selects optimal filters
- 📡 **Multi-Source Fetching** - GitHub, HN, Dev.to, ArXiv, 200+ RSS feeds
- 🛡️ **Error Resilient** - Never fails, silently skips broken sources
- 💾 **Zero Storage** - Fetches on-demand, always fresh
- ⚡ **Fast** - 3-5s response time

---

## Quick Start

```python
from side.intel.api import IntelligenceAPI

api = IntelligenceAPI()

# Get trending signals
signals = await api.get_signals("What's trending in Python?")

# Get answer with RAG
result = await api.answer("Best Redis alternatives")
print(result['answer'])
```

---

## Architecture

```
User Query
    ↓
Query Analyzer (detects intent)
    ↓
Filter Selector (chooses optimal filters)
    ↓
Multi-Source Fetcher (parallel fetch)
    ↓
Strategic Filter (top 10)
    ↓
LLM Answer (with RAG context)
```

---

## Components

### 1. [Query Analysis](./query_analyzer/README.md)
Analyzes queries to detect intent, domain, keywords, and time window.

### 2. [Feed Registry](./feeds/README.md)
Curated list of 200+ high-quality technical sources.

### 3. [Trending APIs](./trending/README.md)
Fetches from GitHub, HN, Dev.to, ArXiv trending endpoints.

### 4. [RSS Fetcher](./rss/README.md)
Error-resilient RSS feed fetcher with automatic retries.

### 5. [Unified API](./api/README.md)
Main interface that ties everything together.

---

## Query Examples

| Query | Intent | Sources Used |
| :--- | :--- | :--- |
| "What's trending in Python?" | TRENDING | GitHub trending, HN top |
| "Best Redis alternatives" | BEST | GitHub search, RSS feeds |
| "Latest AI research" | LATEST | ArXiv recent papers |
| "React vs Vue" | COMPARISON | All sources |

---

## Performance

| Metric | Value |
| :--- | :--- |
| Response time | 3-5s |
| Success rate | >80% |
| Sources | 200+ feeds |
| Cost | $0/month |

---

## Documentation

- [Query Analysis](./query_analyzer/README.md) - Intent detection and context extraction
- [Feed Registry](./feeds/README.md) - Curated source list
- [Trending APIs](./trending/README.md) - Built-in trending endpoints
- [RSS Fetcher](./rss/README.md) - Error-resilient fetching
- [API Reference](./api/README.md) - Unified interface

---

## Development

```bash
# Test query analyzer
python -m side.intel.query_analyzer

# Test RSS fetcher
python -m side.intel.rss_fetcher

# Test trending APIs
python -m side.intel.trending

# Test unified API
python -m side.intel.api
```

---

## License

MIT
