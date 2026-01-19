"""
Zero-Storage Trending Intelligence.

Fetches trending signals directly from sources' built-in trending APIs.
NO database storage - always fresh, always real-time.
"""

import asyncio
import httpx
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from typing import Any
import logging

from side.intel.text_analysis import filter_strategic_articles

logger = logging.getLogger(__name__)


async def fetch_github_trending(
    since: str = "weekly",
    language: str = None
) -> list[dict[str, Any]]:
    """
    Fetch trending repos from GitHub.
    
    Uses GitHub Search API (no auth needed, 10 req/min free).
    
    Args:
        since: "daily", "weekly", or "monthly"
        language: Optional language filter
    
    Returns:
        List of trending repo dicts
    """
    # Calculate date range
    days_map = {"daily": 1, "weekly": 7, "monthly": 30}
    days = days_map.get(since, 7)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # Build query
    query = f"created:>{cutoff}"
    if language:
        query += f" language:{language}"
    
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=20"
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        
        repos = []
        for item in data.get('items', [])[:20]:
            repos.append({
                'id': f"github-{item['id']}",
                'title': f"🔥 {item['full_name']}",
                'description': item.get('description', ''),
                'url': item['html_url'],
                'source': 'github',
                'published_at': item.get('created_at'),
                'metadata': {
                    'stars': item.get('stargazers_count', 0),
                    'language': item.get('language'),
                    'trending_period': since
                }
            })
        
        return repos


async def fetch_hn_top_stories(limit: int = 30) -> list[dict[str, Any]]:
    """
    Fetch top stories from HackerNews.
    
    Uses HN Firebase API (free, unlimited).
    
    Args:
        limit: Max stories to fetch
    
    Returns:
        List of top story dicts
    """
    base_url = "https://hacker-news.firebaseio.com/v0"
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        # Get top story IDs
        response = await client.get(f"{base_url}/topstories.json")
        story_ids = response.json()[:limit]
        
        # Fetch stories in parallel
        async def fetch_story(story_id: int):
            try:
                resp = await client.get(f"{base_url}/item/{story_id}.json")
                return resp.json()
            except Exception:
                return None
        
        stories = await asyncio.gather(*[fetch_story(sid) for sid in story_ids])
        
        # Convert to our format
        results = []
        for story in stories:
            if story and story.get('type') == 'story':
                results.append({
                    'id': f"hn-{story['id']}",
                    'title': story.get('title', ''),
                    'description': story.get('text', '')[:200] if story.get('text') else '',
                    'url': story.get('url', f"https://news.ycombinator.com/item?id={story['id']}"),
                    'source': 'hackernews',
                    'published_at': datetime.fromtimestamp(story.get('time', 0), tz=timezone.utc).isoformat(),
                    'metadata': {
                        'score': story.get('score', 0),
                        'comments': story.get('descendants', 0)
                    }
                })
        
        return results


async def fetch_devto_top(days: int = 7) -> list[dict[str, Any]]:
    """
    Fetch top articles from Dev.to.
    
    Uses Dev.to API (free, no auth needed).
    
    Args:
        days: Top articles from last N days
    
    Returns:
        List of top article dicts
    """
    url = f"https://dev.to/api/articles?top={days}&per_page=20"
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        articles = response.json()
        
        results = []
        for article in articles:
            results.append({
                'id': f"devto-{article['id']}",
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'source': 'devto',
                'published_at': article.get('published_at'),
                'metadata': {
                    'reactions': article.get('public_reactions_count', 0),
                    'comments': article.get('comments_count', 0),
                    'tags': article.get('tag_list', [])
                }
            })
        
        return results


