import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from side.storage.modules.base import ContextEngine
from side.storage.modules.chronos import ChronosStore
from side.storage.modules.transient import OperationalStore

logger = logging.getLogger(__name__)

class SynergyEngine:
    """
    The 'Collective Intelligence' Layer.
    Identifies shared signals between Projects and harvests Technical Patterns.
    """
    def __init__(self, project_path: Path, buffer=None):
        self.project_path = Path(project_path).resolve()
        self.engine = ContextEngine()
        self.strategic = ChronosStore(self.engine)
        self.operational = OperationalStore(self.engine)
        self.buffer = buffer
        self.project_id = ContextEngine.get_project_id(self.project_path)

    def identify_signals(self) -> List[str]:
        """Harvest architectural signals from the current project."""
        signals = []
        # Signal 1: Core Frameworks (Detected via deps or folder structure)
        if (self.project_path / "web").exists(): signals.append("React/NextJS")
        if (self.project_path / "backend" / "src" / "side").exists(): signals.append("Core/Sidelith")
        if (self.project_path / "package.json").exists(): signals.append("NodeJS")
        
        # Signal 2: Database Patterns
        if (self.project_path / "supabase").exists(): signals.append("Supabase")
        
        return signals

    async def harvest_mesh_patterns(self):
        """
        Pulls relevant technical patterns from other nodes using Sparse Semantic Similarity.
        """
        from side.utils.hashing import sparse_hasher
        from side.storage.modules.identity import IdentityStore
        
        # 1. Check Identity Boundaries
        identity = IdentityStore(self.engine)
        profile = identity.get_profile(self.project_id)
        
        if profile and profile.get("is_airgapped"):
            logger.warning(f"🛡️ [SYNERGY]: Project {self.project_id} is AIRGAPPED. Mesh sync disabled.")
            return 0
            
        design_pattern = profile.get("design_pattern", "declarative") if profile else "declarative"
        
        signals = self.identify_signals()
        logger.info(f"🌐 [SYNERGY]: Project Era: {design_pattern}. Searching Mesh for signals: {signals}")
        
        harvest_count = 0
        
        # 1. Generate Bit-Hashes for each local signal
        for signal in signals:
            # [SILO PROTOCOL]: Technical patterns use Global Salt to allow cross-project synergy.
            # Strategic Intent is handled separately and BLOCKED from Mesh.
            signal_hash = sparse_hasher.fingerprint(signal, salt="GLOBAL_TECH_V1")
            
            # 2. Search Mesh by Hash (Threshold: 0.8)
            results = self.operational.search_mesh_by_hash(signal_hash, threshold=0.8)
            
            for res in results:
                # [STRATEGIC PIVOT] Block local intent leakage
                if res.get('category') == 'strategic-intent':
                    continue
                    
                pattern_id = hashlib.sha256(f"{res['type']}:{res['title']}:{res.get('detail', '')}".encode()).hexdigest()[:12]
                
                # Filter for high-value technical patterns
                if self.buffer:
                    await self.buffer.ingest("patterns", {
                        "id": pattern_id,
                        "text": f"Inherited Technical Pattern: {res['title']}. (Similarity: {res['similarity']})",
                        "origin": res.get('node', 'unknown'),
                        "category": res.get('category', 'technical-pattern'),
                        "pattern": signal,
                        "signal_hash": res.get('signal_hash')
                    })
                else:
                    # Sync fallback
                    self.strategic.save_public_pattern(
                        wisdom_id=wisdom_id,
                        wisdom_text=f"Inherited Technical Pattern: {res['title']}. (Similarity: {res['similarity']})",
                        origin_node=res.get('node', 'unknown'),
                        category=res.get('category', 'technical-pattern'),
                        signal_pattern=signal,
                        signal_hash=res.get('signal_hash')
                    )
                harvest_count += 1
                        
        if harvest_count > 0:
            logger.info(f"✨ [SYNERGY]: Harvested {harvest_count} strategic patterns via Sparse Semantic Similarity.")
        return harvest_count

def run_synergy_sync(project_path: Path):
    """Entry point for pattern synchronization."""
    import asyncio
    try:
        engine = SynergyEngine(project_path)
        return asyncio.run(engine.harvest_mesh_patterns())
    except Exception as e:
        logger.error(f"❌ [SYNERGY_ERROR]: Sync failed: {e}")
        return 0
