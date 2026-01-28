
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from side.intel.fractal_indexer import update_branch

logger = logging.getLogger(__name__)

class SovereignHandler(FileSystemEventHandler):
    """
    Handles file system events and triggers Fractal Updates.
    """
    def __init__(self, root: Path, debounce_seconds: float = 1.0):
        self.root = Path(root).resolve()
        self.debounce_seconds = debounce_seconds
        self.last_triggered = {}

    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path).resolve()
        
        # Debounce logic
        now = time.time()
        if file_path in self.last_triggered:
            if now - self.last_triggered[file_path] < self.debounce_seconds:
                return
        
        self.last_triggered[file_path] = now
        
        # Trigger optimized fractal update
        try:
            update_branch(self.root, file_path)
            
            # Phase III-B: Proactive Telemetry Scan
            from side.intel.telemetry import run_proactive_scan
            run_proactive_scan(self.root, file_path)
            
        except Exception as e:
            logger.error(f"❌ [WATCHER_ERROR]: Failed to sync {file_path.name}: {e}")

    def on_created(self, event):
        self.on_modified(event)

def start_sovereign_watcher(root: Path):
    """
    Runs the infinite watch loop.
    """
    event_handler = SovereignHandler(root)
    observer = Observer()
    observer.schedule(event_handler, str(root), recursive=True)
    
    logger.info(f"🦅 [SOVEREIGN WATCH]: Monitoring {root} for Neural Compression...")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
