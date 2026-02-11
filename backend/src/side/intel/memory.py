import logging
import uuid
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from side.storage.modules.strategy import DecisionStore

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    The Hippocampus. Manages store and recall of strategic facts.
    Now backed by SQLite (DecisionStore) for atomic, no-fat persistence.
    """
    def __init__(self, registry: DecisionStore, project_id: str = "default"):
        self.registry = registry
        self.project_id = project_id
        
    def memorize(self, fact: str, tags: List[str] = None, metadata: Dict = None):
        """Commit a fact to long-term memory via the Strategic Store."""
        mid = str(uuid.uuid4())
        self.registry.save_fact(
            fact_id=mid,
            project_id=self.project_id,
            content=fact,
            tags=tags,
            metadata=metadata
        )
        logger.info(f"🧠 [MEMORY] Stored in SQLite: {fact[:50]}... ({mid})")
        return mid
        
    def recall(self, query: str, limit: int = 5) -> str:
        """Recall relevant facts for a query from the Strategic Store."""
        memories = self.registry.recall_facts(
            query=query,
            project_id=self.project_id,
            limit=limit
        )
        
        if not memories:
            return ""
            
        summary = "🧠 [RECALLED CONTEXT]:\n"
        for m in memories:
            summary += f"- {m['content']} (Tags: {m['tags']})\n"
        return summary
