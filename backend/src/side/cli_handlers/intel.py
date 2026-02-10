import asyncio
import time
from pathlib import Path
from .utils import ux, get_engine

def handle_index(args):
    """Manual Indexer."""
    ux.display_status("Analyzing Project Structure...", level="info")
    from side.intel.auto_intelligence import ContextService
    
    path = Path(args.path).resolve()
    intel = ContextService(path, engine=get_engine())
    
    # Run the Feed
    graph = asyncio.run(intel.feed())
    
    ux.display_header("Index Complete")
    if 'stats' in graph:
        ux.display_status(f"Processed {graph['stats'].get('nodes', 0)} nodes.", level="success")
    else:
        ux.display_status("Context Updated.", level="success")
    ux.display_status("Identity successfully projected to: .side/project.json", level="info")
    ux.display_footer()

def handle_watch(args):
    """Real-time File Watcher."""
    from side.services.file_watcher import FileWatcher
    from side.intel.auto_intelligence import ContextService
    
    ux.display_status("Active Monitoring Engaged...", level="info")
    path = Path(args.path).resolve()
    intel = ContextService(path, engine=get_engine())
    
    watcher = FileWatcher(path, on_change=lambda files: asyncio.run(intel.incremental_feed(list(files)[0] if files else path)))
    try:
        asyncio.run(watcher.start())
        # Keep alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        asyncio.run(watcher.stop())
        ux.display_status("Watcher Disengaged.", level="warning")

def handle_strategy(args):
    ux.display_status(f"Analyzing '{args.question}'...", level="info")
    from side.tools import strategy
    
    result = asyncio.run(strategy.handle_decide({
        "question": args.question,
        "context": "CLI User Request"
    }))
    
    ux.display_header("Strategic Analysis")
    ux.display_panel(result, style="cyan")
    ux.display_footer()

def handle_maintenance(args):
    """System Maintenance."""
    engine = get_engine()
    engine.perform_maintenance()
    ux.display_status("System maintenance complete. Context VACUUMed and Backed up.", level="success")
