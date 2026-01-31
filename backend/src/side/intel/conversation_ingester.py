"""
Conversation Ingester (Multi-Provider).

Watches multiple sources (Antigravity, Cursor) for intent signals.
"""

import asyncio
import logging
from typing import List, Set, Optional
from pathlib import Path

from side.intel.conversation_session import ConversationSession, IntentCategory
from side.storage.simple_db import SimplifiedDatabase
from side.intel.sources.base import IntentSource
from side.intel.sources.antigravity import AntigravitySource
from side.intel.sources.cursor import CursorSource

logger = logging.getLogger(__name__)

class ConversationIngester:
    """
    Ingests intent from multiple providers.
    """

    def __init__(self, db: SimplifiedDatabase | None = None, brain_path: Path | None = None):
        self.db = db or SimplifiedDatabase()
        self.store = self.db.intent_fusion
        
        # Initialize Sources
        self.sources: List[IntentSource] = [
            AntigravitySource(brain_path),
            CursorSource()
        ]
        
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._processed_sessions: Set[str] = set()

    async def start(self) -> None:
        """Start watching."""
        if self._running: return
        self._running = True
        logger.info(f"🧠 [INGESTER]: Watching sources: {[type(s).__name__ for s in self.sources]}")
        self._task = asyncio.create_task(self._watch_loop())

    async def stop(self) -> None:
        """Stop watching."""
        self._running = False
        if self._task:
            self._task.cancel()
            try: await self._task
            except asyncio.CancelledError: pass

    async def ingest_all(self) -> None:
        """One-off scan of all sources."""
        for source in self.sources:
            nodes = source.scan_nodes()
            count = 0
            for node in nodes:
                if node["node_id"] not in self._processed_sessions:
                    await self._process_node(node)
                    count += 1
            logger.info(f"🧠 [INGESTER]: Ingested {count} sessions from {type(source).__name__}")

    async def _watch_loop(self) -> None:
        """Poller loop."""
        while self._running:
            try:
                await self.ingest_all() # Reuse logic for now
                await asyncio.sleep(5.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in ingester loop: {e}")
                await asyncio.sleep(10.0)

    async def _process_node(self, node: dict) -> None:
        """Process a normalized node dict."""
        try:
            session_id = node["node_id"]
            raw_intent = node["raw_intent"]
            started_at = node["started_at"]
            source = node.get("source", "UNKNOWN")
            
            # Simple keyword extraction
            keywords = self._extract_keywords(raw_intent)
            category = self._classify_intent(raw_intent)
            
            # Create Session
            session = ConversationSession(
                session_id=session_id,
                project_id=f"{source.lower()}-{session_id[:8]}", # Namespaced project ID
                started_at=started_at,
                raw_intent=raw_intent,
                intent_vector=keywords,
                intent_category=category
            )
            
            self.store.save_session_dict(session.to_dict())
            self._processed_sessions.add(session_id)
            logger.info(f"🧠 [INGESTER]: Ingested {session_id[:8]} from {source}")
            
        except Exception as e:
            logger.error(f"Failed to process node {node.get('node_id')}: {e}")

    def _extract_keywords(self, text: str) -> List[str]:
        stopwords = {"the", "a", "an", "to", "in", "for", "of", "with", "is", "this"}
        return [w for w in text.lower().split() if w not in stopwords and len(w) > 3]

    def _classify_intent(self, text: str) -> IntentCategory:
        lower = text.lower()
        if "debug" in lower or "fix" in lower: return IntentCategory.DEBUGGING
        if "implement" in lower or "add" in lower or "create" in lower: return IntentCategory.IMPLEMENTING
        if "rewrite" in lower or "refactor" in lower: return IntentCategory.REFACTORING
        return IntentCategory.UNKNOWN
