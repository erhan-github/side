"""
Base Intent Source Protocol.

Defines the contract for ingesting intent from different providers (Antigravity, Cursor, etc.).
"""

from typing import Protocol, List, Dict, Any, Optional
from datetime import datetime

class IntentSource(Protocol):
    """Protocol for intent sources."""
    
    def scan_nodes(self) -> List[Dict[str, Any]]:
        """
        Scans for session nodes.
        Returns a list of dicts with:
        - node_id: unique session ID
        - raw_intent: the summary string
        - started_at: datetime
        - ... other metadata
        """
        ...
