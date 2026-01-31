
import logging
import asyncio
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from side.intel.auto_intelligence import AutoIntelligence

logger = logging.getLogger(__name__)

class SovereignHandler(FileSystemEventHandler):
    """
    [KAR-8.3] The Sovereign Event Handler.
    Listens for file changes and triggers incremental intelligence feeds.
    """
    def __init__(self, intel: AutoIntelligence, loop: asyncio.AbstractEventLoop):
        self.intel = intel
        self.loop = loop
        self.ignore_patterns = [".git", "__pycache__", "node_modules", ".side/local.json"]

    def on_modified(self, event):
        if event.is_directory:
            return
        
        path = Path(event.src_path)
        
        # 1. Ignore noise
        if any(p in str(path) for p in self.ignore_patterns):
            return

        # 2. Filter for Strategic Signals
        # We target .md files and specifically task.md / walkthroughs
        is_strategic = path.suffix == ".md" or "task.md" in path.name or "WALKTHROUGH" in path.name
        
        if is_strategic:
            logger.info(f"🔔 [WATCHER]: Strategic Change: {path.name}")
            # Ensure we don't block the observer thread
            try:
                self.loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(self.intel.incremental_feed(path))
                )
            except Exception as e:
                logger.error(f"❌ [WATCHER]: Sync Dispatch Failed: {e}")

class WatcherService:
    def __init__(self, intel: AutoIntelligence):
        self.intel = intel
        self.observer = Observer()
        self.loop = asyncio.get_event_loop()
        
    def start(self):
        """Starts monitoring the project and brain paths."""
        logger.info("🚀 [WATCHER]: Activating Sovereign Watcher...")
        
        # Monitor Project Root
        handler = SovereignHandler(self.intel, self.loop)
        self.observer.schedule(handler, str(self.intel.project_path), recursive=True)
        
        # Monitor Antigravity Brain Path
        if self.intel.brain_path.exists():
            logger.info(f"🔭 [WATCHER]: Monitoring Antigravity Brain at {self.intel.brain_path}")
            self.observer.schedule(handler, str(self.intel.brain_path), recursive=True)
            
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

if __name__ == "__main__":
    # Test Run
    logging.basicConfig(level=logging.INFO)
    intel = AutoIntelligence(Path.cwd())
    watcher = WatcherService(intel)
    watcher.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
