
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

import httpx

from side.intel.sources.base import DomainType, IntelligenceItem, SourcePlugin


class LegalHubPlugin(SourcePlugin):
    """Fetches legal intelligence from curated RSS feeds."""
    
    # RSS Feeds for high-signal legal tech news
    FEEDS = [
        # Example feeds - in prod these would be verified URLs
        "https://feeds.feedburner.com/TechCrunch/startups", # Often covers regulation
        "https://law.justia.com/news/feeds/intellectual-property.xml", # IP Law
    ]
    
    # Keywords to filter relevance for developers
    KEYWORDS = [
        "artificial intelligence", "ai regulation", "gdpr", "open source",
        "licensing", "copyright", "patent", "privacy", "compliance",
        "eu act", "ftc", "sec"
    ]

    @property
    def name(self) -> str:
        return "Legal Intelligence Hub"
        
    @property
    def domain(self) -> DomainType:
        return "legal"
    
    async def fetch(self, limit: int = 5) -> list[IntelligenceItem]:
        """Fetch and filter legal news."""
        items = []
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for feed_url in self.FEEDS:
                try:
                    response = await client.get(feed_url)
                    if response.status_code == 200:
                        feed_items = self._parse_rss(response.text, source_url=feed_url)
                        items.extend(feed_items)
                except Exception as e:
                    print(f"Error fetching legal feed {feed_url}: {e}")
                    
        # Filter for relevance
        relevant_items = self._filter_relevance(items)
        
        # Sort by date
        relevant_items.sort(key=lambda x: x.published_at or datetime.min, reverse=True)
        return relevant_items[:limit]
        
    def _parse_rss(self, xml_content: str, source_url: str) -> list[IntelligenceItem]:
        """Parse RSS XML into IntelligenceItems."""
        items = []
        try:
            root = ET.fromstring(xml_content)
            
            # Handle standard RSS 2.0
            for item in root.findall(".//item")[:10]:
                title = item.find("title").text if item.find("title") is not None else "Untitled"
                link = item.find("link").text if item.find("link") is not None else source_url
                desc = item.find("description").text if item.find("description") is not None else ""
                
                # Try to parse date (very basic, improvements needed for prod)
                pub_date = None
                pub_string = item.find("pubDate")
                if pub_string is not None:
                    # Simple attempt, otherwise ignore date sorting
                    try:
                        # RFC 822 format often used in RSS
                        from email.utils import parsedate_to_datetime
                        pub_date = parsedate_to_datetime(pub_string.text)
        except Exception:
                        pass

                items.append(IntelligenceItem(
                    id=link,
                    title=title,
                    url=link,
                    source="Legal Feed",
                    domain="legal",
                    description=desc,
                    published_at=pub_date,
                    tags=["legal", "compliance"]
                ))
        except Exception:
            pass
            
        return items

    def _filter_relevance(self, items: list[IntelligenceItem]) -> list[IntelligenceItem]:
        """Filter items matching developer legal keywords."""
        relevant = []
        for item in items:
            text = f"{item.title} {item.description}".lower()
            if any(kw in text for kw in self.KEYWORDS):
                relevant.append(item)
        return relevant

    async def close(self) -> None:
        pass
