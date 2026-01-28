import json
import logging
import uuid
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from side.utils.crypto import shield

logger = logging.getLogger(__name__)

class MemoryPersistence:
    """
    Sovereign JSON-based storage for Long-Term Memory.
    Acts as a 'Lite' vector store before upgrading to Chroma/pgvector.
    """
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        if not self.storage_path.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self._save([])

    def _load(self) -> List[Dict[str, Any]]:
        try:
            # USE SHIELD TO DECRYPT MEMORY
            raw_data = shield.unseal_file(self.storage_path)
            return json.loads(raw_data)
        except Exception:
            return []

    def _save(self, data: List[Dict[str, Any]]):
        # USE SHIELD TO ENCRYPT MEMORY
        shield.seal_file(self.storage_path, json.dumps(data, indent=2))

    def add(self, content: str, tags: List[str] = None, metadata: Dict = None) -> str:
        data = self._load()
        memory_id = str(uuid.uuid4())
        entry = {
            "id": memory_id,
            "content": content,
            "tags": tags or [],
            "metadata": metadata or {},
            "timestamp": time.time(),
            # Future: "embedding": [...] 
        }
        data.append(entry)
        self._save(data)
        return memory_id

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fuzzy recall.
        TODO: Upgrade to semantic search (Vector Embeddings) in Phase 2.
        """
        data = self._load()
        results = []
        query_terms = query.lower().split()
        
        for entry in data:
            content = entry["content"].lower()
            # Simple scoring: How many terms match?
            score = sum(1 for term in query_terms if term in content)
            
            # Boost by tags
            for tag in entry["tags"]:
                if tag.lower() in query_terms:
                    score += 2
            
            if score > 0:
                entry["score"] = score
                results.append(entry)
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

class MemoryManager:
    """
    The Hippocampus. Manages store and recall of strategic facts.
    """
    def __init__(self, project_path: Path):
        self.persistence = MemoryPersistence(project_path / ".side" / "memory.json")
        
    def memorize(self, fact: str, tags: List[str] = None):
        """Commit a fact to long-term memory."""
        mid = self.persistence.add(fact, tags)
        logger.info(f"🧠 [MEMORY] Stored: {fact[:50]}... ({mid})")
        return mid
        
    def recall(self, query: str) -> str:
        """Recall relevant facts for a query."""
        memories = self.persistence.search(query)
        if not memories:
            return ""
            
        summary = "🧠 [RECALLED CONTEXT]:\n"
        for m in memories:
            summary += f"- {m['content']} (Tags: {m['tags']})\n"
        return summary
