import os
import re
import logging
import uuid
from pathlib import Path
from side.storage.modules.strategic import StrategicStore

logger = logging.getLogger(__name__)

class StrategicScavenger:
    """
    [STRATEGIC_SCAVENGER]: Ingests 5-year plans from raw documentation.
    Scans for 'MONOLITH.md', 'STRATEGY.md', and files in 'docs/' to 
    auto-populate the StrategicStore.
    """
    
    def __init__(self, strategic: StrategicStore):
        self.strategic = strategic

    async def scavenge(self, root_path: Path):
        """
        Scans the project root for strategic signals.
        """
        logger.info("🔭 [STRATEGIC_SCAVENGER]: Scanning for Sovereign Plans...")
        
        # Priority 1: MONOLITH.md (The Core)
        monolith = root_path / "MONOLITH.md"
        if monolith.exists():
            await self._ingest_file(monolith, "objective")

        # Priority 2: strategy.md
        strategy = root_path / "strategy.md"
        if strategy.exists():
            await self._ingest_file(strategy, "vision")
            
        # Priority 3: docs/*.md
        docs_dir = root_path / "docs"
        if docs_dir.exists():
            for f in docs_dir.glob("*.md"):
                await self._ingest_file(f, "goal")

    async def _ingest_file(self, file_path: Path, p_type: str):
        """
        Extracts level-1 headers as 'Plans' and content as 'Reasoning'.
        """
        try:
            content = file_path.read_text()
            # Simple Markdown extraction: Look for # or ##
            matches = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
            
            for title in matches:
                # Add to Strategic Store if not exists
                plan_id = f"scavenge_{uuid.uuid5(uuid.NAMESPACE_DNS, title).hex[:8]}"
                self.strategic.save_plan(
                    project_id="default",
                    plan_id=plan_id,
                    title=title,
                    plan_type=p_type,
                    description=f"Auto-scavenged from {file_path.name}"
                )
            logger.info(f"🔭 [SCAVENGER]: Ingested {len(matches)} plans from {file_path.name}")
        except Exception as e:
            logger.error(f"Scavernger failed for {file_path}: {e}")
