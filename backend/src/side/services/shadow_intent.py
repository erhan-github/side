import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict
from side.services.unified_buffer import UnifiedBuffer

logger = logging.getLogger(__name__)

class ShadowIntentService:
    """
    [SHADOW_INTENT]: Captures the 'Lost Context' of development.
    Listens for temporary buffer updates from the IDE and transmutes 
    them into 'Negative Momentum' signals if they are discarded.
    """
    
    def __init__(self, buffer: UnifiedBuffer):
        self.buffer = buffer
        self._last_buffers: Dict[str, str] = {} # path -> content
        self._running = False

    async def start(self):
        self._running = True
        logger.info("🌑 [SHADOW_INTENT]: Listening for Ghost Intent...")

    async def ingest_shadow_buffer(self, file_path: str, content: str):
        """
        Receives a 'Snapshot' of a file while a user is typing (before save).
        """
        if not self._running:
            return

        last_content = self._last_buffers.get(file_path, "")
        
        # Calculate Delta (Simple Levenshtein or just length/content check for now)
        # In V4 we will use full Semantic Diffing on the shadow buffer.
        if content != last_content:
            await self.buffer.ingest("activity", {
                "tool": "shadow_intent",
                "action": "buffer_update",
                "payload": {
                    "path": file_path,
                    "length_delta": len(content) - len(last_content),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "momentum": 0.3
                }
            })
            self._last_buffers[file_path] = content

    async def notify_save(self, file_path: str, final_content: str):
        """
        Triggered when a file is actually saved. 
        Calculates the 'Rejection Delta' (what was in the shadow but didn't make it to save).
        """
        shadow_content = self._last_buffers.get(file_path, "")
        if shadow_content and shadow_content != final_content:
            # We found 'Shadow Intent' that was rejected!
            await self.buffer.ingest("rejection", {
                "project_id": "global",
                "path": file_path,
                "shadow_snapshot": shadow_content[:2000], # Preview
                "final_snapshot": final_content[:2000],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "strategic_weight": 0.8 # Rejections are high-value
            })
            
        # Reset shadow for this file
        if file_path in self._last_buffers:
            del self._last_buffers[file_path]

    async def stop(self):
        self._running = False
        logger.info("🌑 [SHADOW_INTENT]: Ghost Listener Offline.")
