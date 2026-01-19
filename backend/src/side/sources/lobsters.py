"""
Lobste.rs source for Side.

Fetches articles from the Lobsters RSS feed.
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from side.intel.market import Article
from side.utils import ResilientHTTPClient


class LobstersSource:
    """
    Fetches articles from Lobste.rs.

    Uses the RSS feed:
    https://lobste.rs/rss
    """

    name = "lobsters"
    RSS_URL = "https://lobste.rs/rss"

    def __init__(self) -> None:
        """Initialize the source."""
        self.client = ResilientHTTPClient(timeout=30.0, max_retries=3)

    async def fetch(self, days: int = 7, limit: int = 50) -> list[Article]:
        """
        Fetch articles from Lobsters RSS.

        Args:
            days: Days to look back
            limit: Max articles to fetch

        Returns:
            List of articles
        """
        xml_content = await self.client.get_text(self.RSS_URL)

        articles = self._parse_rss(xml_content)

        # Filter by date
        cutoff = datetime.now(timezone.utc)
        filtered = []
        for article in articles:
            if article.published_at:
                age = (cutoff - article.published_at).days
                if age <= days:
                    filtered.append(article)
            else:
                filtered.append(article)

        return filtered[:limit]

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.close()

    def _parse_rss(self, xml_content: str) -> list[Article]:
        """Parse RSS XML into articles."""
        articles = []

        try:
            root = ET.fromstring(xml_content)

            for item in root.findall(".//item"):
                article = self._parse_item(item)
                if article:
                    articles.append(article)
        except ET.ParseError:
            pass

        return articles

    def _parse_item(self, item: ET.Element) -> Article | None:
        """Parse a single RSS item."""
        title = item.findtext("title")
        link = item.findtext("link")

        if not title or not link:
            return None

        guid = item.findtext("guid", link)
        article_id = f"lobsters-{hash(guid) & 0xFFFFFFFF}"

        # Parse date
        pub_date_str = item.findtext("pubDate")
        published_at = None
        if pub_date_str:
            try:
                published_at = parsedate_to_datetime(pub_date_str)
            except (ValueError, TypeError):
                pass

        # Get tags
        tags = [cat.text for cat in item.findall("category") if cat.text]

        return Article(
            id=article_id,
            title=title,
            url=link,
            source=self.name,
            description=item.findtext("description"),
            author=item.findtext("{http://purl.org/dc/elements/1.1/}creator"),
            published_at=published_at,
            tags=tags,
        )
