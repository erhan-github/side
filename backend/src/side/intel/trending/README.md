# Trending APIs
> Zero-storage intelligence from built-in trending endpoints

---

## Purpose

Fetches trending signals directly from sources' built-in trending APIs:
- **GitHub**: Trending repositories
- **HackerNews**: Top stories
- **Dev.to**: Top articles
- **ArXiv**: Recent papers

**Zero storage** - always fresh, always real-time.

---

## Usage

```python
from side.intel.trending import get_trending_signals

# Get trending across all sources
signals = await get_trending_signals(
    github_since="weekly",
    max_results=10
)

# Get trending repos only
from side.intel.trending import get_trending_repos
repos = await get_trending_repos(language="python")

# Get trending discussions
from side.intel.trending import get_trending_discussions
discussions = await get_trending_discussions()
```

---

## Sources

### 1. GitHub Trending

**Endpoint**: `https://api.github.com/search/repositories`

**Filters**:
- `since`: "daily", "weekly", "monthly"
- `language`: "python", "rust", "go", etc.
- `sort`: "stars" (default)

**Example**:
```python
repos = await fetch_github_trending(
    since="weekly",
    language="python"
)
```

**Returns**:
```python
{
    'id': 'github-12345',
    'title': '🔥 username/repo-name',
    'description': 'A cool new tool',
    'url': 'https://github.com/username/repo',
    'source': 'github',
    'metadata': {
        'stars': 1200,
        'language': 'Python',
        'trending_period': 'weekly'
    }
}
```

---

### 2. HackerNews Top Stories

**Endpoint**: `https://hacker-news.firebaseio.com/v0/topstories.json`

**Filters**:
- Top stories (front page)
- Best stories
- New stories

**Example**:
```python
stories = await fetch_hn_top_stories(limit=30)
```

**Returns**:
```python
{
    'id': 'hn-39123456',
    'title': 'Show HN: My new project',
    'url': 'https://example.com',
    'source': 'hackernews',
    'metadata': {
        'score': 250,
        'comments': 45
    }
}
```

---

### 3. Dev.to Top Articles

**Endpoint**: `https://dev.to/api/articles?top=7`

**Filters**:
- `top=7`: Top this week
- `top=30`: Top this month

**Example**:
```python
articles = await fetch_devto_top(days=7)
```

**Returns**:
```python
{
    'id': 'devto-12345',
    'title': 'How to build X',
    'url': 'https://dev.to/article',
    'source': 'devto',
    'metadata': {
        'reactions': 150,
        'comments': 20,
        'tags': ['python', 'tutorial']
    }
}
```

---

### 4. ArXiv Recent Papers

**Endpoint**: `https://export.arxiv.org/api/query`

**Filters**:
- `categories`: "cs.AI+cs.LG+cs.CL"
- `sortBy`: "submittedDate"
- `days`: Papers from last N days

**Example**:
```python
papers = await fetch_arxiv_recent(
    categories="cs.AI+cs.LG+cs.CL",
    days=7
)
```

**Returns**:
```python
{
    'id': 'arxiv-2401.12345',
    'title': 'Novel Approach to X',
    'url': 'https://arxiv.org/abs/2401.12345',
    'source': 'arxiv',
    'published_at': '2026-01-15T10:00:00Z'
}
```

---

## Combined Fetching

The main function fetches from all sources in parallel:

```python
signals = await get_trending_signals(
    github_since="weekly",    # GitHub: weekly trending
    hn_limit=30,              # HN: top 30 stories
    devto_days=7,             # Dev.to: top this week
    arxiv_days=7,             # ArXiv: last 7 days
    max_results=10            # Return top 10 overall
)
```

**Flow**:
1. Fetch all sources in parallel (3-5s)
2. Filter to strategic signals
3. Score with heuristics
4. Sort by score
5. Return top N

---

## Performance

| Metric | Value |
| :--- | :--- |
| **Fetch time** | 3-5s (parallel) |
| **Success rate** | >90% |
| **Sources** | 4 (GitHub, HN, Dev.to, ArXiv) |
| **Cost** | $0 (all free APIs) |

---

## Error Handling

All fetches use `return_exceptions=True`:
```python
results = await asyncio.gather(
    fetch_github_trending(),
    fetch_hn_top_stories(),
    fetch_devto_top(),
    fetch_arxiv_recent(),
    return_exceptions=True  # Never crashes
)
```

If a source fails:
- ✅ Other sources continue
- ✅ Error is logged
- ✅ Empty list returned for failed source

---

## Testing

```bash
python -m side.intel.trending
```

**Output**:
```
ZERO-STORAGE TRENDING INTELLIGENCE
======================================================================

✅ Fetched 10 trending signals:

1. 🔥 username/repo-name... (github)
2. Show HN: My project... (hackernews)
3. Latest AI paper... (arxiv)
...
```

---

## API Reference

### `get_trending_signals(...) -> List[Dict]`

Fetch trending signals from all sources.

**Parameters**:
- `github_since` (str): "daily", "weekly", or "monthly"
- `hn_limit` (int): Max HN stories
- `devto_days` (int): Top articles from last N days
- `arxiv_days` (int): Papers from last N days
- `max_results` (int): Max signals to return

**Returns**: List of signal dicts

### `fetch_github_trending(since, language) -> List[Dict]`

Fetch trending GitHub repos.

### `fetch_hn_top_stories(limit) -> List[Dict]`

Fetch HN top stories.

### `fetch_devto_top(days) -> List[Dict]`

Fetch Dev.to top articles.

### `fetch_arxiv_recent(categories, days) -> List[Dict]`

Fetch recent ArXiv papers.

---

## Rate Limits

| Source | Limit | Auth Required |
| :--- | :--- | :--- |
| GitHub | 10 req/min | No |
| HackerNews | Unlimited | No |
| Dev.to | Unlimited | No |
| ArXiv | Unlimited | No |

All sources are free and don't require authentication.
