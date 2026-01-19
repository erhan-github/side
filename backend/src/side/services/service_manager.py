"""
Service manager for background intelligence services.

Manages lifecycle of all background services (file watcher, cache warmer, etc.)
"""

import asyncio
import logging
import signal
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from side.services.file_watcher import FileWatcher
from side.utils.cache_warmer import CacheWarmer, get_cache_warmer

logger = logging.getLogger(__name__)


class ServiceManager:
    """
    Manages all background services.

    Responsibilities:
    - Start/stop services
    - Health monitoring
    - Graceful shutdown
    - State persistence
    """

    def __init__(self, project_path: str | Path):
        """
        Initialize service manager.

        Args:
            project_path: Path to project to monitor
        """
        self.project_path = Path(project_path).resolve()
        self._running = False
        self._services: Dict[str, Any] = {}
        self._health_task: asyncio.Task | None = None

        # Service status
        self._status = {
            "started_at": None,
            "services": {},
        }

    async def start(self) -> None:
        """Start all background services."""
        if self._running:
            logger.warning("Service manager already running")
            return

        self._running = True
        self._status["started_at"] = datetime.now(timezone.utc).isoformat()

        logger.info("Starting sideMCP background services...")

        try:
            # Start file watcher
            await self._start_file_watcher()

            # Start context tracker
            await self._start_context_tracker()

            # Start cache warmer
            await self._start_cache_warmer()

            # Start cleanup scheduler
            await self._start_cleanup_scheduler()

            # Start Supabase Sync
            await self._start_supabase_sync()

            # Start Telemetry
            await self._start_telemetry()

            # Start health monitoring
            self._health_task = asyncio.create_task(self._health_monitor())

            # [Hyper-Ralph] Start Service Reaper
            self._reaper_task = asyncio.create_task(self._service_reaper())

            # Setup signal handlers for graceful shutdown
            self._setup_signal_handlers()

            logger.info("✅ All services started successfully (Reaper active)")

        except Exception as e:
            logger.error(f"Failed to start services: {e}", exc_info=True)
            await self.stop()
            raise

    async def stop(self) -> None:
        """Stop all background services gracefully."""
        if not self._running:
            return

        logger.info("Stopping sideMCP background services...")

        self._running = False

        # Stop reaper
        if hasattr(self, "_reaper_task") and self._reaper_task:
            self._reaper_task.cancel()
            try:
                await self._reaper_task
            except asyncio.CancelledError:
                pass

        # Stop health monitor
        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass

        # Stop all services
        for name, service in self._services.items():
            try:
                logger.info(f"Stopping {name}...")
                if hasattr(service, "stop"):
                    await service.stop()
                elif isinstance(service, asyncio.Task):
                    service.cancel()
                    try:
                        await service
                    except asyncio.CancelledError:
                        pass
                self._status["services"][name]["status"] = "stopped"
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}", exc_info=True)

        logger.info("✅ All services stopped")

    async def _start_file_watcher(self) -> None:
        """Start file watcher service."""
        logger.info("Starting file watcher...")

        watcher = FileWatcher(
            project_path=self.project_path,
            on_change=self._on_files_changed,
            debounce_seconds=2.0,
        )

        await watcher.start()

        self._services["file_watcher"] = watcher
        self._status["services"]["file_watcher"] = {
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info("✅ File watcher started")

    async def _start_context_tracker(self) -> None:
        """Start context tracker service."""
        logger.info("Starting context tracker...")

        from side.services.context_tracker import ContextTracker
        from side.storage.simple_db import SimplifiedDatabase

        db = SimplifiedDatabase()
        tracker = ContextTracker(db)

        self._services["context_tracker"] = tracker
        self._status["services"]["context_tracker"] = {
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info("✅ Context tracker started")

    async def _start_cache_warmer(self) -> None:
        """Start cache warmer service."""
        logger.info("Starting cache warmer...")

        from side.intel.market import MarketAnalyzer
        from side.storage.simple_db import SimplifiedDatabase

        db = SimplifiedDatabase()
        market = MarketAnalyzer()

        warmer = get_cache_warmer(db=db, market=market)
        warmer.interval_minutes = 30  # Refresh every 30 min

        await warmer.start()

        self._services["cache_warmer"] = warmer
        self._status["services"]["cache_warmer"] = {
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "interval_minutes": 30,
        }

        logger.info("✅ Cache warmer started")

    async def _start_cleanup_scheduler(self) -> None:
        """Start cleanup scheduler service."""
        logger.info("Starting cleanup scheduler...")

        from side.services.cleanup_scheduler import CleanupScheduler
        from side.storage.simple_db import SimplifiedDatabase

        db = SimplifiedDatabase()
        scheduler = CleanupScheduler(db)

        await scheduler.start()

        self._services["cleanup_scheduler"] = scheduler
        self._status["services"]["cleanup_scheduler"] = {
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "schedule": "Daily at 3 AM"
        }

        logger.info("✅ Cleanup scheduler started")

    async def _start_supabase_sync(self) -> None:
        """Start Supabase sync service."""
        logger.info("Starting Supabase sync...")

        from side.services.supabase_sync import SupabaseSyncService
        from side.storage.simple_db import SimplifiedDatabase

        # Initialize DB and Project ID
        db = SimplifiedDatabase()
        project_id = SimplifiedDatabase.get_project_id(self.project_path)

        sync_service = SupabaseSyncService(db, project_id)
        
        # Start in background task since it runs forever
        sync_task = asyncio.create_task(sync_service.run_forever(interval=300))
        
        self._services["supabase_sync"] = sync_task
        self._status["services"]["supabase_sync"] = {
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info("✅ Supabase sync started")

    async def _start_background_engines(self) -> None:
        """Start all background engines (Telemetry, Supabase Sync, Context Tracker, Auditor, Reaper)."""
        logger.info("Starting background engines...")

        from side.services.telemetry import TelemetryService
        from side.services.supabase_sync import SupabaseSyncService
        from side.services.context_tracker import ContextTracker
        from side.intel.auditor import AuditorService
        from side.storage.simple_db import SimplifiedDatabase

        self.tasks = [] # Initialize list to hold background tasks
        self.db = SimplifiedDatabase() # Initialize DB for engines
        project_id = SimplifiedDatabase.get_project_id(self.project_path)
        
        # 1. Telemetry (Anonymous Heartbeat)
        self.telemetry = TelemetryService(project_id)
        self.tasks.append(asyncio.create_task(self.telemetry.run_forever(interval=3600)))
        
        # 2. Supabase Sync
        self.sync_service = SupabaseSyncService(self.db, project_id)
        self.tasks.append(asyncio.create_task(self.sync_service.run_forever(interval=300)))
        
        # 3. Context Tracking
        self.context_tracker = ContextTracker(self.db) # ContextTracker expects db, not project_path in init
        self.tasks.append(asyncio.create_task(self.context_tracker.watch_forever(self.project_path)))

        # 4. Side Auditor (Daily Forensic Scan)
        self.auditor_service = AuditorService(self.db, self.project_path)
        self.tasks.append(asyncio.create_task(self.auditor_service.run_forever()))
        
        # 5. Service Reaper (Self-Healing)
        # The reaper monitors 'self.tasks' and restarts them if they die.
        self.tasks.append(asyncio.create_task(self._service_reaper()))
        
        logger.info("Service Manager started all background engines.")

    async def _on_files_changed(self, files: List[Path]) -> None:
        """
        Callback when files change.

        Triggers knowledge sync and context update.
        """
        logger.info(f"Files changed: {len(files)} files")

        # Update work context
        if "context_tracker" in self._services:
            try:
                tracker = self._services["context_tracker"]
                await tracker.update_context(self.project_path, changed_files)
                logger.debug("Work context updated")
            except Exception as e:
                logger.error(f"Error updating context: {e}", exc_info=True)

        # Invalidate query cache (context changed)
        try:
            from side.storage.simple_db import SimplifiedDatabase

            db = SimplifiedDatabase()
            deleted = db.invalidate_query_cache()
            if deleted > 0:
                logger.debug(f"Invalidated {deleted} cached queries")
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}", exc_info=True)

    async def _health_monitor(self) -> None:
        """Monitor service health."""
        while self._running:
            try:
                # Check each service
                for name, service in self._services.items():
                    is_healthy = True

                    # Check if service has health check method
                    if hasattr(service, "is_healthy"):
                        is_healthy = await service.is_healthy()

                    # Check if service is still running
                    if hasattr(service, "_running"):
                        is_healthy = is_healthy and service._running

                    # Update status
                    if name in self._status["services"]:
                        self._status["services"][name]["healthy"] = is_healthy

                    if not is_healthy:
                        logger.warning(f"Service {name} is unhealthy")

                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor: {e}", exc_info=True)
    async def _service_reaper(self) -> None:
        """
        [Hyper-Ralph] The Service Reaper.
        Periodically checks for 'Zombie' tasks (crashed services) and attempts to restart them.
        """
        while self._running:
            try:
                await asyncio.sleep(60) # Reap every 60s
                
                for name, service in list(self._services.items()):
                    should_restart = False
                    
                    if isinstance(service, asyncio.Task):
                        if service.done():
                            if service.exception():
                                logger.error(f"Service {name} crashed with exception: {service.exception()}")
                                should_restart = True
                            elif not self._running:
                                pass # Shutting down
                            else:
                                logger.warning(f"Service {name} exited unexpectedly.")
                                should_restart = True
                    
                    if should_restart:
                        logger.info(f"Reaper: Restarting {name}...")
                        if name == "supabase_sync": await self._start_supabase_sync()
                        elif name == "telemetry": await self._start_telemetry()
                        elif name == "cache_warmer": await self._start_cache_warmer()
                        elif name == "cleanup_scheduler": await self._start_cleanup_scheduler()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in service reaper: {e}", exc_info=True)

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        try:
            loop = asyncio.get_event_loop()

            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(
                    sig,
                    lambda: asyncio.create_task(self.stop()),
                )

            logger.debug("Signal handlers registered")
        except NotImplementedError:
            # Signal handlers not supported on this platform (e.g., Windows)
            logger.debug("Signal handlers not supported on this platform")

    def get_status(self) -> Dict[str, Any]:
        """Get current service status."""
        return self._status.copy()

    async def run_forever(self) -> None:
        """Run services until stopped."""
        await self.start()

        # Wait until stopped
        while self._running:
            await asyncio.sleep(1)


async def main() -> None:
    """Main entry point for background service."""
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Get project path from args or use current directory
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."

    # Create and run service manager
    manager = ServiceManager(project_path)

    try:
        await manager.run_forever()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
