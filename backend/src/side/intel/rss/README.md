# Error-Resilient RSS Fetcher
> Never fails, always returns fresh content

---

## Purpose

Fetches RSS feeds from 200+ sources with built-in resilience:
- **Never crashes** - silently skips broken feeds
- **Automatic retries** - 3 attempts with exponential backoff
- **Timeout protection** - 5s per feed
- **Parallel fetching** - 50 feeds at once
- **Tracks failures** - permanently failed feeds are skipped

---

## Usage

```python
from side.intel.rss_fetcher import ResilientRSSFetcher

fetcher = ResilientRSSFetcher()

# Fetch from specific feeds
feeds = {
    "Julia Evans": "https://jvns.ca/atom.xml",
    "Dan Luu": "https://danluu.com/atom.xml",
}

articles = await fetcher.fetch_all(feeds, max_articles_per_feed=5)
```

---

## Features

### 1. Silent Error Handling

```python
# Even if some feeds fail, you get results
articles = await fetcher.fetch_all(feeds)

# Broken feeds are logged but don't crash
# ✅ Fetched from 4/5 feeds (1 failed)
# ✅ Returns articles from successful feeds
```

### 2. Automatic Retries

```python
# Retries with exponential backoff
for attempt in range(3):
    try:
        response = await client.get(url)
        break
    except TimeoutException:
        await asyncio.sleep(0.5 * (attempt + 1))
```

### 3. Parallel Fetching

```python
# Fetch 50 feeds at once with semaphore
semaphore = asyncio.Semaphore(50)

async def fetch_with_semaphore(name, url):
    async with semaphore:
        return await fetch_feed(name, url)

results = await asyncio.gather(*tasks)
```

### 4. Failure Tracking

```python
# Permanently failed feeds are tracked
self.failed_feeds = set()

# 404/410 errors → permanent failure
if status_code in [404, 410]:
    self.failed_feeds.add(url)
    
# Skip on next fetch
if url in self.failed_feeds:
    return FeedResult(success=False, articles=[])
```

---

## Examples

### Example 1: Fetch from All Feeds

```python
from side.intel.feed_registry import get_all_feeds

fetcher = ResilientRSSFetcher()
all_feeds = get_all_feeds()

articles = await fetcher.fetch_all(all_feeds, max_articles_per_feed=3)

print(f"Fetched {len(articles)} articles")
# Fetched 250 articles from 86 feeds
```

### Example 2: Fetch by Category

```python
articles = await fetcher.fetch_category("technical", max_articles_per_feed=5)

for article in articles[:5]:
    print(f"• {article['title']}")
    print(f"  Source: {article['source']}")
```

### Example 3: Quick Fetch (Top 50 Feeds)

```python
# Faster - only top 50 feeds
articles = await fetcher.fetch_top_sources(
    max_articles_per_feed=3,
    limit_feeds=50
)

# Returns in ~5s instead of ~15s
```

---

## Configuration

```python
fetcher = ResilientRSSFetcher(
    timeout=5.0,        # Timeout per feed
    max_retries=2,      # Retry attempts
    max_concurrent=50   # Parallel fetches
)
```

---

## Error Handling

### Error Types

| Error | Handling | Result |
| :--- | :--- | :--- |
| **Timeout** | Retry 3x, then skip | Empty articles |
| **404/410** | Mark as permanent failure | Skip forever |
| **Network** | Retry 3x, then skip | Empty articles |
| **Parse** | Log and skip entry | Continue with others |

### Example Output

```
Testing with 5 feeds...
Martin Kleppmann: HTTP 404
✅ Fetched 8 articles from 4/5 feeds
```

**No errors shown to user** - system continues gracefully.

---

## Feed Result Format

```python
@dataclass
class FeedResult:
    source_name: str
    url: str
    success: bool
    articles: List[Dict[str, Any]]
    error: Optional[str] = None
    fetch_time_ms: int = 0
```

### Article Format

```python
{
    'id': 'rss-Julia Evans-12345',
    'title': 'How DNS works',
    'description': 'A deep dive into DNS...',
    'url': 'https://jvns.ca/blog/dns',
    'source': 'Julia Evans',
    'published_at': '2026-01-18T10:00:00Z',
    'metadata': {
        'author': 'Julia Evans',
        'tags': ['networking', 'dns']
    }
}
```

---

## Performance

| Metric | Value |
| :--- | :--- |
| **Fetch time** | 5-15s (50-200 feeds) |
| **Success rate** | 80-90% |
| **Timeout** | 5s per feed |
| **Concurrent** | 50 feeds at once |
| **Retries** | 3 attempts |

---

## Testing

```bash
python -m side.intel.rss_fetcher
```

**Output**:
```
RESILIENT RSS FETCHER TEST
======================================================================

Fetching from 20 feeds...

✅ Fetched 45 articles

1. A data model for Git... (Julia Evans)
2. On Friday Deploys... (Charity Majors)
...

======================================================================
✅ Resilient fetcher working - no errors!
```

---

## API Reference

### `ResilientRSSFetcher(timeout, max_retries, max_concurrent)`

Create a new fetcher instance.

### `fetch_feed(name, url, max_articles) -> FeedResult`

Fetch a single RSS feed.

**Returns**: `FeedResult` (always succeeds, may have empty articles)

### `fetch_all(feeds, max_articles_per_feed) -> List[Dict]`

Fetch from all feeds in parallel.

**Returns**: List of all articles from successful feeds

### `fetch_category(category, max_articles_per_feed) -> List[Dict]`

Fetch from a specific category of feeds.

### `fetch_top_sources(max_articles_per_feed, limit_feeds) -> List[Dict]`

Fetch from top N sources only (faster).

---

## Convenience Functions

```python
from side.intel.rss_fetcher import get_fresh_content

# Quick way to get fresh content
articles = await get_fresh_content(
    category="technical",  # Optional
    max_articles=100
)
```

---

## Dependencies

- `httpx`: Async HTTP client
- `feedparser`: RSS/Atom parsing
- `asyncio`: Parallel fetching

---

## See Also

- [Feed Registry](../feeds/README.md) - Curated feed list
- [Trending APIs](../trending/README.md) - Alternative to RSS
- [Unified API](../api/README.md) - Main interface
