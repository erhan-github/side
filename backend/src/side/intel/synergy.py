
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from side.storage.simple_db import SimplifiedDatabase

logger = logging.getLogger(__name__)

class SynergyEngine:
    """
    The 'Collective Intelligence' Layer.
    Identifies shared signals between Projects and harvests Public Wisdom.
    """
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path).resolve()
        self.db = SimplifiedDatabase()
        self.project_id = self.db.get_project_id(self.project_path)

    def identify_signals(self) -> List[str]:
        """Harvest architectural signals from the current project."""
        signals = []
        # Signal 1: Core Frameworks (Detected via deps or folder structure)
        if (self.project_path / "web").exists(): signals.append("React/NextJS")
        if (self.project_path / "backend" / "src" / "side").exists(): signals.append("Sovereign/Sidelith")
        if (self.project_path / "package.json").exists(): signals.append("NodeJS")
        
        # Signal 2: Database Patterns
        if (self.project_path / "supabase").exists(): signals.append("Supabase")
        
        return signals

    def harvest_mesh_wisdom(self):
        """Pulls relevant strategic wisdom from other nodes."""
        signals = self.identify_signals()
        logger.info(f"🌐 [SYNERGY]: Searching Mesh for signals: {signals}")
        
        nodes = self.db.list_mesh_nodes()
        harvest_count = 0
        
        for node in nodes:
            if node['project_id'] == self.project_id:
                continue
                
            # Perform a strategic search for our signals on this node
            for signal in signals:
                # Fuzzy match: Search for individual keywords in the signal
                keywords = signal.replace("/", " ").split()
                for kw in keywords:
                    results = self.db.search_mesh_wisdom(kw)
                    for res in results:
                        # Filter for high-value rejections or decisions
                        if res['type'] in ['REJECTION', 'LEARNING', 'DECISION']:
                            wisdom_id = hashlib.sha256(f"{res['type']}:{res['title']}:{res['detail']}".encode()).hexdigest()[:12]
                            self.db.save_public_wisdom(
                                wisdom_id=wisdom_id,
                                wisdom_text=f"Inherited {res['type']}: {res['title']}. Detail: {res['detail']}",
                                origin_node=node['name'],
                                category=res.get('category', 'cross-node'),
                                signal_pattern=signal
                            )
                            harvest_count += 1
                        
        if harvest_count > 0:
            logger.info(f"✨ [SYNERGY]: Harvested {harvest_count} strategic patterns from the Universal Mesh.")
        return harvest_count

def run_synergy_sync(project_path: Path):
    """Entry point for wisdom synchronization."""
    try:
        engine = SynergyEngine(project_path)
        return engine.harvest_mesh_wisdom()
    except Exception as e:
        logger.error(f"❌ [SYNERGY_ERROR]: Sync failed: {e}")
        return 0
