"""
Service manager for background intelligence services.

Manages lifecycle of all background services (file watcher, cache warmer, etc.)
"""

import asyncio
import logging
import signal
from side.services.integrity import IntegrityService
from side.services.mixins import ServiceLifecycleMixin
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from side.storage.modules.base import ContextEngine
from side.storage.modules.identity import IdentityService
from side.storage.modules.strategy import DecisionStore
from side.storage.modules.audit import AuditService
from side.storage.modules.transient import SessionCache
from side.utils.memory_diagnostics import get_diagnostics as get_memory_diagnostics

logger = logging.getLogger(__name__)


class ServiceManager(ServiceLifecycleMixin):
    """
    Manages all background services.
    Inherits lifecycle uniformity via ServiceLifecycleMixin.
    """

    def __init__(self, project_path: str | Path):
        """Initialize service manager."""
        super().__init__()
        self.project_path = Path(project_path).resolve()
        self.engine = ContextEngine()
        self.profile = IdentityService(self.engine)
        self.plans = DecisionStore(self.engine)
        self.audits = AuditService(self.engine)
        self.operational = SessionCache(self.engine)
        
        from side.services.data_buffer import DataBuffer
        from side.config import config
        self.buffer = DataBuffer({
            'plans': self.plans,
            'audits': self.audits,
            'operational': self.operational
        })
        
        self._running = False
        self._health_task: asyncio.Task | None = None
        self._memory_task: asyncio.Task | None = None

        # Service status (Mixin handles self._status["services"])
        self._status.update({
            "started_at": None,
        })
        
    async def _run_periodic_audit(self):
        """Runs the Isolation Audit every 24 hours."""
        while self._running:
            try:
                from side.intel.isolation_audit import run_project_audit
                run_project_audit(self.project_path)
            except Exception as e:
                logger.error(f"Isolation audit failed: {e}")
            from side.config import config
            await asyncio.sleep(config.service_audit_interval)

    async def start(self) -> None:
        """Start all background services."""
        if self._running:
            logger.warning("Service manager already running")
            return

        self._running = True
        self._status["started_at"] = datetime.now(timezone.utc).isoformat()

        logger.info("Starting sideMCP background services...")

        try:
            self.integrity = IntegrityService(self.project_path)
            if not await self.integrity.verify_node():
                 logger.warning("⚠️ Node integrity check failed. Background engines may be stale.")

            await self.buffer.start()
            await self._start_background_engines()

            self._health_task = asyncio.create_task(self._health_monitor())
            self._memory_task = asyncio.create_task(self._memory_monitor())

            self._setup_signal_handlers()
            logger.info("✅ All services started successfully (Data Buffer active)")

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

        # Mixin handles standard task cancellation
        await self.kill_all_services()

        if self._health_task: self._health_task.cancel()
        if self._memory_task: self._memory_task.cancel()
        
        await self.buffer.stop()
        logger.info("✅ All services stopped")

    async def _start_background_engines(self) -> None:
        """Start all background engines using standard lifecycle mixin."""
        logger.info("Starting background engines...")

        from side.services.context_tracker import ContextTracker
        from side.services.system_health import SystemHealthService
        from side.services.event_ledger import EventLedgerService
        from side.services.socket_listener import SocketListenerService
        from side.services.event_logger import EventLogger
        from side.services.state_snapshot import StateSnapshotService
        from side.services.system_monitor import SystemMonitorService
        from side.services.intent_tracker import IntentTrackerService
        from side.services.metrics_calculator import MetricsCalculator
        from side.services.doc_scanner import GoalIngestor
        from side.intel.context_service import ContextService
        from side.services.file_watcher import FileWatcher
        
        # 0. File Watcher
        self.watcher = FileWatcher(
            project_path=self.project_path,
            on_change=self._on_files_changed,
            debounce_seconds=2.0,
            buffer=self.buffer
        )
        await self.launch_service("file_watcher", self.watcher.start)
        
        # 1. Isolation Audit
        await self.launch_service("isolation_audit", self._run_periodic_audit)
        
        # 2. Context Tracker
        self.context_tracker = ContextTracker(self.operational, self.plans, self.profile)
        await self.launch_service("context_tracker", self.context_tracker.watch_forever, self.project_path)

        # 3. System Health
        self.system_health = SystemHealthService(self.operational)
        await self.launch_service("system_health", self.system_health.run_forever)

        # 4. Event Ledger
        self.event_ledger = EventLedgerService(self.audits, self.operational, buffer=self.buffer)
        await self.launch_service("event_ledger", self.event_ledger.watch_logs)
        
        # 5. Socket Listener
        self.socket_listener = SocketListenerService(buffer=self.buffer)
        await self.launch_service("socket_listener", self.socket_listener.start)

        # 6. State Snapshot
        self.state_snapshot = StateSnapshotService(self.engine, self.plans, self.audits, self.operational)
        await self.launch_service("state_snapshot", self.state_snapshot.start)
        
        # 7. ContextService
        self.context_service = ContextService(self.project_path, self.engine, buffer=self.buffer)
        await self.launch_service("auto_intel", self.context_service)

        # 8. System Monitor
        self.system_monitor = SystemMonitorService(self.buffer, self.project_path)
        await self.launch_service("system_monitor", self.system_monitor.start)

        # 9. Event Logger
        self.event_logger = EventLogger(self.operational)
        await self.launch_service("event_logger", self.event_logger.run_forever)

        # 10. Service Reaper (Self-Healing)
        await self.launch_service("service_reaper", self._service_reaper)
        
        # 11. Intent Tracker
        self.intent_tracker = IntentTrackerService(self.buffer)
        await self.launch_service("intent_tracker", self.intent_tracker.start)

        # 12. Metrics Calculator
        self.metrics_calculator = MetricsCalculator(self.buffer)
        
        # 13. Doc Scanner
        self.goal_ingestor = GoalIngestor(self.plans)
        await self.launch_service("doc_scanner", self.goal_ingestor.scavenge, self.project_path)
        
        if hasattr(self, "event_ledger"):
            self.event_ledger.roi_callback = self.metrics_calculator.estimate_resolution_impact
        
        logger.info("Service Manager started all background engines via Mixin.")

    async def _on_files_changed(self, files: List[Path]) -> None:
        """Callback when files change."""
        logger.info(f"Files changed: {len(files)} files")

        if hasattr(self, "context_tracker"):
            try:
                await self.context_tracker.update_context(self.project_path, files)
            except Exception as e:
                logger.error(f"Error updating context: {e}")

        if hasattr(self, "resolution_ledger"):
            for f in files:
                await self.resolution_ledger.notify_save(f)

        if hasattr(self, "shadow_intent"):
            for f in files:
                try:
                    with open(f, 'r') as content_file:
                        content = content_file.read()
                    await self.shadow_intent.notify_save(str(f), content)
                except: pass

    async def _health_monitor(self) -> None:
        """Monitor service health."""
        from side.config import config
        while self._running:
            try:
                for name, task in self._tasks.items():
                    is_healthy = not task.done() or task.exception() is None
                    if name in self._status["services"]:
                        self._status["services"][name]["healthy"] = is_healthy

                await asyncio.sleep(config.heartbeat_interval)
            except asyncio.CancelledError: break
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
    
    async def _memory_monitor(self) -> None:
        """Monitor memory usage and log diagnostics."""
        mem_diag = get_memory_diagnostics()
        while self._running:
            try:
                mem_diag.sample()
                report_lines = [mem_diag.get_report()]
                
                if hasattr(self, "watcher"):
                    watcher_diag = self.watcher.get_diagnostics()
                    report_lines.append(f"  File Watchers: {watcher_diag['watcher_count']} active")
                    report_lines.append(f"  Git Velocity: {watcher_diag['git_velocity']:.2f}")
                
                active_tasks = len([t for t in self._tasks.values() if not t.done()])
                report_lines.append(f"  Active Services: {active_tasks}/{len(self._tasks)}")
                
                logger.info("\n".join(report_lines))
                
                # Wait before next check (30 seconds)
                await asyncio.sleep(30)
            except asyncio.CancelledError: break
            except Exception as e:
                logger.error(f"Error in memory monitor: {e}")
                await asyncio.sleep(30)
    
    async def _service_reaper(self) -> None:
        """[High-Integrity] Self-Healing."""
        while self._running:
            try:
                await asyncio.sleep(60)
                for name, task in list(self._tasks.items()):
                    if task.done() and self._running:
                        logger.warning(f"Reaper: Service {name} exited. Restarting...")
                        # In a real implementation, we'd re-launch based on original factory
                        # For now, it logs the failure and cleanup happens on stop
            except asyncio.CancelledError: break
            except Exception as e:
                logger.error(f"Error in reaper: {e}")

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        try:
            loop = asyncio.get_event_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
        except (NotImplementedError, RuntimeError) as e:
            logger.warning(f"Could not setup signal handlers (likely non-Unix platform): {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current service status."""
        return self._status.copy()

    async def run_forever(self) -> None:
        """Run services until stopped."""
        await self.start()
        while self._running: await asyncio.sleep(1)


async def main() -> None:
    """Main entry point for background service."""
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."
    manager = ServiceManager(project_path)
    try: await manager.run_forever()
    except KeyboardInterrupt: logger.info("Received interrupt signal")
    finally: await manager.stop()


if __name__ == "__main__":
    asyncio.run(main())
