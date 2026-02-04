"""
Service manager for background intelligence services.

Manages lifecycle of all background services (file watcher, cache warmer, etc.)
"""

import asyncio
import logging
import signal
from side.services.integrity import IntegrityService
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from side.storage.modules.base import ContextEngine
from side.storage.modules.identity import IdentityStore
from side.storage.modules.strategic import StrategicStore
from side.storage.modules.forensic import ForensicStore
from side.storage.modules.transient import OperationalStore

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
        self.engine = ContextEngine()
        self.identity = IdentityStore(self.engine)
        self.strategic = StrategicStore(self.engine)
        self.forensic = ForensicStore(self.engine)
        self.operational = OperationalStore(self.engine)
        
        # [KAR-6.12] Initialize Unified Buffer
        from side.services.unified_buffer import UnifiedBuffer
        from side.config import config
        self.buffer = UnifiedBuffer({
            'strategic': self.strategic,
            'forensic': self.forensic,
            'operational': self.operational
        })
        
        self._running = False
        self._services: Dict[str, Any] = {}
        self._health_task: asyncio.Task | None = None
        self.tasks: List[asyncio.Task] = []

        # Service status
        self._status = {
            "started_at": None,
            "services": {},
        }
        
    async def _run_periodic_audit(self):
        """Runs the Isolation Audit every 24 hours."""
        while self._running:
            try:
                from side.intel.isolation_audit import run_project_audit
                run_project_audit(self.project_path)
            except Exception as e:
                logger.error(f"Isolation audit failed: {e}")
            await asyncio.sleep(config.service_audit_interval) # Configurable interval

    async def start(self) -> None:
        """Start all background services."""
        if self._running:
            logger.warning("Service manager already running")
            return

        self._running = True
        self._status["started_at"] = datetime.now(timezone.utc).isoformat()

        logger.info("Starting sideMCP background services...")

        try:
            # -1. Self-Check (Integrity)
            self.integrity = IntegrityService(self.project_path)
            if not await self.integrity.verify_node():
                 logger.warning("⚠️ Node integrity check failed. Background engines may be stale.")

            # 0. Start Unified Buffer (The Heartbeat)
            await self.buffer.start()

            # 1. Start background engines (Unified Logic)
            await self._start_background_engines()

            # Start health monitoring
            self._health_task = asyncio.create_task(self._health_monitor())

            # Setup signal handlers for graceful shutdown
            self._setup_signal_handlers()

            logger.info("✅ All services started successfully (Unified Buffer active)")

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

        # Stop all explicit services
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

        # [KAR-6.12] Stop background tasks
        for task in self.tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # [KAR-6.12] Stop Unified Buffer
        await self.buffer.stop()

        logger.info("✅ All services stopped")

    async def _start_file_watcher(self) -> None:
        """Start file watcher service."""
        logger.info("Starting file watcher...")

        from side.services.file_watcher import FileWatcher

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

        tracker = ContextTracker(self.operational)

        self._services["context_tracker"] = tracker
        self._status["services"]["context_tracker"] = {
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info("✅ Context tracker started")



    async def _start_cleanup_scheduler(self) -> None:
        """Start cleanup scheduler service."""
        logger.info("Starting cleanup scheduler...")

        from side.services.cleanup_scheduler import CleanupScheduler

        scheduler = CleanupScheduler(self.forensic)

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

        # SFO Sprint: No Fat Architecture - passing direct stores
        project_id = ContextEngine.get_project_id(self.project_path)

        sync_service = SupabaseSyncService(self.operational, self.identity, project_id)
        
        # Start in background task since it runs forever
        sync_task = asyncio.create_task(sync_service.run_forever(interval=300))
        
        self._services["supabase_sync"] = sync_task
        self._status["services"]["supabase_sync"] = {
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info("✅ Supabase sync started")

    async def _start_background_engines(self) -> None:
        """Start all background engines (Context Tracker, Silicon Pulse, Socket Listener)."""
        logger.info("Starting background engines...")

        from side.services.context_tracker import ContextTracker
        from side.services.silicon_pulse import SiliconPulseService
        from side.services.causal_ledger import ResolutionLedgerService
        from side.services.midnight_learning import MidnightLearningService
        from side.services.temporal_auditor import TemporalAuditorService
        from side.intel.auto_intelligence import AutoIntelligence
        from side.intel.isolation_audit import IsolationAuditor
        from side.services.socket_listener import SocketListenerService
        from side.services.signal_auditor import SignalAuditorService
        
        self.tasks = [] # Initialize list to hold background tasks
        project_id = ContextEngine.get_project_id(self.project_path)
        
        # 0. File Watcher (Sovereign Events)
        from side.services.file_watcher import FileWatcher
        self.watcher = FileWatcher(
            project_path=self.project_path,
            on_change=self._on_files_changed,
            debounce_seconds=2.0,
            buffer=self.buffer
        )
        self.tasks.append(asyncio.create_task(self.watcher.start()))
        
        # 1. Isolation Audit (Silo Protocol)
        self.isolation_auditor = IsolationAuditor(self.project_path)
        self.tasks.append(asyncio.create_task(self._run_periodic_audit()))
        
        # 2. Context Tracker (Operational Awareness)
        self.context_tracker = ContextTracker(self.operational, self.strategic, self.identity)
        self.tasks.append(asyncio.create_task(self.context_tracker.watch_forever(self.project_path)))

        # 3. [HYPER-PERCEPTION] Silicon Pulse (Hardware Friction)
        self.silicon_pulse = SiliconPulseService(self.operational)
        self.tasks.append(asyncio.create_task(self.silicon_pulse.run_forever()))

        # 4. [HYPER-PERCEPTION] Resolution Ledger (Causal Intelligence)
        self.resolution_ledger = ResolutionLedgerService(self.forensic, self.operational, buffer=self.buffer)
        self.tasks.append(asyncio.create_task(self.resolution_ledger.watch_logs()))
        
        # 5. [KAR-6.16] Universal Polyglot Socket Listener
        self.socket_listener = SocketListenerService(buffer=self.buffer)
        self.tasks.append(asyncio.create_task(self.socket_listener.start()))
        self._services["socket_listener"] = self.socket_listener
        self._status["services"]["socket_listener"] = {
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

        # 6. [ACTIVE CONTINUITY] Rolling Chronicle (Real-time Synthesis) (T-006)
        from side.services.rolling_chronicle import RollingChronicleService
        self.rolling_chronicle = RollingChronicleService(self.engine, self.strategic, self.forensic, self.operational)
        self.tasks.append(asyncio.create_task(self.rolling_chronicle.start()))
        
        # 7. [KAR-4] Strategic Context (AutoIntelligence)
        self.auto_intel = AutoIntelligence(self.project_path, buffer=self.buffer)
        self.tasks.append(asyncio.create_task(self.auto_intel.feed()))

        # 8. [KAR-5] Temporal Forensic Chronology
        self.temporal_auditor = TemporalAuditorService(self.buffer, self.project_path)
        self.tasks.append(asyncio.create_task(self.temporal_auditor.start()))

        # 9. [HYPER-PERCEPTION] Signal Auditor (Deep Discovery)
        self.signal_auditor = SignalAuditorService(self.operational)
        self.tasks.append(asyncio.create_task(self.signal_auditor.run_forever()))

        # 10. Service Reaper (Self-Healing)
        self.tasks.append(asyncio.create_task(self._service_reaper()))
        
        # 11. [SHADOW_INTENT] Ghost Listener (The Trash Moat) (T-106)
        from side.services.shadow_intent import ShadowIntentService
        self.shadow_intent = ShadowIntentService(self.buffer)
        self.tasks.append(asyncio.create_task(self.shadow_intent.start()))

        # 12. [ROI_SIMULATOR] Averted Disaster Ledger (T-108)
        from side.services.roi_simulator import ROISimulatorService
        self.roi_simulator = ROISimulatorService(self.buffer)
        
        # 13. [STRATEGIC_SCAVENGER] Plan Ingestion
        from side.services.strategic_scavenger import StrategicScavenger
        self.scavenger = StrategicScavenger(self.strategic)
        self.tasks.append(asyncio.create_task(self.scavenger.scavenge(self.project_path)))
        
        # Wire ROI to Resolution Ledger
        if hasattr(self, "resolution_ledger"):
            self.resolution_ledger.roi_callback = self.roi_simulator.simulate_resolution_impact
        
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
                await tracker.update_context(self.project_path, files) # changed_files -> files
                logger.debug("Work context updated")
            except Exception as e:
                logger.error(f"Error updating context: {e}", exc_info=True)

        # [V2: Invisible Intelligence] Trigger Proactive Audit
        if "auditor" in self._services:
            try:
                auditor_service = self._services["auditor"]
                # Run quick 8B LLM scan on the changed files
                await auditor_service.auditor.quick_scan(files)
                logger.info("Proactive V2 Audit complete (Invisible Layer)")
            except Exception as e:
                logger.error(f"Proactive Audit failed: {e}")

        # [KAR-6.2] [WFW] Notify Resolution Ledger of potential fixes
        if hasattr(self, "resolution_ledger"):
            for f in files:
                await self.resolution_ledger.notify_save(f)

        # [SHADOW_INTENT] Analyze rejections on save
        if hasattr(self, "shadow_intent"):
            for f in files:
                try:
                    with open(f, 'r') as content_file:
                        content = content_file.read()
                    await self.shadow_intent.notify_save(str(f), content)
                except:
                    pass

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
                await asyncio.sleep(config.heartbeat_interval)  # Configurable check

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
                        
                        # [MACHINE_TRUTH]: Notify Causal Ledger of the crash
                        if hasattr(self, "resolution_ledger"):
                            asyncio.create_task(self.resolution_ledger.notify_process_exit(1)) # General error exit
                            
                        if name == "supabase_sync": await self._start_supabase_sync()
                        elif name == "telemetry": await self._start_telemetry()
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
