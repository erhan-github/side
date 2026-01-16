"""
Hacker News source for CSO.ai.

Fetches top stories from the HN API.
"""

from datetime import datetime, timezone

import httpx

from cso_ai.intel.market import Article


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
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch(self, days: int = 7, limit: int = 50) -> list[Article]:
        """
        Fetch top stories from Hacker News.

        Args:
            days: Days to look back
            limit: Max stories to fetch

        Returns:
            List of articles
        """
        # Get top story IDs
        response = await self.client.get(f"{self.BASE_URL}/topstories.json")
        response.raise_for_status()
        story_ids: list[int] = response.json()

        # Fetch story details
        articles = []
        for story_id in story_ids[:limit]:
            try:
                article = await self._fetch_story(story_id)
                if article:
                    # Filter by date
                    if article.published_at:
                        age = (datetime.now(timezone.utc) - article.published_at).days
                        if age <= days:
                            articles.append(article)
                    else:
                        articles.append(article)
            except Exception:
                continue

        return articles

    async def _fetch_story(self, story_id: int) -> Article | None:
        """Fetch a single story."""
        response = await self.client.get(f"{self.BASE_URL}/item/{story_id}.json")
        response.raise_for_status()
        data = response.json()

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

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
