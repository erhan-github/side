import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from side.intel.fractal_indexer import IGNORES, update_branch

logger = logging.getLogger(__name__)

class SovereignHandler(FileSystemEventHandler):
    """
    The 'Always-On' Observer.
    Listens for file changes and triggers real-time context updates.
    """
    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()
        
    def on_modified(self, event):
        self._process(event)
        
    def on_created(self, event):
        self._process(event)
        
    def on_deleted(self, event):
        self._process(event)

    def _process(self, event):
        if event.is_directory:
            return
            
        path = Path(event.src_path).resolve()
        
        # 1. Filter Ignores
        if any(p in path.parts for p in IGNORES):
            return
        if path.name.startswith('.'):
            return
            
        # 2. Filter Extension (Palantir focus)
        if path.suffix not in {'.py', '.md', '.ts', '.js', '.json', '.html', '.css', '.toml'}:
            return
            
        # 3. Trigger Branch Update (O(log N))
        logger.info(f"📁 [WATCHER]: Change detected in {path.name}. Updating Context...")
        print(f"📁 [WATCHER]: Change in {path.name}") # Print for CLI visibility
        try:
            update_branch(self.root_path, path)
            logger.info(f"✅ [WATCHER]: Context Re-Synchronized.")
            print(f"✅ [WATCHER]: Context Re-Synchronized.")
        except Exception as e:
            logger.error(f"❌ [WATCHER]: Update failed: {e}")
            print(f"❌ [WATCHER]: Update failed: {e}")

def start_watcher(root_path: Path):
    """Starts the Sovereign Watcher in a background thread."""
    event_handler = SovereignHandler(root_path)
    observer = Observer()
    observer.schedule(event_handler, str(root_path), recursive=True)
    observer.start()
    
    logger.info(f"🛡️ [SOVEREIGN WATCHER]: Active on {root_path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    import sys
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    start_watcher(root)
