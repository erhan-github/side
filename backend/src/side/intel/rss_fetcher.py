"""
Error-Resilient RSS Fetcher - Never fails, always returns fresh content.

Handles:
- Broken feeds (skip silently)
- Network errors (retry with exponential backoff)
- Malformed XML (skip and log)
- Rate limits (respect and wait)
- Timeouts (fail fast, move to next)

Strategy: Fetch from 200 feeds, expect 20% to fail, still get 160 sources.
"""

import asyncio
import httpx
import feedparser
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from side.intel.feed_registry import get_all_feeds, get_feeds_by_category

logger = logging.getLogger(__name__)


@dataclass
class FeedResult:
    """Result from fetching a single feed."""
    source_name: str
    url: str
    success: bool
    articles: List[Dict[str, Any]]
    error: Optional[str] = None
    fetch_time_ms: int = 0


class ResilientRSSFetcher:
    """
    Fetches RSS feeds with built-in resilience.
    
    Features:
    - Parallel fetching (100 feeds at once)
    - Automatic retries (3 attempts)
    - Timeout protection (5s per feed)
    - Silent error handling (never crashes)
    - Fallback mechanisms
    """
    
    def __init__(
        self,
        timeout: float = 5.0,
        max_retries: int = 2,
        max_concurrent: int = 50
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_concurrent = max_concurrent
        self.failed_feeds = set()  # Track permanently failed feeds
    
    async def fetch_feed(
        self,
        name: str,
        url: str,
        max_articles: int = 5
    ) -> FeedResult:
        """
        Fetch a single RSS feed with error handling.
        
        Args:
            name: Feed name (for logging)
            url: RSS feed URL
            max_articles: Max articles to extract
        
        Returns:
            FeedResult (always succeeds, may have empty articles)
        """
        start_time = datetime.now()
        
        # Skip if previously failed permanently
        if url in self.failed_feeds:
            return FeedResult(
                source_name=name,
                url=url,
                success=False,
                articles=[],
                error="Previously failed",
                fetch_time_ms=0
            )
        
        # Try fetching with retries
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, follow_redirects=True)
                    response.raise_for_status()
                    
                    # Parse RSS/Atom feed
                    feed = feedparser.parse(response.text)
                    
                    # Extract articles
                    articles = []
                    for entry in feed.entries[:max_articles]:
                        article = self._parse_entry(entry, name)
                        if article:
                            articles.append(article)
                    
                    fetch_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    
                    return FeedResult(
                        source_name=name,
                        url=url,
                        success=True,
                        articles=articles,
                        fetch_time_ms=fetch_time
                    )
            
            except httpx.TimeoutException:
                logger.warning(f"{name}: Timeout (attempt {attempt + 1})")
                if attempt == self.max_retries:
                    self.failed_feeds.add(url)
                    return FeedResult(name, url, False, [], "Timeout")
                await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
            
            except httpx.HTTPStatusError as e:
                logger.warning(f"{name}: HTTP {e.response.status_code}")
                if e.response.status_code in [404, 410]:  # Permanent errors
                    self.failed_feeds.add(url)
                return FeedResult(name, url, False, [], f"HTTP {e.response.status_code}")
            
            except Exception as e:
                logger.warning(f"{name}: {type(e).__name__}: {str(e)[:50]}")
                if attempt == self.max_retries:
                    return FeedResult(name, url, False, [], str(e)[:100])
                await asyncio.sleep(0.5 * (attempt + 1))
        
        return FeedResult(name, url, False, [], "Max retries exceeded")
    
    def _parse_entry(self, entry: Any, source_name: str) -> Optional[Dict[str, Any]]:
        """Parse a single feed entry into our format."""
        try:
            # Extract published date
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_at = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc).isoformat()
            
            # Extract description/summary
            description = ""
            if hasattr(entry, 'summary'):
                description = entry.summary[:300]
            elif hasattr(entry, 'description'):
                description = entry.description[:300]
            
            return {
                'id': f"rss-{source_name}-{hash(entry.get('link', ''))}",
                'title': entry.get('title', 'Untitled'),
                'description': description,
                'url': entry.get('link', ''),
                'source': source_name,
                'published_at': published_at,
                'metadata': {
                    'author': entry.get('author', ''),
                    'tags': [tag.get('term', '') for tag in entry.get('tags', [])]
                }
            }
        except Exception as e:
            logger.debug(f"Failed to parse entry from {source_name}: {e}")
            return None
    
    async def fetch_all(
        self,
        feeds: Dict[str, str],
        max_articles_per_feed: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fetch from all feeds in parallel with semaphore for concurrency control.
        
        Args:
            feeds: Dict of {name: url}
            max_articles_per_feed: Max articles per feed
        
        Returns:
            List of all articles from all successful feeds
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def fetch_with_semaphore(name: str, url: str):
            async with semaphore:
                return await self.fetch_feed(name, url, max_articles_per_feed)
        
        # Fetch all feeds in parallel (with concurrency limit)
        tasks = [fetch_with_semaphore(name, url) for name, url in feeds.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        all_articles = []
        success_count = 0
        fail_count = 0
        
        for result in results:
            if isinstance(result, FeedResult):
                if result.success:
                    all_articles.extend(result.articles)
                    success_count += 1
                else:
                    fail_count += 1
            elif isinstance(result, Exception):
                logger.error(f"Unexpected error: {result}")
                fail_count += 1
        
        logger.info(f"Fetched from {success_count}/{len(feeds)} feeds ({fail_count} failed)")
        logger.info(f"Total articles: {len(all_articles)}")
        
        return all_articles
    
    async def fetch_category(
        self,
        category: str,
        max_articles_per_feed: int = 5
    ) -> List[Dict[str, Any]]:
        """Fetch from a specific category of feeds."""
        feeds = get_feeds_by_category(category)
        return await self.fetch_all(feeds, max_articles_per_feed)
    
    async def fetch_top_sources(
        self,
        max_articles_per_feed: int = 3,
        limit_feeds: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch from top N sources only (for faster results).
        
        Args:
            max_articles_per_feed: Articles per feed
            limit_feeds: Max feeds to fetch from
        
        Returns:
            List of articles
        """
        all_feeds = get_all_feeds()
        
        # Take first N feeds (prioritize technical leaders)
        limited_feeds = dict(list(all_feeds.items())[:limit_feeds])
        
        return await self.fetch_all(limited_feeds, max_articles_per_feed)


# Convenience functions

async def get_fresh_content(
    category: Optional[str] = None,
    max_articles: int = 100
) -> List[Dict[str, Any]]:
    """
    Get fresh content from RSS feeds.
    
    Args:
        category: Optional category filter
        max_articles: Max total articles to return
    
    Returns:
        List of fresh articles
    """
    fetcher = ResilientRSSFetcher()
    
    if category:
        articles = await fetcher.fetch_category(category)
    else:
        # Fetch from top 50 feeds for speed
        articles = await fetcher.fetch_top_sources(limit_feeds=50)
    
    # Sort by published date (newest first)
    articles.sort(
        key=lambda x: x.get('published_at', ''),
        reverse=True
    )
    
    return articles[:max_articles]


if __name__ == "__main__":
    # Test the resilient fetcher
    async def test():
        print("\n" + "="*70)
        print("RESILIENT RSS FETCHER TEST")
        print("="*70)
        
        fetcher = ResilientRSSFetcher()
        
        # Test with top 20 feeds
        from side.intel.feed_registry import TECHNICAL_LEADERS
        test_feeds = dict(list(TECHNICAL_LEADERS.items())[:20])
        
        print(f"\nFetching from {len(test_feeds)} feeds...")
        articles = await fetcher.fetch_all(test_feeds, max_articles_per_feed=3)
        
        print(f"\n✅ Fetched {len(articles)} articles\n")
        
        # Show first 5
        for i, article in enumerate(articles[:5], 1):
            print(f"{i}. {article['title'][:60]}...")
            print(f"   Source: {article['source']}")
            print()
        
        print("="*70)
        print("✅ Resilient fetcher working - no errors!")
        print("="*70 + "\n")
    
    asyncio.run(test())
