"""
GitHub Trending source for Side.

Fetches trending repositories from GitHub.
"""

import re
from datetime import datetime, timezone

from side.intel.market import Article
from side.utils import ResilientHTTPClient


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
        # Note: ResilientHTTPClient doesn't support custom headers in __init__
        # We'll pass them in each request
        self.client = ResilientHTTPClient(timeout=30.0, max_retries=3)
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def fetch(self, days: int = 7, limit: int = 25) -> list[Article]:
        """
        Fetch trending repositories IN PARALLEL.

        Args:
            days: Not used (trending is always recent)
            limit: Max repos to fetch

        Returns:
            List of articles (repos as articles)
        """
        import asyncio
        
        async def fetch_period(period: str) -> list[Article]:
            try:
                html = await self.client.get_text(
                    f"{self.TRENDING_URL}?since={period}",
                    headers=self.headers,
                )
                return self._parse_trending(html, period)
            except Exception as e:
                print(f"GitHub fetch error: {e}")
                return []
        
        # Fetch daily and weekly in parallel
        results = await asyncio.gather(
            fetch_period("daily"),
            fetch_period("weekly"),
            return_exceptions=True
        )
        
        # Flatten results
        articles = []
        for result in results:
            if isinstance(result, list):
                articles.extend(result)

        # Deduplicate
        seen = set()
        unique = []
        for article in articles:
            if article.url not in seen:
                seen.add(article.url)
                unique.append(article)

        return unique[:limit]

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.close()

    def _parse_trending(self, html: str, period: str) -> list[Article]:
        """Parse GitHub trending page."""
        articles = []

        # Find all repo links - pattern: href="/owner/repo"
        # Exclude special paths like /apps/, /trending/, /explore/, etc.
        repo_pattern = re.compile(
            r'href="/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)"',
        )

        # Track found repos to avoid duplicates within this parse
        found_repos = set()

        # Paths to exclude
        excluded_prefixes = {
            "apps", "trending", "explore", "topics", "collections",
            "events", "sponsors", "settings", "features", "security",
            "enterprise", "team", "pricing", "login", "signup",
            "about", "contact", "privacy", "terms", "site",
        }

        for match in repo_pattern.finditer(html):
            owner = match.group(1)
            repo = match.group(2)

            # Skip excluded prefixes
            if owner.lower() in excluded_prefixes:
                continue

            # Skip if owner looks like a special page
            if owner.startswith("_") or repo.startswith("."):
                continue

            repo_full = f"{owner}/{repo}"

            # Skip duplicates
            if repo_full in found_repos:
                continue

            found_repos.add(repo_full)
            url = f"https://github.com/{repo_full}"

            # Try to extract description from nearby text
            desc = self._extract_description(html, repo_full)

            articles.append(
                Article(
                    id=f"github-{owner}-{repo}",
                    title=f"🔥 {repo_full}",
                    url=url,
                    source=self.name,
                    description=desc,
                    published_at=datetime.now(timezone.utc),
                    tags=[f"trending-{period}", "github", "open-source"],
                )
            )

        return articles

    def _extract_description(self, html: str, repo_full: str) -> str | None:
        """Try to extract repo description from HTML."""
        # Look for description near the repo link
        # GitHub often has: <p class="...">description</p>
        try:
            # Find the repo in HTML and look for nearby paragraph
            idx = html.find(repo_full)
            if idx > 0:
                # Look in the next 500 chars for a paragraph
                snippet = html[idx:idx + 500]
                p_match = re.search(r'<p[^>]*>([^<]{10,200})</p>', snippet)
                if p_match:
                    desc = p_match.group(1).strip()
                    # Clean up HTML entities
                    desc = desc.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                    return desc
        except Exception:
            pass
        return None
