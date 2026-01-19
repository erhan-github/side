"""
Hacker News source for Side.

Fetches top stories from the HN API.
"""

from datetime import datetime, timezone

from side.intel.market import Article
from side.utils import ResilientHTTPClient


class HackerNewsSource:
    """
    Fetches articles from Hacker News.

    Uses the official Firebase API:
    https://hacker-news.firebaseio.com/v0/
    """

    name = "hackernews"
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    HN_ITEM_URL = "https://news.ycombinator.com/item?id="

    def __init__(self) -> None:
        """Initialize the source."""
        self.client = ResilientHTTPClient(timeout=30.0, max_retries=3)

    async def fetch(self, days: int = 7, limit: int = 50) -> list[Article]:
        """
        Fetch top stories from Hacker News IN PARALLEL.

        Args:
            days: Days to look back
            limit: Max stories to fetch

        Returns:
            List of articles
        """
        import asyncio
        
        # Get top story IDs (with retry logic)
        story_ids: list[int] = await self.client.get_json(f"{self.BASE_URL}/topstories.json")

        # Fetch story details in parallel
        async def fetch_and_filter(story_id: int) -> Article | None:
            try:
                article = await self._fetch_story(story_id)
                if article:
                    # Filter by date
                    if article.published_at:
                        age = (datetime.now(timezone.utc) - article.published_at).days
                        if age <= days:
                            return article
                    else:
                        return article
                return None
            except Exception:
                return None

        # Fetch all stories in parallel (limit concurrency to avoid overwhelming API)
        results = await asyncio.gather(
            *[fetch_and_filter(story_id) for story_id in story_ids[:limit]],
            return_exceptions=True
        )

        # Filter out None and exceptions
        articles = [r for r in results if isinstance(r, Article)]
        return articles

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.close()

    async def _fetch_story(self, story_id: int) -> Article | None:
        """Fetch a single story."""
        data = await self.client.get_json(f"{self.BASE_URL}/item/{story_id}.json")

        if not data or data.get("type") != "story":
            return None

        url = data.get("url", f"{self.HN_ITEM_URL}{story_id}")

        return Article(
            id=f"hn-{story_id}",
            title=data.get("title", ""),
            url=url,
            source=self.name,
            author=data.get("by"),
            score=data.get("score"),
            published_at=(
                datetime.fromtimestamp(data["time"], tz=timezone.utc)
                if data.get("time")
                else None
            ),
        )
