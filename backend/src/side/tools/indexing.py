"""
Indexing tool handler for Side.
Handles: reindex_dna (Context Densification)
"""

import logging
import asyncio
from pathlib import Path
from typing import Any

from side.intel.auto_intelligence import ContextService
from side.storage.modules.base import ContextEngine

from side.utils.paths import get_repo_root

logger = logging.getLogger(__name__)

async def handle_reindex_dna(arguments: dict[str, Any]) -> str:
    """
    Handle reindex_dna tool (Context Densification).
    """
    path_str = arguments.get("path")
    if path_str:
        project_path = Path(path_str).resolve()
    else:
        project_path = get_repo_root()
    
    # [ECONOMY]: Charge for Context Densification (15 SUs)
    from side.tools.core import get_database
    db = get_database()
    project_id = db.get_project_id()
    
    if not db.identity.charge_action(project_id, "CONTEXT_BOOST"):
        return "🚫 [INSUFFICIENT FUNDS]: Context Densification requires 15 SUs. Run 'side login' or upgrade."
    
    print(f"🧠 [CONTEXT DENSIFICATION]: Building the codebase architecture at {project_path}...")
    
    intel = ContextService(project_path, engine)
    
    try:
        # Run the multi-threaded feed (tree-sitter indexing)
        graph = await intel.feed()
        
        node_count = 0
        if isinstance(graph, dict) and 'stats' in graph:
            node_count = graph['stats'].get('nodes', 0)
        
        return f"✅ [SUCCESS]: Context Densification complete. Processed {node_count} nodes into the Strategic Memory."
    except Exception as e:
        logger.exception(f"Indexing failed: {e}")
        return f"🚫 [ERROR]: Context Densification failed: {str(e)}"
