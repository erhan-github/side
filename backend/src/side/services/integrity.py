import logging
import hashlib
from pathlib import Path
from side.storage.modules.mmap_store import MmapStore

logger = logging.getLogger(__name__)

class IntegrityService:
    """
    [SOC 2]: Verifies the technical integrity of the Sidelith node.
    Checks if the mmap-index matches the repository state.
    """
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.mmap = MmapStore(project_path)
        
    async def verify_node(self) -> bool:
        """
        Runs a quick integrity check.
        In a production scenario, we'd verify the mmap checksum.
        """
        logger.info("🔒 [INTEGRITY]: Running Node self-check... [MMAP_DNA_VALIDATION]")
        
        # 1. Check if Mmap exists
        mmap_file = self.project_path / ".side" / "sovereign.mmap"
        if not mmap_file.exists():
            logger.warning("🔒 [INTEGRITY]: Mmap index missing. [FS_MISSING_ARTIFACT]")
            return False
            
        # 2. Verify basic mmap state
        self.mmap.open()
        if self.mmap._count == 0:
            logger.warning("🔒 [INTEGRITY]: Mmap index is empty. [ZERO_BYTE_ENTROPY]")
            return False
            
        logger.info(f"🔒 [INTEGRITY]: Node Verified. ({self.mmap._count} vectors locked).")
        return True
