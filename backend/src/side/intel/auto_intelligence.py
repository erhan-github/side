from __future__ import annotations
import logging
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from side.intel.memory import MemoryManager
from side.intel.bridge import BrainBridge
from side.utils.crypto import shield
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from side.storage.modules.base import ContextEngine

import os
from side.intel.handlers.topology import DNAHandler
from side.intel.handlers.feeds import FeedHandler
from side.intel.handlers.janitor import JanitorHandler
from side.intel.handlers.context import ContextHandler

logger = logging.getLogger(__name__)

class AutoIntelligence:
    """
    System Context Orchestrator [Tier-3].
    Delegates specialized logic to handlers:
    - DNAHandler: Structural Truth & Indexing.
    - FeedHandler: Historical & Incremental Sync.
    - JanitorHandler: Cache Decay & Pruning.
    - ContextHandler: High-Fidelity Prompt Construction.
    """

    def __init__(self, project_path: Path, engine: ContextEngine, buffer=None):
        import os
        from side.storage.modules.mmap_store import MmapStore
        
        self.project_path = project_path
        self.engine = engine
        self.strategic = engine.strategic
        self.forensic = engine.audit
        self.buffer = buffer
        
        self.mmap = MmapStore(project_path)
        self.memory = MemoryManager(self.strategic, project_id=self.engine.get_project_id())
        
        # [KAR-4]: Universal Brain Path Discovery
        env_brain = os.getenv("SIDE_BRAIN_PATH")
        antigravity_brain = Path.home() / ".gemini" / "antigravity" / "brain"
        self.brain_path = Path(env_brain) if env_brain else antigravity_brain

        # Initialize Handlers
        self.dna_handler = DNAHandler(project_path, engine, self.brain_path, buffer)
        self.feed_handler = FeedHandler(project_path, engine, self.brain_path, self.strategic)
        self.janitor_handler = JanitorHandler(self.strategic, engine)
        self.context_handler = ContextHandler(project_path, engine, self.strategic, self.memory)

    async def setup(self):
        """Initializes the intelligence context via DNA and Feed handlers."""
        from side.intel.fractal_indexer import run_fractal_scan
        from side.storage.modules.identity import IdentityStore
        
        project_id = self.engine.get_project_id()
        identity = IdentityStore(self.engine)
        
        if not identity.charge_action(project_id, "CONTEXT_BOOST"):
             logger.warning(f"⚠️ [ECONOMY]: Insufficient SUs for Context Boost (Index).")
        
        start_time = time.time()
        logger.info("🧠 [BRAIN]: Initiating Parallel Fractal Context Scan...")
        run_fractal_scan(self.project_path, ontology_store=self.engine.ontology)
        logger.info(f"🧠 [BRAIN]: Scan completed in {time.time() - start_time:.2f}s.")
        
        config = await self.sync_checkpoint()
        await self._sync_mmap_patterns()
        return config

    async def sync_checkpoint(self):
        """[SERIALIZATION PROTOCOL]: Serializes the current 'Weights' to local telemetry."""
        root_index_path = self.project_path / ".side" / "local.json"
        local_data = {}
        if root_index_path.exists():
            try:
                raw_data = shield.unseal_file(root_index_path)
                local_data = json.loads(raw_data)
            except Exception as e:
                logger.warning(f"Failed to read local index: {e}")
        
        # [PERFORMANCE]: Optimized Stats Scan (Batch 1 Remediation)
        stats = self._get_project_stats()
        
        from side.models.brain import ContextSnapshot, BrainStats, DNA
        snapshot_obj = ContextSnapshot(
            stats=BrainStats(
                nodes=stats["nodes"],
                total_lines=stats["total_lines"]
            ),
            dna=DNA(
                signals=local_data.get("dna", {}).get("signals", [])
            )
        )
        
        metadata_file = self.project_path / ".side" / "project_metadata.json"
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        # Only seal if meaningful data exists
        shield.seal_file(metadata_file, snapshot_obj.model_dump_json(indent=2))
        logger.debug("💾 [CHECKPOINT]: Project metadata serialized (STRICT).")
        return snapshot_obj

    def _get_project_stats(self) -> Dict[str, int]:
        """Deep Scan: Fast directory traversal with early pruning."""
        from side.services.ignore import ProjectIgnore
        ignore = ProjectIgnore(self.project_path)
        nodes = 0
        total_lines = 0
        
        stack = [self.project_path]
        while stack:
            curr = stack.pop()
            try:
                with os.scandir(curr) as it:
                    for entry in it:
                        path = Path(entry.path)
                        if ignore.should_ignore(path):
                            continue
                        
                        nodes += 1
                        if entry.is_dir():
                            stack.append(path)
                        elif entry.is_file():
                            if path.suffix in ('.py', '.js', '.ts', '.tsx', '.css', '.html', '.md', '.json', '.yaml', '.yml'):
                                try:
                                    with open(path, 'rb') as f:
                                        total_lines += sum(1 for _ in f)
                                except Exception:
                                    pass
            except (PermissionError, FileNotFoundError):
                continue
        return {"nodes": nodes, "total_lines": total_lines}

    async def _sync_mmap_patterns(self):
        """Syncs public patterns to Mmap Store."""
        try:
            patterns = self.strategic.list_public_patterns()
            fragments = []
            for p in patterns:
                sig_hash = p.get('signal_hash')
                p_id = p.get('id')
                if sig_hash is not None and p_id:
                    import uuid
                try:
                    import uuid
                    uuid_obj = uuid.UUID(p_id)
                    fragments.append((sig_hash, uuid_obj.bytes))
                except (ValueError, TypeError):
                    continue
            
            if fragments:
                 self.mmap.sync_from_ledger(fragments)
                 logger.info("✨ [CONTEXT]: Technical timeline synced.")
        except Exception as e:
            logger.warning(f"MMAP Sync Failed: {e}")

    # --- Delegated Methods ---

    async def incremental_feed(self, file_path: Path):
        await self.feed_handler.incremental_feed(file_path)

    async def historic_feed(self, months: int = 3) -> List[Dict[str, Any]]:
        return await self.feed_handler.historic_feed(months)

    async def autonomous_janitor(self, throttle_hook=None) -> int:
        return await self.janitor_handler.autonomous_janitor(throttle_hook)

    async def prune_patterns(self) -> int:
        return await self.janitor_handler.autonomous_janitor()

    def gather_context(self, active_file: str = None, topic: str = None, include_code: bool = True) -> str:
        return self.context_handler.gather_context(active_file, topic, include_code)

    def get_surgical_context(self, query: str, limit: int = 3) -> str:
        return self.context_handler.get_surgical_context(query, limit)

    def get_episodic_context(self, limit: int = 15) -> str:
        return self.context_handler.get_episodic_context(self.forensic, limit)

    def get_condensed_dna(self) -> str:
        return self.dna_handler.get_condensed_dna()

    async def optimize_weights(self) -> dict:
        from side.intel.observer import StrategicObserver
        observer = StrategicObserver(self.forensic)
        new_facts = await observer.distill_observations(self.engine.get_project_id(), limit=20)
        
        from side.utils.context_cache import ContextCache
        cache = ContextCache(self.project_path, self.engine)
        cache_data = cache.generate(force=True)
        
        logger.info(f"⚓ [WEIGHTS]: Optimized context cache (Facts: +{new_facts})")
        return cache_data

    def enrich_system_prompt(self, base_prompt: str, context: str) -> str:
        return f"{base_prompt}\n\n=== STRATEGIC CONTEXT ===\n{context}\n==========================\n"

    def _get_operational_reality(self) -> str:
        return self.context_handler._get_operational_reality()
