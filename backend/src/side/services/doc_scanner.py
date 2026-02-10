import os
import re
import logging
import uuid
from pathlib import Path
from side.storage.modules.strategy import StrategyRegistry

logger = logging.getLogger(__name__)

class DocScanner:
    """
    Documentation Scanner.
    Ingests project goals from raw documentation files.
    """
    
    def __init__(self, registry: StrategyRegistry):
        self.registry = registry

    async def scavenge(self, root_path: Path):
        """
        Scans the project root for goal signals.
        """
        logger.info("🔭 [DOC_SCANNER]: Scanning for Project Goals...")
        
        # Database is the primary source; Scavenger acts as a bridge for existing docs.

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
                plan_id = f"scan_{uuid.uuid5(uuid.NAMESPACE_DNS, title).hex[:8]}"
                self.registry.save_goal(
                    project_id="default",
                    plan_id=plan_id,
                    title=title,
                    plan_type=p_type,
                    description=f"Auto-scanned from {file_path.name}"
                )
            logger.info(f"🔭 [DOC_SCANNER]: Ingested {len(matches)} plans from {file_path.name}")
        except Exception as e:
            logger.error(f"DocScanner failed for {file_path}: {e}")
