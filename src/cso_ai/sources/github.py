"""
GitHub Trending source for CSO.ai.

Fetches trending repositories from GitHub.
"""

import re
from datetime import datetime, timezone

import httpx

from cso_ai.intel.market import Article


class GitHubSource:
    """
    Fetches trending repositories from GitHub.

    Note: GitHub doesn't have an official trending API,
    so we scrape the trending page.
    """

    name = "github"
    TRENDING_URL = "https://github.com/trending"

    def __init__(self) -> None:
        """Initialize the source."""
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
                ),
            },
        )

    async def fetch(self, days: int = 7, limit: int = 25) -> list[Article]:
        """
        Fetch trending repositories.

        Args:
            days: Not used (trending is always recent)
            limit: Max repos to fetch

        Returns:
            List of articles (repos as articles)
        """
        articles = []

        for period in ["daily", "weekly"]:
            try:
                response = await self.client.get(
                    f"{self.TRENDING_URL}?since={period}"
                )
                response.raise_for_status()
                repos = self._parse_trending(response.text, period)
                articles.extend(repos)
            except Exception:
                continue

        # Deduplicate
        seen = set()
        unique = []
        for article in articles:
            if article.url not in seen:
                seen.add(article.url)
                unique.append(article)

        return unique[:limit]

    def _parse_trending(self, html: str, period: str) -> list[Article]:
        """Parse GitHub trending page."""
        articles = []

        # Extract repo patterns
        repo_pattern = re.compile(
            r'<h2 class="h3 lh-condensed">\s*<a href="(/[^"]+)"',
            re.DOTALL,
        )

        for match in repo_pattern.finditer(html):
            path = match.group(1).strip()
            repo_name = path.strip("/")
            url = f"https://github.com{path}"

            articles.append(
                Article(
                    id=f"github-{repo_name.replace('/', '-')}",
                    title=f"📦 {repo_name}",
                    url=url,
                    source=self.name,
                    published_at=datetime.now(timezone.utc),
                    tags=[f"trending-{period}"],
                )
            )

        return articles

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
