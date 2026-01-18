"""
CSO.ai Market Intelligence.

Gathers and analyzes market information:
- Tech trends and news
- Competitor signals
- Industry developments
- Opportunity detection
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import httpx




from cso_ai.intel.sources.base import IntelligenceItem

# Compatibility alias for code expecting Article
Article = IntelligenceItem


class MarketAnalyzer:
    """
    Analyzes market trends and gathers intelligence.

    Uses Groq (Llama 3.3 70B) for smart article scoring.

    Responsibilities:
    - Fetch content from multiple sources
    - Score relevance against profile
    - Identify trends and patterns
    - Surface actionable opportunities
    """

    def __init__(self) -> None:
        """Initialize the analyzer."""
        self._articles: list[Article] = []
        self._strategist = None

    def _get_strategist(self):
        """Lazy load the strategist."""
        if self._strategist is None:
            from cso_ai.intel.strategist import Strategist
            self._strategist = Strategist()
        return self._strategist


    async def fetch_all_sources(
        self, 
        days: int = 7, 
        profile: dict[str, Any] | None = None
    ) -> list[IntelligenceItem]:
        """
        Fetch items from all sources IN PARALLEL with Domain Filtering.

        Args:
            days: Number of days to look back
            profile: User profile for domain-specific filtering

        Returns:
            List of IntelligenceItems
        """
        import asyncio
        from cso_ai.sources import HackerNewsSource, LobstersSource, GitHubSource
        from cso_ai.intel.sources.legal import LegalHubPlugin
        from cso_ai.intel.sources.investment import InvestmentHubPlugin
        from cso_ai.intel.sources.base import IntelligenceItem

        # Initialize Plugins
        legacy_sources = [
            ("HackerNews", HackerNewsSource(), "tech"),
            ("Lobsters", LobstersSource(), "tech"),
            ("GitHub", GitHubSource(), "tech"),
        ]
        
        plugins = [
            LegalHubPlugin(),
            InvestmentHubPlugin(),
        ]

        # Configure plugins with context
        domain = None
        if profile:
            biz = profile.get("business", {})
            domain = biz.get("domain")
            
        for p in plugins:
            if hasattr(p, "set_context"):
                p.set_context(domain)

        # 1. Fetch Legacy Sources (Article objects)
        async def fetch_legacy(name: str, source: Any, domain: str) -> list[IntelligenceItem]:
            items = []
            try:
                articles = await source.fetch(days=days, limit=15)
                await source.close()
                # Convert to IntelligenceItem
                for a in articles:
                    items.append(IntelligenceItem(
                        id=a.id,
                        title=a.title,
                        url=a.url,
                        source=a.source,
                        domain=domain,
                        description=a.description,
                        author=a.author,
                        published_at=a.published_at,
                        fetched_at=a.fetched_at,
                        tags=a.tags,
                        relevance_score=a.relevance_score,
                        relevance_reason=a.relevance_reason
                    ))
            except Exception as e:
                print(f"Error fetching from {name}: {e}")
            return items

        # 2. Fetch New Plugins (IntelligenceItem objects)
        async def fetch_plugin(plugin: Any) -> list[IntelligenceItem]:
            try:
                return await plugin.fetch(limit=10)
            except Exception as e:
                print(f"Error fetching from plugin {plugin.name}: {e}")
                return []

        # Execute all fetches
        tasks = [fetch_legacy(name, src, dom) for name, src, dom in legacy_sources]
        tasks += [fetch_plugin(p) for p in plugins]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten results
        all_items: list[IntelligenceItem] = []
        for result in results:
            if isinstance(result, list):
                all_items.extend(result)
        
        # Apply "Balanced Diet" Mixing Logic
        # We want a mix of Tech, Legal, and Investment
        final_mix = self._apply_diversity_mix(all_items)

        self._articles = final_mix # Store as current cache
        return final_mix

    def _apply_diversity_mix(self, items: list[IntelligenceItem]) -> list[IntelligenceItem]:
        """Enforce diversity in results."""
        tech = [i for i in items if i.domain == "tech"]
        legal = [i for i in items if i.domain == "legal"]
        invest = [i for i in items if i.domain == "investment"]
        
        # Simple mixing strategy: top N from each category
        # 15 Tech, 3 Legal, 2 Investment
        selection = []
        selection.extend(tech[:15])
        selection.extend(legal[:3])
        selection.extend(invest[:2])
        
        # Sort by date usually, but here we might want to group or sort by score later
        # For now, simplistic sort by date if available (normalize to aware UTC)
        def get_sort_date(item):
            dt = item.published_at or datetime.min
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
            
        selection.sort(key=get_sort_date, reverse=True)
        return selection

    async def score_articles(
        self,
        articles: list[Article],
        profile: dict[str, Any],
    ) -> list[Article]:
        """
        Score articles for relevance using [Hyper-Ralph] Batch Scoring.
        """
        strategist = self._get_strategist()
        if not articles:
            return []

        # Convert objects to dicts for strategist
        article_dicts = [
            {
                "title": a.title,
                "url": a.url,
                "description": a.description
            } for a in articles
        ]

        # Batch scoring in chunks of 10
        import math
        chunk_size = 10
        all_scores = []
        
        for i in range(0, len(article_dicts), chunk_size):
            chunk = article_dicts[i:i + chunk_size]
            scores = await strategist.batch_score_articles(chunk, profile)
            all_scores.extend(scores)

        # Map scores back to objects
        score_map = {s["url"]: s for s in all_scores if "url" in s}
        for article in articles:
            s_data = score_map.get(article.url, {})
            article.relevance_score = float(s_data.get("score", 50))
            article.relevance_reason = s_data.get("reason", "Heuristic fallback")

        # Sort by relevance
        articles.sort(key=lambda a: a.relevance_score or 0, reverse=True)
        return articles

    def _format_profile(self, profile: dict[str, Any]) -> str:
        """Format profile for scoring prompt."""
        lines = []

        tech = profile.get("technical", {})
        if tech.get("primary_language"):
            lines.append(f"Language: {tech['primary_language']}")
        if tech.get("frameworks"):
            lines.append(f"Frameworks: {', '.join(tech['frameworks'])}")

        biz = profile.get("business", {})
        if biz.get("domain"):
            lines.append(f"Domain: {biz['domain']}")
        if biz.get("product_type"):
            lines.append(f"Product: {biz['product_type']}")
        if biz.get("integrations"):
            lines.append(f"Uses: {', '.join(biz['integrations'])}")

        return "\n".join(lines) if lines else "General software project"

    async def get_tech_articles(
        self,
        profile: dict[str, Any],
        days: int = 7,
        limit: int = 10,
    ) -> list[Article]:
        """Get tech-focused articles scored for the profile."""
        articles = await self.fetch_all_sources(days)
        scored = await self.score_articles(articles, profile)
        return scored[:limit]

    async def get_business_articles(
        self,
        profile: dict[str, Any],
        days: int = 7,
        limit: int = 10,
    ) -> list[Article]:
        """Get business-focused articles."""
        # For now, same as tech but could filter differently
        articles = await self.fetch_all_sources(days)
        scored = await self.score_articles(articles, profile)

        # Prefer business-related content
        business_keywords = ["startup", "funding", "business", "market", "growth", "revenue"]
        for article in scored:
            text = f"{article.title} {article.description or ''}".lower()
            if any(kw in text for kw in business_keywords):
                article.relevance_score = (article.relevance_score or 0) + 10

        scored.sort(key=lambda a: a.relevance_score or 0, reverse=True)
        return scored[:limit]

    async def explore_topic(
        self,
        topic: str,
        profile: dict[str, Any],
        limit: int = 10,
    ) -> list[Article]:
        """Get articles about a specific topic."""
        articles = await self.fetch_all_sources(days=14)

        # Filter by topic
        topic_lower = topic.lower()
        relevant = []
        for article in articles:
            text = f"{article.title} {article.description or ''} {' '.join(article.tags)}".lower()
            if topic_lower in text:
                relevant.append(article)

        # Score remaining
        scored = await self.score_articles(relevant, profile)
        return scored[:limit]

    async def analyze_url(
        self,
        url: str,
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze a specific URL for relevance."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                # Extract title from HTML
                html = response.text
                title_match = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
                title = title_match.group(1) if title_match else url

                # Extract description
                desc_match = re.search(
                    r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
                    html,
                    re.IGNORECASE,
                )
                description = desc_match.group(1) if desc_match else None

        except Exception:
            title = url
            description = None

        # Score using strategist
        strategist = self._get_strategist()
        score, reason = await strategist.score_article(
            title=title,
            url=url,
            description=description,
            profile=profile,
        )

        return {
            "url": url,
            "title": title,
            "description": description,
            "relevance_score": score,
            "relevance_reason": reason,
            "worth_reading": score >= 50,
            "recommendation": (
                "Highly relevant - read this!" if score >= 70 else
                "Somewhat relevant - skim it" if score >= 50 else
                "Low relevance - skip unless curious"
            ),
        }
