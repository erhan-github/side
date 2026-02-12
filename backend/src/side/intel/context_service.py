from __future__ import annotations
import logging
import time
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from side.models.core import Finding
from side.storage.modules import ContextEngine
from side.utils.crypto import shield

if TYPE_CHECKING:
    from side.storage.modules import ContextEngine


from side.intel.connector import Connector
from side.intel.tree_indexer import run_context_scan
from side.intel.code_monitor import CodeMonitor
from side.intel.session_analyzer import SessionAnalyzer
from side.intel.handlers.topology import CodeIndexer
from side.intel.handlers.feeds import HistoryAnalyzer
from side.intel.handlers.janitor import MaintenanceService
from side.intel.handlers.context import PromptBuilder
from side.services.doc_scanner import DocScanner

logger = logging.getLogger(__name__)

from side.services.base import LifecycleComponent

class ContextService(LifecycleComponent):
    """
    Orchestrates system intelligence, delegating to specialized handlers.
    Implements LifecycleComponent for deterministic orchestration.
    """

    def __init__(self, project_path: Path, engine: ContextEngine, buffer=None):
        super().__init__(name="auto_intel")
        from side.storage.modules.mmap_store import MmapStore
        
        self.project_path = project_path
        self.engine = engine
        self.plans = engine.plans
        self.audits = engine.audits
        self.buffer = buffer
        
        self.mmap = MmapStore(project_path)
        
        # Brain Path Strategy
        env_brain = os.getenv("SIDE_BRAIN_PATH")
        default_brain = Path.home() / ".side" / "brain"
        self.brain_path = Path(env_brain) if env_brain else default_brain

        # Initialize Handlers
        self.indexer = CodeIndexer(self.project_path, self.engine, self.brain_path, self.buffer)
        self.history = HistoryAnalyzer(self.project_path, self.engine, self.brain_path, self.plans)
        self.janitor = MaintenanceService(self.plans, self.engine)
        self.orchestrator = PromptBuilder(self.project_path, self.engine, self.plans)
        self.doc_scanner = DocScanner(self.plans)

    async def get_ai_memory_snapshot(self) -> str:
        """Retrieves the official AI Memory for the project."""
        project_id = self.engine.get_project_id(self.project_path)
        return self.orchestrator.get_ai_memory()

    async def setup(self, force: bool = False) -> None:
        """Initializes the intelligence context with high-integrity caching."""
        start_time = time.time()
        project_id = self.engine.get_project_id(self.project_path)
        
        # 1. Try Cache First
        if not force:
            cache = self.engine.operational.get_fingerprint(project_id)
            if cache:
                logger.info("🧠 [CONTEXT]: Restored state from AI Memory cache.")
                await self.sync_checkpoint()
                return

        logger.info("🔭 [CONTEXT]: Cache miss. Initiating Deep Context Scan...")
        run_context_scan(self.project_path, schema_store=self.engine.schema)
        
        # 2. Persist to Cache
        fingerprint = self.orchestrator.get_ai_memory()
        stats = self._get_project_stats()
        self.engine.operational.save_fingerprint(project_id, {"dna": fingerprint}, stats)
        
        logger.info(f"✨ [CONTEXT]: Scan completed and cached in {time.time() - start_time:.2f}s.")
        await self.sync_checkpoint()
        await self._sync_mmap_patterns()

    async def start(self) -> None:
        """The main intelligence feed loop."""
        await self.feed()

    async def teardown(self) -> None:
        """Standard teardown for intelligence state."""
        logger.info("Tearing down ContextService...")
        await self.sync_checkpoint()

    async def feed(self):
        """Original feed logic, now wrapped by start()."""
        # Placeholder for the actual feed implementation if it exists elsewhere 
        # or logic being moved here.
        pass

    async def sync_checkpoint(self):
        """Serializes current state to local telemetry."""
        root_index_path = self.project_path / ".side" / "local.json"
        local_data = {}
        if root_index_path.exists():
            try:
                raw_data = shield.unseal_file(root_index_path)
                local_data = json.loads(raw_data)
            except Exception as e:
                logger.warning(f"Failed to read local index: {e}")
        
        stats = self._get_project_stats()
        
        from side.models.project import ContextSnapshot, ProjectStats, DNA
        snapshot_obj = ContextSnapshot(
            stats=ProjectStats(
                nodes=stats["nodes"],
                total_lines=stats["total_lines"]
            ),
            dna=DNA(
                signals=local_data.get("dna", {}).get("signals", [])
            )
        )
        
        metadata_file = self.project_path / ".side" / "project_metadata.json"
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        shield.seal_file(metadata_file, snapshot_obj.model_dump_json(indent=2))
        return snapshot_obj

    def _get_project_stats(self) -> Dict[str, int]:
        """Deep Scan: Fast directory traversal."""
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
                                except Exception as e:
                                    logger.debug(f"Deep Scan: Could not read {path}: {e}")
            except (PermissionError, FileNotFoundError) as e:
                logger.debug(f"Deep Scan: Path inaccessible {curr}: {e}")
        return {"nodes": nodes, "total_lines": total_lines}

    async def _sync_mmap_patterns(self):
        """Syncs public patterns to Mmap Store."""
        try:
            patterns = self.plans.list_public_patterns()
            fragments = []
            for p in patterns:
                sig_hash = p.get('signal_hash')
                p_id = p.get('id')
                if sig_hash is not None and p_id:
                    try:
                        import uuid
                        uuid_obj = uuid.UUID(p_id)
                        fragments.append((sig_hash, uuid_obj.bytes))
                    except (ValueError, TypeError):
                        continue
            
            if fragments:
                 self.mmap.sync_from_ledger(fragments)
        except Exception as e:
            logger.warning(f"MMAP Sync Failed: {e}")

    # --- Delegated Methods ---

    async def incremental_feed(self, file_path: Path):
        await self.history.incremental_feed(file_path)

    async def historic_feed(self, months: int = 3) -> List[Dict[str, Any]]:
        return await self.history.historic_feed(months)

    async def autonomous_janitor(self, throttle_hook=None) -> int:
        return await self.janitor.autonomous_janitor(throttle_hook)

    async def prune_patterns(self) -> int:
        return await self.janitor.autonomous_janitor()

    def gather_context(self, active_file: str = None, topic: str = None, include_code: bool = True) -> str:
        return self.orchestrator.gather_context(active_file, topic, include_code)

    def get_surgical_context(self, query: str, limit: int = 3) -> str:
        return self.orchestrator.get_surgical_context(query, limit)

    def get_episodic_context(self, limit: int = 15) -> str:
        return self.orchestrator.get_episodic_context(self.audits, limit)

    def get_condensed_dna(self) -> str:
        return self.indexer.get_condensed_dna()

    async def optimize_weights(self) -> dict:
        """Regenerate the context cache."""
        from side.intel.code_monitor import CodeMonitor
        monitor = CodeMonitor(self.audits)
        new_facts = await monitor.distill_observations(self.engine.get_project_id(), limit=20)
        
        from side.utils.context_cache import ContextCache
        cache = ContextCache(self.project_path, self.engine)
        cache_data = cache.generate(force=True)
        
        logger.info(f"Optimized context cache (Facts: +{new_facts})")
        return cache_data

    def enrich_system_prompt(self, base_prompt: str, context: str) -> str:
        return f"{base_prompt}\n\n=== CONTEXT ===\n{context}\n===============\n"

    def _get_ai_memory(self) -> str:
        return self.orchestrator.get_git_status()

    # --- Event-Driven Architecture ---

    def attach_to_event_bus(self, event_bus):
        """
        Connects intelligence to system events.
        """
        from side.utils.event_optimizer import FrictionPoint, EventPriority, Event

        @event_bus.on(FrictionPoint.FILE_STRUCTURE_CHANGE, EventPriority.HIGH)
        async def handle_structure_change(event: Event):
            path = Path(event.payload.get("path"))
            event_type = event.payload.get("event_type")
            
            logger.info(f"Structure change detected: {path.name} ({event_type})")
            
            if event_type == "deleted":
                await self.indexer.drop_single(path)
                logger.debug(f"Context purged for deleted file: {path.name}")
            elif event_type == "created":
                await self.indexer.scan_single(path)
                
            if path.suffix in {'.py', '.ts', '.tsx', '.js', '.md'}:
                await self.orchestrator.refresh_context_for_file(path)

        @event_bus.on(FrictionPoint.GIT_COMMIT, EventPriority.NORMAL)
        async def handle_commit(event: Event):
            message = event.payload.get("message")
            logger.info(f"Analyzing commit: {message}")
            await self.history.process_latest_commit()

