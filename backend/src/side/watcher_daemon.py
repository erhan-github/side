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

from side.forensic_audit.runner import ForensicAuditRunner
from side.intel.intelligence_store import IntelligenceStore
from side.storage.simple_db import SimplifiedDatabase
from side.common.telemetry import monitor

class SidelithEventHandler(FileSystemEventHandler):
    """
    Handles file system events, triggers forensic audits, AND records the Event Clock.
    """
    def __init__(self, runner: ForensicAuditRunner, store: Optional[IntelligenceStore], loop: asyncio.AbstractEventLoop, project_id: str):
        self.runner = runner
        self.store = store
        self.loop = loop
        self.project_id = project_id
        self.last_scan_time: Dict[str, float] = {}
        self.debounce_seconds = 2.0  # Faster debounce for responsiveness
        self.pending_scans: Set[str] = set()

    def on_modified(self, event: FileSystemEvent):
        if event.is_directory:
            return
        
        filepath = str(event.src_path)
        if self._should_ignore(filepath):
            return

        # Simple Debounce Logic
        now = time.time()
        last = self.last_scan_time.get(filepath, 0)
        
        if now - last > self.debounce_seconds:
            # print(f"👀 Detected change in: {Path(filepath).name}")
            self.last_scan_time[filepath] = now
            # Schedule audit in the async loop
            asyncio.run_coroutine_threadsafe(
                self._process_event(filepath),
                self.loop
            )

    def _should_ignore(self, filepath: str) -> bool:
        # Ignore common noise
        ignored = [
            '__pycache__', '.git', '.side', 'node_modules', 
            '.DS_Store', 'dist', 'build', '.env', '.pytest_cache'
        ]
        return any(x in filepath for x in ignored)

    async def _process_event(self, filepath: str):
        """
        The Core Logic: Record Event -> Audit -> Update Record.
        """
        try:
            rel_path = Path(filepath).name
            
            # print(f"🕵️  Analzying {rel_path}...")
            
            # 2. THE AUDIT: Verify the change
            # Default to checking logic for code, strategy for docs
            if filepath.endswith('.py'):
                res = await self.runner.run_single_probe("forensic.code_quality", filepath)
                probe_type = "forensic.code_quality"
            elif filepath.endswith('.md'):
                res = await self.runner.run_single_probe("forensic.strategy", filepath)
                probe_type = "forensic.strategy"
            else:
                return

            # 3. THE EVENT CLOCK
            # Standard: Record silently.
            if self.store:
                outcome_status = "PASS"
                summary = "Verified"
                
                # Intelligent Summary Extraction
                if res:
                    lines = res.splitlines()
                    # Find the first line that isn't PASS
                    failure_line = next((line for line in lines if "FAIL" in line or "WARN" in line or "Critical" in line), None)
                    if failure_line:
                        summary = failure_line
                    else:
                        summary = lines[0] if lines else "Verified"

                if "FAIL" in res or "Critical" in res:
                     outcome_status = "VIOLATION"
                elif "WARN" in res:
                     outcome_status = "WARNING"
                
                self.store.record_event(
                    project_id=self.project_id,
                    event_type="CODE_MODIFICATION",
                    context={
                        "file": rel_path,
                        "path": filepath,
                        "probe": probe_type,
                        "full_report": res # Capture full context
                    },
                    outcome=f"{outcome_status}: {summary}"
                )
            
            # 4. THE WHISPER (Silent Mode)
            # Only speak if CRITICAL
            if "FAIL" in res or "Critical" in res:
                 print(f"\n🚨 Sidelith Whisper [{datetime.now().strftime('%H:%M:%S')}]:\n{res}")
                
        except Exception as e:
            # Errors are always critical enough to log to stderr
            import sys
            print(f"⚠️ Watcher Error: {e}", file=sys.stderr)

async def start_watcher(path: str):
    """
    Starts the Sidelith Watcher Daemon (The Event Clock).
    """
    path_obj = Path(path).resolve()
    print(f"🔭 Sidelith Watcher active on: {path_obj}")
    print("   (Press Ctrl+C to stop)")

    # Initialize The Stack
    db = SimplifiedDatabase()
    store = IntelligenceStore(db)
    runner = ForensicAuditRunner(str(path_obj))
    
    # Get Project ID (Identity Resolution)
    project_id = db.get_project_id(str(path_obj))
    
    loop = asyncio.get_running_loop()
    
    event_handler = SidelithEventHandler(runner, store, loop, project_id)
    observer = Observer()
    observer.schedule(event_handler, str(path_obj), recursive=True)
    observer.start()

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
