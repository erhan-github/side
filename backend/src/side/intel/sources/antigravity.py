"""
Antigravity Intent Source.

Provides Antigravity session data via IntentSource protocol.
"""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone
import json

from side.intel.sources.base import IntentSource
from side.intel.connector import Connector

class AntigravitySource(IntentSource):
    """
    Wraps Connector to read ~/.gemini/antigravity/brain nodes.
    """
    
    def __init__(self, brain_path: Path | None = None):
        if brain_path is None:
            brain_path = Path.home() / ".gemini" / "antigravity" / "brain"
        self.connector = Connector(brain_path)
        self.brain_path = brain_path

    def scan_nodes(self) -> List[Dict[str, Any]]:
        connector_nodes = self.connector.scan_nodes()
        results = []
        
        for node in connector_nodes:
            # Translate Bridge format to IntentSource format
            session_id = node.get("node_id")
            
            # Extract raw intent from metadata (manual read again for high fidelity check)
            # Or rely on bridge if we updated it. 
            # Sticking to the previous logic which worked:
            
            session_dir = self.brain_path / session_id
            meta_path = session_dir / "task.md.metadata.json"
            
            raw_intent = ""
            started_at = datetime.now(timezone.utc)
            
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text())
                    raw_intent = meta.get("summary", "")
                    if "updatedAt" in meta:
                         ts = meta["updatedAt"].replace("Z", "+00:00")
                         started_at = datetime.fromisoformat(ts)
                except:
                    pass
            
            # If no meta summary, check tasks
            if not raw_intent and node.get("tasks"):
                 raw_intent = f"Task: {node['tasks'][0].get('id')}"

            if raw_intent:
                results.append({
                    "node_id": session_id,
                    "raw_intent": raw_intent,
                    "started_at": started_at,
                    "source": "ANTIGRAVITY",
                    "metadata": node
                })
                
        return results
