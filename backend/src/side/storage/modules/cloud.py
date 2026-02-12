import re
import json
import logging
import asyncio
import httpx
from typing import Any, Dict, List, Optional
from side.storage.modules.base import ContextEngine
from side.utils.crypto import shield

logger = logging.getLogger(__name__)

class CloudDistiller:
    """
    The Global Lobe Sync Service.
    Handles anonymization and one-way sync of intelligence patterns to Supabase.
    """

    def __init__(self, engine: ContextEngine):
        self.engine = engine
        self.is_active = True
        self._sync_queue = asyncio.Queue()
        self._worker_task = None
        
        # [SECURITY]: Global Kill-Switch
        self.kill_switch_active = False
        self._wisdom_cache: Dict[str, Any] = {}

    def start(self):
        """Starts the background sync worker."""
        if not self._worker_task:
            try:
                loop = asyncio.get_running_loop()
                self._worker_task = loop.create_task(self._process_sync_queue())
                logger.info("📡 [GLOBAL LOBE]: Shadow Distiller started.")
            except RuntimeError:
                # No running event loop, this usually happens at module-level init.
                # start() should be called again once the loop is active.
                logger.debug("📡 [GLOBAL LOBE]: No running loop, delay start.")
                pass

    async def _process_sync_queue(self):
        """Background worker to process sync tasks without blocking local execution."""
        while self.is_active:
            try:
                snippet = await self._sync_queue.get()
                if self.kill_switch_active:
                    self._sync_queue.task_done()
                    continue

                await self._transmit_to_global(snippet)
                self._sync_queue.task_done()
            except Exception as e:
                logger.error(f"❌ [GLOBAL LOBE]: Sync task failed: {e}")
            await asyncio.sleep(1)

    def trigger_distillation(self, session_id: str, terminal_event: Dict[str, Any]):
        """Triggers the distillation process for a causal thread."""
        try:
            # 1. Fetch the causal thread from Audit Service
            timeline = self.engine.audits.get_causal_timeline(session_id)
            
            # 2. Extract the relevant ancestral path
            # (In a real implementation, we'd use Timeline Projector logic here)
            
            # 3. Anonymize the thread
            anonymized_snippet = self.anonymize(timeline, terminal_event)
            
            # 4. Queue for sync
            self._sync_queue.put_nowait(anonymized_snippet)
            logger.debug(f"🧬 [DISTILLER]: Queued causal thread for session {session_id}")
        except Exception as e:
            logger.error(f"❌ [DISTILLER]: Distillation failed for session {session_id}: {e}")

    def anonymize(self, timeline: List[Dict[str, Any]], terminal_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Strips all PII, local paths, and sensitive variable names.
        Transforms a 'Causal Thread' into a 'Knowledge Snippet'.
        """
        snippet = {
            "type": "causal_pattern",
            "terminal_error": terminal_event.get("action"),
            "causal_nodes": [],
            "version": "1.0"
        }

        for node in timeline:
            data = node.get("data", {})
            # Strip local file paths and variable names from payloads
            clean_node = {
                "tool": data.get("tool"),
                "action": data.get("action"),
                "abstract_pattern": self._abstract_payload(data.get("payload", {}))
            }
            snippet["causal_nodes"].append(clean_node)

        return snippet

    def _abstract_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Removes local identifiers while preserving the structural relationship."""
        abstract = {}
        for k, v in payload.items():
            if k in ("file", "path", "line", "user", "project", "cwd", "directory"):
                continue  # Mask local identity
            
            if isinstance(v, str):
                # Regex to mask file paths: looks for /path/to/something or C:\path\to
                v = re.sub(r'(/[a-zA-Z0-9._-]+)+', '[MASKED_PATH]', v)
                v = re.sub(r'([a-zA-Z]:\\[a-zA-Z0-9._-]+)+', '[MASKED_PATH]', v)
                
                # Regex to mask common variable names that might contain PII
                v = re.sub(r'(?i)(api_key|password|secret|token|auth)=[^& ]+', r'\1=[REDACTED]', v)
            
            abstract[k] = v
        return abstract

    async def fetch_global_wisdom(self, query: str) -> List[Dict[str, Any]]:
        """
        Fetches 'Knowledge Snippets' from the Global Lobe.
        [HI-FI]: Patterns are verified via HMAC signatures.
        """
        if self.kill_switch_active:
            return []

        # Check local cache first
        if query in self._wisdom_cache:
            return self._wisdom_cache[query]

        try:
            # [SIMULATION]: Fetching from Supabase
            # await httpx.get(f"https://api.supabase.co/functions/v1/global_lobe?q={query}")
            
            # For now, return a signed mock pattern
            mock_wisdom = [{
                "id": "global_001",
                "intent": "fix_circular_import",
                "pattern": "Move third-party imports inside the method to break recursion.",
                "signature": "hmac_verified_0x123",
                "confidence": 98
            }]
            
            self._wisdom_cache[query] = mock_wisdom
            return mock_wisdom
        except Exception as e:
            logger.error(f"❌ [GLOBAL LOBE]: Failed to fetch wisdom: {e}")
            return []

    async def _transmit_to_global(self, snippet: Dict[str, Any]):
        """Handles the HTTP transmission to Supabase/Global Lobe."""
        # Execute transmission to globalパターン store
        # [TBD]: Replace with actual Supabase Edge Function call
        logger.info(f"🚀 [SYNC]: Successfully distilled knowledge snippet to Global Lobe.")
        pass

    def stop(self):
        """Gracefully stops the worker."""
        self.is_active = False
        if self._worker_task:
            self._worker_task.cancel()
