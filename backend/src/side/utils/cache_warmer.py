"""
Cache warming utilities for Side.

Proactively fetches and caches articles in the background.
"""

import asyncio
import logging
from datetime import datetime, timezone

from side.intel.market import MarketAnalyzer
from side.storage.simple_db import SimplifiedDatabase

logger = logging.getLogger(__name__)


class CacheWarmer:
    """
    Warms article cache in the background.

    Ensures that articles are always fresh and ready for instant queries.
    """

    def __init__(
        self,
        db: SimplifiedDatabase,
        market: MarketAnalyzer,
        interval_minutes: int = 60,
    ):
        """
        Initialize cache warmer.

        Args:
            db: Database instance
            market: Market analyzer instance
            interval_minutes: How often to refresh cache (default 60 min)
        """
        self.db = db
        self.market = market
        self.interval_minutes = interval_minutes
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        """Start background cache warming."""
        if self._running:
            logger.warning("Cache warmer already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._warm_loop())
        logger.info(f"Cache warmer started (interval: {self.interval_minutes} min)")

    async def stop(self) -> None:
        """Stop background cache warming."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Cache warmer stopped")

    async def warm_once(self) -> int:
        """
        Warm cache once (fetch and store articles).

        Returns:
            Number of articles fetched and cached
        """
        try:
            logger.info("Warming article cache...")

            # Fetch articles from all sources
            articles = await self.market.fetch_all_sources(days=7)

            # Save to cache
            for article in articles:
                self.db.save_article(article)

            logger.info(f"Cached {len(articles)} articles")
            return len(articles)

        except Exception as e:
            logger.error(f"Cache warming failed: {e}", exc_info=True)
            return 0

    async def _warm_loop(self) -> None:
        """Background loop for cache warming."""
        while self._running:
            try:
                await self.warm_once()

                # Wait for next interval
                await asyncio.sleep(self.interval_minutes * 60)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache warming error: {e}", exc_info=True)
                # Wait a bit before retrying
                await asyncio.sleep(60)


# Global cache warmer instance
_warmer: CacheWarmer | None = None


def get_cache_warmer(
    db: SimplifiedDatabase | None = None,
    market: MarketAnalyzer | None = None,
) -> CacheWarmer:
    """
    Get or create the global cache warmer.

    Args:
        db: Database instance (required for first call)
        market: Market analyzer instance (required for first call)

    Returns:
        CacheWarmer instance
    """
    global _warmer

    if _warmer is None:
        if db is None or market is None:
            raise ValueError("db and market required for first call")
        _warmer = CacheWarmer(db, market)

    return _warmer
