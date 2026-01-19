# Feed Registry
> Curated list of 200+ high-quality technical sources

---

## Purpose

Maintains a curated registry of RSS feeds from:
- **Technical Leaders** (80): Julia Evans, Martin Fowler, Dan Luu, etc.
- **Developer Tools** (40): Vercel, Supabase, GitHub, Cursor, etc.
- **VCs & Investors** (40): a16z, Y Combinator, Paul Graham, etc.
- **AI/ML Researchers** (20): Andrej Karpathy, Chip Huyen, etc.
- **Product Leaders** (20): Lenny Rachitsky, Stratechery, etc.

**Total**: 200 feeds (currently 86, expanding)

---

## Usage

```python
from side.intel.feed_registry import get_all_feeds, get_feeds_by_category

# Get all feeds
all_feeds = get_all_feeds()
print(f"Total feeds: {len(all_feeds)}")

# Get by category
technical = get_feeds_by_category("technical")
tools = get_feeds_by_category("tools")
investors = get_feeds_by_category("investors")
```

---

## Categories

### Technical Leaders (80 feeds)

**Systems & Infrastructure**:
- Julia Evans - https://jvns.ca/atom.xml
- Charity Majors - https://charity.wtf/feed/
- Dan Luu - https://danluu.com/atom.xml
- Martin Kleppmann - https://martin.kleppmann.com/rss.xml

**Frontend & Web**:
- Dan Abramov - https://overreacted.io/rss.xml
- Kent C. Dodds - https://kentcdodds.com/blog/rss.xml
- Josh W Comeau - https://www.joshwcomeau.com/rss.xml

**Backend & Architecture**:
- Martin Fowler - https://martinfowler.com/feed.atom
- Uncle Bob Martin - https://blog.cleancoder.com/atom.xml

**Security**:
- Troy Hunt - https://www.troyhunt.com/rss/
- Bruce Schneier - https://www.schneier.com/blog/atom.xml

---

### Developer Tools (40 feeds)

**Cloud & Infrastructure**:
- Vercel - https://vercel.com/blog/feed
- Cloudflare - https://blog.cloudflare.com/rss/
- Railway - https://blog.railway.app/rss.xml
- Fly.io - https://fly.io/blog/feed.xml

**Databases**:
- Supabase - https://supabase.com/blog/rss.xml
- PlanetScale - https://planetscale.com/blog/rss.xml
- Neon - https://neon.tech/blog/rss.xml

**AI/ML Tools**:
- OpenAI - https://openai.com/blog/rss/
- Anthropic - https://www.anthropic.com/news/rss.xml
- Hugging Face - https://huggingface.co/blog/feed.xml

---

### VCs & Investors (40 feeds)

**Top VCs**:
- a16z - https://a16z.com/feed/
- Y Combinator - https://www.ycombinator.com/blog/feed
- Sequoia Capital - https://www.sequoiacap.com/feed/

**Individual Investors**:
- Paul Graham - http://www.paulgraham.com/rss.html
- Sam Altman - https://blog.samaltman.com/posts.atom
- Packy McCormick - https://www.notboring.co/feed
- Lenny Rachitsky - https://www.lennysnewsletter.com/feed

---

### AI/ML Researchers (20 feeds)

- Andrej Karpathy - https://karpathy.github.io/feed.xml
- Chip Huyen - https://huyenchip.com/feed.xml
- Eugene Yan - https://eugeneyan.com/feed.xml
- Lilian Weng - https://lilianweng.github.io/feed.xml

---

## Feed Metadata

```python
FEED_METADATA = {
    "technical_weight": 0.8,  # 80% technical
    "investor_weight": 0.2,   # 20% investors/product
    "total_feeds": 200,
    "categories": {
        "technical": 80,
        "tools": 40,
        "investors": 40,
        "research": 20,
        "product": 20,
    }
}
```

---

## Quality Criteria

Feeds are selected based on:
- ✅ **Authority**: Recognized experts in their field
- ✅ **Consistency**: Regular publishing schedule
- ✅ **Quality**: High signal-to-noise ratio
- ✅ **Relevance**: Technical depth and insights
- ✅ **Accessibility**: Public RSS feed available

**Excluded**:
- ❌ Twitter/X (too noisy, no RSS)
- ❌ Low-quality aggregators
- ❌ Paywalled content without RSS
- ❌ Inactive blogs (>6 months)

---

## Adding New Feeds

To add a new feed:

1. Verify RSS feed is working
2. Categorize appropriately
3. Add to `feed_registry.py`:

```python
TECHNICAL_LEADERS = {
    # ...
    "New Author": "https://example.com/feed.xml",
}
```

---

## Testing

```bash
python -m side.intel.feed_registry
```

**Output**:
```
Total curated feeds: 86
Breakdown:
  Technical Leaders: 30
  Developer Tools: 25
  VCs & Investors: 17
  AI/ML Researchers: 8
  Product Leaders: 6
```

---

## Maintenance

Feeds are automatically validated by the RSS fetcher:
- Broken feeds (404, 410) are tracked and skipped
- Timeout feeds are retried with exponential backoff
- Permanently failed feeds are logged for review

See [RSS Fetcher](../rss/README.md) for error handling details.
