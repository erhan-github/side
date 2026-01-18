"""
CSO.ai Signal Aggregator - The "Deep Market" Fetcher.

Fetches high-signal intelligence for specific business domains.
Sources are carefully curated to ensure relevance (no noise).

Architecture:
- DomainSources: Static registry of high-quality RSS feeds per domain.
- SignalAggregator: Async fetcher that normalizes feeds into generic Signals.
"""

import asyncio
import feedparser
import httpx
from datetime import datetime, timezone
import logging
from typing import Any

logger = logging.getLogger("cso_ai.intel.signals")

class DomainSources:
    """Registry of high-quality sources."""
    
    # Curated sources (Palantir-level quality)
    SOURCES = {
        "EdTech": [
            {"url": "https://www.edsurge.com/articles_rss", "name": "EdSurge"},
            # TechCrunch EdTech feed is flaky/404s often
            # THE Journal redirects/fails
        ],
        "FinTech": [
            {"url": "https://techcrunch.com/category/fintech/feed/", "name": "TechCrunch FinTech"},
            {"url": "https://www.finextra.com/rss/headlines.aspx", "name": "Finextra"},
            {"url": "https://cointelegraph.com/rss", "name": "CoinTelegraph"},
        ],
        "Health": [
            {"url": "https://mobihealthnews.com/feed", "name": "MobiHealthNews"},
            {"url": "https://techcrunch.com/category/biotech-health/feed/", "name": "TechCrunch Health"},
        ],
        "SaaS": [
            {"url": "https://www.saastr.com/feed/", "name": "SaaStr"},
            {"url": "https://techcrunch.com/category/enterprise/feed/", "name": "TechCrunch Enterprise"},
        ],
        "DevTool": [
            {"url": "https://news.ycombinator.com/rss", "name": "Hacker News"},
            {"url": "https://dev.to/feed", "name": "Dev.to"},
        ],
        "General Software": [
             {"url": "https://news.ycombinator.com/rss", "name": "Hacker News"},
        ]
    }

    @classmethod
    def get_sources(cls, domain: str) -> list[dict[str, str]]:
        return cls.SOURCES.get(domain, cls.SOURCES["General Software"])


class SignalAggregator:
    """Fetches and normalizes market signals."""

    async def fetch_signals(self, domain: str) -> list[dict[str, Any]]:
        """
        Fetch top signals for a domain.
        
        Returns:
            List of normalized signals:
            [
                {
                    "title": "New LMS Standard Released",
                    "url": "...",
                    "source": "EdSurge",
                    "domain": "EdTech",
                    "published_at": "...",
                    "description": "..."
                },
                ...
            ]
        """
        sources = DomainSources.get_sources(domain)
        tasks = [self._fetch_feed(s, domain) for s in sources]
        
        # Run all fetches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_signals = []
        for res in results:
            if isinstance(res, list):
                all_signals.extend(res)
                
        # Sort by date (newest first)
        all_signals.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        return all_signals[:15]  # Return top 15

    async def _fetch_feed(self, source: dict, domain: str) -> list[dict[str, Any]]:
        """Fetch and parse a single RSS feed."""
        try:
            # We use httpx for async fetching, then pass string to feedparser
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(source["url"])
                response.raise_for_status()
                
            feed = feedparser.parse(response.text)
            signals = []
            
            for entry in feed.entries[:5]:  # Top 5 per source
                # Normalize date
                pub_date = datetime.now(timezone.utc).isoformat()
                if hasattr(entry, "published"):
                    pub_date = entry.published
                
                signals.append({
                    "title": entry.title,
                    "url": entry.link,
                    "source": source["name"],
                    "domain": domain,
                    "published_at": pub_date,
                    "description": self._clean_description(entry.get("summary", "")),
                })
            
            return signals
        except Exception as e:
            logger.warning(f"Failed to fetch {source['name']}: {e}")
            return []

    def _clean_description(self, html_text: str) -> str:
        """Remove HTML tags from description."""
        import re
        clean = re.sub(r'<[^>]+>', '', html_text)
        return clean[:300].strip() + "..."
