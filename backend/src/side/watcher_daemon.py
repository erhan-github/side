import sys
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Set, Dict, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

# Add backend python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from side.storage.modules.base import ContextEngine
from side.storage.modules.audit import AuditService
from side.intel.tree_indexer import update_branch

import logging
logger = logging.getLogger("side.watcher")

class SidelithEventHandler(FileSystemEventHandler):
    """
    Handles file system events, triggers audits, AND records the Event Clock.
    """
    def __init__(self, engine: ContextEngine, ledger: AuditService, loop: asyncio.AbstractEventLoop, project_id: str):
        self.engine = engine
        self.ledger = ledger
        self.loop = loop
        self.project_id = project_id
        self.last_scan_time: Dict[str, float] = {}
        self.debounce_seconds = 2.0
        self.last_chronicle_time = time.time()
        self.CHRONICLE_INTERVAL = 3600 # 1 Hour
        
        # [HARDENING]: Event Storm Circuit Breaker
        self.event_window: list[float] = []
        self.window_size = 10.0 # seconds
        self.quiet_mode = False
        self.quiet_until = 0.0

    def on_modified(self, event: FileSystemEvent):
        if event.is_directory:
            return
        
        filepath = str(event.src_path)
        if self._should_ignore(filepath):
            return

        now = time.time()
        
        # 1. Handle State Snapshot (Hourly Synthesis)
        if now - self.last_chronicle_time > self.CHRONICLE_INTERVAL:
            self.last_chronicle_time = now
            asyncio.run_coroutine_threadsafe(
                self._trigger_state_snapshot(),
                self.loop
            )

        # 2. Circuit Breaker Check
        if self._check_event_storm():
            return

        # 3. Handle File Modification
        last = self.last_scan_time.get(filepath, 0)
        if now - last > self.debounce_seconds:
            self.last_scan_time[filepath] = now
            asyncio.run_coroutine_threadsafe(
                self._process_event(filepath),
                self.loop
            )

    async def _service_reaper(self) -> None:
        """Self-Healing mechanism for background services."""

    def _check_event_storm(self) -> bool:
        """Detects high-IO situations (npm install, etc) and throttles observation."""
        now = time.time()
        
        # Recovery
        if self.quiet_mode:
            if now > self.quiet_until:
                self.quiet_mode = False
                logger.info("🛡️ [WATCHER]: IO High Load subsided. Resuming Deep Awareness.")
            else:
                return True

        # Track window
        self.event_window = [ts for ts in self.event_window if now - ts < self.window_size]
        self.event_window.append(now)
        
        from side.config import config
        if len(self.event_window) > config.watcher_high_io_threshold:
            self.quiet_mode = True
            self.quiet_until = now + 30.0 # 30s Silence
            logger.warning(f"⚠️ [WATCHER]: High IO detected ({len(self.event_window)} events/10s). Entering Quiet Mode for 30s.")
            return True
        return False

    async def _trigger_state_snapshot(self):
        """
        [CONSISTENCY CHECK] Triggers the hourly state compression.
        
        Philosophy:
        - We lack direct chat access (Cursor/IDE privacy).
        - We discover INTENT by observing OUTCOMES (FS changes + Git logs).
        - Consistency: Does the current state align with the Project Definition?
        - State Snapshot: High-fidelity records of these discovered truths.
        """
        try:
            logger.info(f"⏳ [CONSISTENCY CHECK]: Discovering intent from outcomes...")
            self.ledger.log_activity(
                project_id=self.project_id,
                tool="watcher",
                action="CONSISTENCY_CHECK",
                cost_tokens=0
            )
            # Remove fat
            self.ledger.cleanup_expired_data()
        except Exception as e:
            logger.error(f"⚠️ Consistency Check Error: {e}")

    def _should_ignore(self, filepath: str) -> bool:
        # [GITIGNORE INHERITANCE]: Strategic Audit
        from side.utils.ignore_store import get_ignore_store
        ignore_store = get_ignore_store(self.engine.get_repo_root())
        
        if ignore_store.is_ignored(filepath):
            return True
            
        # Hardcoded safety segments as backup
        path_parts = Path(filepath).parts
        segments = {'.git', '.side', 'node_modules', '__pycache__'}
        return any(part in segments for part in path_parts) or filepath.endswith('.env')

    async def _process_event(self, filepath: str):
        """
        The Core Logic: Record Event -> Pulse Check -> Log.
        """
        try:
            rel_path = Path(filepath).name
            
            # 1. RUN THE HEALTH CHECK
            from side.health import health, HealthStatus
            
            context = {
                "user": "Developer",
                "target_file": filepath,
            }
            
            # 1.1 Read file content for health check
            try:
                content = Path(filepath).read_text()
                context["file_content"] = content
            except Exception:
                pass

            result = health.check_health(context)
            
            # 2. LOG THE OUTCOME (SYSTEM CORE)
            outcome_status = "PASS"
            if result.status == HealthStatus.VIOLATION:
                outcome_status = "VIOLATION"
            elif result.status == HealthStatus.DRIFT:
                outcome_status = "DRIFT"
            
            # Health check costs 0 SU for background watcher
            self.ledger.log_activity(
                project_id=self.project_id,
                tool="watcher",
                action=f"FILE_MOD:{rel_path}",
                cost_tokens=0,
                payload={"outcome": outcome_status}
            )
            
            # 3. CRITICAL: Trigger Fractal Index Update (Merkle Consistency)
            try:
                # Run sync to block event propagation if needed, but here we just trigger
                update_branch(self.engine.get_repo_root(), Path(filepath), schema_store=self.engine.schema)
                logger.info(f"⚡ [FRACTAL]: Selective index update for {rel_path}")
            except Exception as e:
                logger.warning(f"⚠️ Fractal Sync Failed for {rel_path}: {e}")
            
            # 4. Console Feedback -> Logger Feedback
            if result.status == HealthStatus.VIOLATION:
                 logger.error(f"🚨 [CRITICAL VIOLATION]: {filepath}")
                 for v in result.violations:
                     logger.error(f"   ❌ {v}")
            elif result.status == HealthStatus.DRIFT:
                 logger.warning(f"⚠️ [INTENT DRIFT]: {filepath}")
        
        except Exception as e:
            logger.error(f"⚠️ Watcher Error: {e}")

async def start_watcher(path: str):
    """
    Starts the Sidelith Watcher Daemon (The Event Clock).
    """
    path_obj = Path(path).resolve()
    logger.info(f"🔭 Sidelith Watcher active on: {path_obj}")

    # [SILENT PARTNER]: Set low process priority
    try:
        if sys.platform != 'win32':
            os.nice(10) # 0 is normal, 20 is lowest. 10 is very polite.
            logger.info("🍃 [POLITE]: Background priority set (os.nice).")
    except Exception as e:
        logger.warning(f"⚠️ Could not set process niceness: {e}")
    engine = ContextEngine()
    ledger = engine.audits
    project_id = ContextEngine.get_project_id(str(path_obj))
    loop = asyncio.get_running_loop()
    
    event_handler = SidelithEventHandler(engine, ledger, loop, project_id)
    observer = Observer()
    observer.schedule(event_handler, str(path_obj), recursive=True)
    observer.start()

    # 3. START TERMINAL MONITOR
    from side.terminal.monitor import TerminalMonitor
    term_monitor = TerminalMonitor()
    asyncio.create_task(term_monitor.start())

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # Default to current dir if no arg
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    asyncio.run(start_watcher(target_dir))
