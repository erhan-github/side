"""
Cleanup scheduler for automatic data maintenance.

Runs daily cleanup job to remove expired data and keep database small.
"""

import asyncio
import logging
from datetime import datetime, time, timezone

from side.storage.simple_db import SimplifiedDatabase

logger = logging.getLogger(__name__)


class CleanupScheduler:
    """
    Schedules and runs automatic cleanup jobs.

    Runs daily at 3 AM to clean up expired data.
    """

    def __init__(self, db: SimplifiedDatabase):
        """
        Initialize cleanup scheduler.

        Args:
            db: Database instance
        """
        self.db = db
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start cleanup scheduler."""
        if self._running:
            logger.warning("Cleanup scheduler already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._cleanup_loop())
        logger.info("Cleanup scheduler started (runs daily at 3 AM)")

    async def stop(self) -> None:
        """Stop cleanup scheduler."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Cleanup scheduler stopped")

    async def run_cleanup_now(self) -> dict[str, int]:
        """
        Run cleanup immediately (for testing/manual trigger).

        Returns:
            Dict with counts of deleted records per table
        """
        logger.info("Running cleanup job...")

        try:
            deleted = self.db.cleanup_expired_data()

            total = sum(deleted.values())
            logger.info(
                f"Cleanup complete: {total} records deleted "
                f"(work_context: {deleted.get('work_context', 0)}, "
                f"query_cache: {deleted.get('query_cache', 0)}, "
                f"articles: {deleted.get('articles', 0)})"
            )

            # Get database stats after cleanup
            stats = self.db.get_database_stats()
            logger.info(
                f"Database size: {stats['db_size_mb']:.2f} MB "
                f"({stats['profiles_count']} profiles, "
                f"{stats['articles_count']} articles)"
            )

            return deleted

        except Exception as e:
            logger.error(f"Cleanup job failed: {e}", exc_info=True)
            return {}

    async def _cleanup_loop(self) -> None:
        """Background loop for scheduled cleanup."""
        while self._running:
            try:
                # Calculate time until next 3 AM
                now = datetime.now(timezone.utc)
                target_time = time(hour=3, minute=0)  # 3 AM

                # Get next occurrence of 3 AM
                next_run = datetime.combine(now.date(), target_time, tzinfo=timezone.utc)
                if next_run <= now:
                    # If 3 AM already passed today, schedule for tomorrow
                    from datetime import timedelta

                    next_run += timedelta(days=1)

                # Calculate wait time
                wait_seconds = (next_run - now).total_seconds()

                logger.debug(f"Next cleanup scheduled for {next_run.isoformat()}")

                # Wait until next run
                await asyncio.sleep(wait_seconds)

                # Run cleanup
                await self.run_cleanup_now()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}", exc_info=True)
                # Wait 1 hour before retrying
                await asyncio.sleep(3600)
