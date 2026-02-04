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

# from side.forensic_audit.runner import ForensicAuditRunner (DELETED)
# from side.intel.intelligence_store import IntelligenceStore (DELETED)
from side.storage.modules.base import ContextEngine
from side.storage.modules.forensic import ForensicStore
# from side.common.telemetry import monitor (DELETED)

class SidelithEventHandler(FileSystemEventHandler):
    """
    Handles file system events, triggers forensic audits, AND records the Event Clock.
    """
    def __init__(self, engine: ContextEngine, forensic: ForensicStore, loop: asyncio.AbstractEventLoop, project_id: str):
        self.engine = engine
        self.forensic = forensic
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
        
        # 1. Handle Rolling Chronicle (Hourly Synthesis)
        if now - self.last_chronicle_time > self.CHRONICLE_INTERVAL:
            self.last_chronicle_time = now
            asyncio.run_coroutine_threadsafe(
                self._trigger_rolling_chronicle(),
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

    def _check_event_storm(self) -> bool:
        """Detects high-IO situations (npm install, etc) and throttles observation."""
        now = time.time()
        
        # Recovery
        if self.quiet_mode:
            if now > self.quiet_until:
                self.quiet_mode = False
                print("🛡️ [WATCHER]: IO High Load subsided. Resuming Deep Awareness.")
            else:
                return True

        # Track window
        self.event_window = [ts for ts in self.event_window if now - ts < self.window_size]
        self.event_window.append(now)
        
        from side.config import config
        if len(self.event_window) > config.watcher_high_io_threshold:
            self.quiet_mode = True
            self.quiet_until = now + 30.0 # 30s Silence
            print(f"⚠️ [WATCHER]: High IO detected ({len(self.event_window)} events/10s). Entering Quiet Mode for 30s.")
            return True
        return False

    async def _trigger_rolling_chronicle(self):
        """
        [SILENT RESONANCE] Triggers the hourly intent compression.
        
        Philosophy:
        - We lack direct chat access (Cursor/IDE privacy).
        - We discover INTENT by observing OUTCOMES (FS changes + Git logs).
        - Resonance: Does the current state align with the Sovereign Anchor?
        - Rolling Chronicle: High-fidelity records of these discovered truths.
        """
        try:
            print(f"\n⏳ [SILENT RESONANCE]: Discovering intent from outcomes...")
            self.forensic.log_activity(
                project_id=self.project_id,
                tool="watcher",
                action="SILENT_RESONANCE",
                cost_tokens=0
            )
            # Remove fat: optimize call replaced with standard cleanup if needed
            self.forensic.cleanup_expired_data()
        except Exception as e:
            print(f"⚠️ Resonance Error: {e}")

    def _should_ignore(self, filepath: str) -> bool:
        # [EFFICIENCY]: Cache ignored patterns as a set for O(1) lookups
        if not hasattr(self, '_ignored_segments'):
            self._ignored_segments = {
                '__pycache__', '.git', '.side', 'node_modules', 
                '.DS_Store', 'dist', 'build', '.pytest_cache'
            }
        
        path_parts = Path(filepath).parts
        return any(part in self._ignored_segments for part in path_parts) or filepath.endswith('.env')

    async def _process_event(self, filepath: str):
        """
        The Core Logic: Record Event -> Pulse Check -> Log.
        """
        try:
            rel_path = Path(filepath).name
            
            # 1. RUN THE PULSE
            from side.pulse import pulse, PulseStatus
            
            context = {
                "user": "Developer",
                "target_file": filepath,
            }
            
            # 1.1 Read file content for pulse check
            try:
                content = Path(filepath).read_text()
                context["file_content"] = content
            except Exception:
                pass

            result = pulse.check_pulse(context)
            
            # 2. LOG THE OUTCOME (SOVEREIGN CORE)
            outcome_status = "PASS"
            if result.status == PulseStatus.VIOLATION:
                outcome_status = "VIOLATION"
            elif result.status == PulseStatus.DRIFT:
                outcome_status = "DRIFT"
            
            # Pulse check costs 0 SU for background watcher
            self.forensic.log_activity(
                project_id=self.project_id,
                tool="watcher",
                action=f"FILE_MOD:{rel_path}",
                cost_tokens=0,
                payload={"outcome": outcome_status}
            )
            
            # 3. Console Feedback
            if result.status == PulseStatus.VIOLATION:
                 print(f"\n🚨 [RED LINE VIOLATION]: {filepath}")
                 for v in result.violations:
                     print(f"   ❌ {v}")
            elif result.status == PulseStatus.DRIFT:
                 print(f"\n⚠️ [INTENT DRIFT]: {filepath}")
        
        except Exception as e:
            print(f"⚠️ Watcher Error: {e}", file=sys.stderr)

async def start_watcher(path: str):
    """
    Starts the Sidelith Watcher Daemon (The Event Clock).
    """
    path_obj = Path(path).resolve()
    print(f"🔭 Sidelith Watcher active on: {path_obj}")

    # [SILENT PARTNER]: Set low process priority
    try:
        if sys.platform != 'win32':
            os.nice(10) # 0 is normal, 20 is lowest. 10 is very polite.
            print("🍃 [POLITE]: Background priority set (os.nice).")
    except Exception as e:
        print(f"⚠️ Could not set process niceness: {e}")
    engine = ContextEngine()
    forensic = ForensicStore(engine)
    project_id = ContextEngine.get_project_id(str(path_obj))
    loop = asyncio.get_running_loop()
    
    event_handler = SidelithEventHandler(engine, forensic, loop, project_id)
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
