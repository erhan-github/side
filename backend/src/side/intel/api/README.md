# Unified Intelligence API
> Single interface for all intelligence operations

---

## Purpose

Main API that combines:
- Query analysis (intent detection)
- Smart filter selection
- Multi-source fetching
- Strategic filtering
- RAG-enhanced answers

**One API, all intelligence**.

---

## Quick Start

```python
from side.intel.api import IntelligenceAPI

api = IntelligenceAPI()

# Get signals
signals = await api.get_signals("What's trending in Python?")

# Get answer with RAG
result = await api.answer("Best Redis alternatives")
print(result['answer'])
```

---

## Core Methods

### `get_signals(query, max_results=10)`

Get relevant signals for a query.

**Parameters**:
- `query` (str): User's query
- `max_results` (int): Max signals to return

**Returns**: List of signal dicts

**Example**:
```python
signals = await api.get_signals("What's trending in Python?")

for signal in signals:
    print(f"• {signal['title']}")
    print(f"  Source: {signal['source']}")
    print(f"  Score: {signal['score']}/100")
```

---

### `answer(question, use_signals=True)`

Answer a question using RAG with intelligence signals.

**Parameters**:
- `question` (str): User's question
- `use_signals` (bool): Whether to use signals

**Returns**: Dict with answer and metadata

**Example**:
```python
result = await api.answer("What are the best Redis alternatives?")

print(result['answer'])
# "Based on trending signals, consider Dragonfly (25x faster)..."

print(f"Used {result['signals_used']} signals")
# Used 5 signals
```

---

## How It Works

### 1. Query Analysis

```python
# User query: "What's trending in Python?"

context = query_analyzer.analyze(query)
# → Intent: TRENDING
# → Domain: GENERAL
# → Language: python
# → Time: week
```

### 2. Filter Selection

```python
if context.intent == QueryIntent.TRENDING:
    # Use trending APIs
    signals = await fetch_trending(context)
elif context.intent == QueryIntent.LATEST:
    # Use recent/new filters
    signals = await fetch_latest(context)
elif context.intent == QueryIntent.BEST:
    # Use top/best filters
    signals = await fetch_best(context)
else:
    # Use search
    signals = await fetch_search(context)
```

### 3. Multi-Source Fetching

```python
# Fetch from multiple sources in parallel
trending = await get_trending_signals()  # GitHub, HN, Dev.to
rss = await get_fresh_content()          # 200+ RSS feeds

all_signals = trending + rss
```

### 4. Strategic Filtering

```python
# Filter to strategic signals
strategic = filter_strategic_articles(all_signals)

# Score with heuristics
for signal in strategic:
    signal['score'] = score_article_heuristic(signal)

# Sort and return top N
strategic.sort(key=lambda x: x['score'], reverse=True)
return strategic[:max_results]
```

### 5. RAG Answer

```python
# Format signals as context
context = format_signals(signals)

# Build prompt
prompt = f"""
{context}

User Question: {question}

Based on the signals above, provide an answer.
"""

# Get LLM answer
answer = await strategist.ask_llm(prompt)
```

---

## Query Examples

| Query | Intent | Sources | Signals |
| :--- | :--- | :--- | :--- |
| "What's trending in Python?" | TRENDING | GitHub, HN | 5 repos |
| "Best Redis alternatives" | BEST | GitHub, RSS | 5 tools |
| "Latest AI research" | LATEST | ArXiv | 5 papers |
| "React vs Vue" | COMPARISON | All | 5 articles |

---

## Response Format

### `get_signals()` Response

```python
[
    {
        'id': 'github-12345',
        'title': 'Cool new tool',
        'description': 'A tool for X',
        'url': 'https://github.com/...',
        'source': 'github',
        'score': 85,
        'category': 'competition',
        'keywords': ['tool', 'python'],
        'published_at': '2026-01-18T10:00:00Z'
    },
    # ... more signals
]
```

### `answer()` Response

```python
{
    'answer': 'Based on trending signals, consider...',
    'signals_used': 5,
    'signal_titles': [
        'Dragonfly: Redis Alternative',
        'KeyDB: Multithreaded Redis',
        # ...
    ],
    'enhanced': True  # Whether signals were used
}
```

---

## Performance

| Metric | Value |
| :--- | :--- |
| **Query analysis** | <10ms |
| **Signal fetching** | 3-5s |
| **Total response** | 3-5s |
| **Success rate** | >80% |
| **Cost** | $0/month |

---

## Error Handling

The API never fails:
- ✅ Broken feeds are skipped
- ✅ Failed sources are logged
- ✅ Always returns results (even if empty)
- ✅ Graceful degradation

```python
# Even if all sources fail, you get an answer
result = await api.answer("Some question")
# → Uses LLM without signals
# → signals_used = 0
# → enhanced = False
```

---

## Testing

```bash
python -m side.intel.api
```

**Output**:
```
UNIFIED INTELLIGENCE API TEST
======================================================================

1. Testing: What's trending in Python?
   Found 5 signals:
   1. Cool repo... (github)
   2. HN discussion... (hackernews)
   ...

✅ Unified API working!
```

---

## Advanced Usage

### Custom Filter Selection

```python
# Force specific intent
from side.intel.query_analyzer import QueryIntent

api = IntelligenceAPI()

# Override intent detection
context = api.query_analyzer.analyze(query)
context.intent = QueryIntent.BEST  # Force "best" filter

signals = await api._fetch_best(context)
```

### A/B Testing

```python
# Test with and without signals
result_with = await api.answer(question, use_signals=True)
result_without = await api.answer(question, use_signals=False)

# Compare quality
print(f"With signals: {len(result_with['answer'])} chars")
print(f"Without: {len(result_without['answer'])} chars")
```

---

## Dependencies

- `query_analyzer`: Intent detection
- `trending`: GitHub, HN, Dev.to, ArXiv APIs
- `rss_fetcher`: RSS feed fetching
- `text_analysis`: Strategic filtering
- `strategist`: LLM integration

---

## See Also

- [Query Analysis](../query_analyzer/README.md)
- [Trending APIs](../trending/README.md)
- [Feed Registry](../feeds/README.md)
- [RSS Fetcher](../rss/README.md)