async def fetch_arxiv_recent(
    categories: str = "cs.AI+cs.LG+cs.CL",
    days: int = 7,
    max_results: int = 30
) -> list[dict[str, Any]]:
    """
    Fetch recent papers from ArXiv.
    
    Uses ArXiv API (free, unlimited).
    
    Args:
        categories: ArXiv categories
        days: Papers from last N days
        max_results: Max papers to fetch
    
    Returns:
        List of recent paper dicts
    """
    url = f"https://export.arxiv.org/api/query?search_query=cat:{categories}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        papers = []
        for entry in root.findall('atom:entry', ns):
            published_elem = entry.find('atom:published', ns)
            if published_elem is not None:
                published = datetime.fromisoformat(published_elem.text.replace('Z', '+00:00'))
                
                # Only include recent papers
                if published < cutoff:
                    continue
            
            title = entry.find('atom:title', ns)
            summary = entry.find('atom:summary', ns)
            link = entry.find('atom:id', ns)
            
            if title is not None and link is not None:
                papers.append({
                    'id': f"arxiv-{link.text.split('/')[-1]}",
                    'title': title.text.strip().replace('\n', ' '),
                    'description': summary.text.strip().replace('\n', ' ')[:200] if summary is not None else '',
                    'url': link.text,
                    'source': 'arxiv',
                    'published_at': published_elem.text if published_elem is not None else None
                })
        
        return papers


async def get_trending_signals(
    github_since: str = "weekly",
    hn_limit: int = 30,
    devto_days: int = 7,
    arxiv_days: int = 7,
    max_results: int = 10
) -> list[dict[str, Any]]:
    """
    Fetch trending signals from all sources.
    
    This is the MAIN function - fetches everything in parallel.
    NO storage, always fresh.
    
    Args:
        github_since: "daily", "weekly", or "monthly"
        hn_limit: Max HN stories
        devto_days: Top Dev.to articles from last N days
        arxiv_days: ArXiv papers from last N days
        max_results: Max signals to return
    
    Returns:
        Top N trending signals across all sources
    """
    logger.info("Fetching trending signals from all sources...")
    
    # Fetch all sources in parallel
    results = await asyncio.gather(
        fetch_github_trending(since=github_since),
        fetch_hn_top_stories(limit=hn_limit),
        fetch_devto_top(days=devto_days),
        fetch_arxiv_recent(days=arxiv_days),
        return_exceptions=True
    )
    
    # Combine all signals
    all_signals = []
    for result in results:
        if isinstance(result, list):
            all_signals.extend(result)
        elif isinstance(result, Exception):
            logger.error(f"Source fetch failed: {result}")
    
    logger.info(f"Fetched {len(all_signals)} total signals")
    
    # Filter to strategic signals
    strategic = filter_strategic_articles(all_signals, max_results=max_results * 2)
    
    # Sort by heuristic score and take top N
    from side.intel.text_analysis import score_article_heuristic
    for signal in strategic:
        if 'score' not in signal:
            signal['score'] = score_article_heuristic(signal)
    
    strategic.sort(key=lambda x: x.get('score', 0), reverse=True)
    top_signals = strategic[:max_results]
    
    logger.info(f"Filtered to {len(top_signals)} strategic signals")
    
    return top_signals


# Convenience functions for specific use cases

async def get_trending_repos(language: str = None) -> list[dict[str, Any]]:
    """Get trending GitHub repos."""
    return await fetch_github_trending(since="weekly", language=language)


async def get_trending_discussions() -> list[dict[str, Any]]:
    """Get trending HN discussions."""
    return await fetch_hn_top_stories(limit=20)


async def get_trending_articles() -> list[dict[str, Any]]:
    """Get trending Dev.to articles."""
    return await fetch_devto_top(days=7)


async def get_latest_research() -> list[dict[str, Any]]:
    """Get latest AI/ML research papers."""
    return await fetch_arxiv_recent(days=7)


if __name__ == "__main__":
    # Test the zero-storage fetcher
    async def test():
        print("\n" + "="*70)
        print("ZERO-STORAGE TRENDING INTELLIGENCE")
        print("="*70)
        
        signals = await get_trending_signals(max_results=10)
        
        print(f"\n✅ Fetched {len(signals)} trending signals:\n")
        
        for i, signal in enumerate(signals, 1):
            print(f"{i}. {signal['title'][:65]}...")
            print(f"   Source: {signal['source']} | Score: {signal.get('score', 0)}/100")
            if signal.get('category'):
                print(f"   Category: {signal['category']}")
            print()
        
        print("="*70)
        print("✅ All data fetched on-demand, zero storage!")
        print("="*70 + "\n")
    
    asyncio.run(test())
