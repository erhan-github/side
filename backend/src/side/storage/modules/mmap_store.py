import os
import mmap
import logging
import struct
import numpy as np
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Split-Contiguous Format: [N * 8-byte hashes] [N * 16-byte UUIDs]
# This ensures hashes are perfectly contiguous for SIMD/NEON processing.
HASH_SIZE = 8
UUID_SIZE = 16

class MmapStore:
    """
    [INTEL-4] Memory-Mapped Context Store.
    Provides zero-copy binary access to model fragments for accelerated processing.
    """

    def __init__(self, project_path: Path):
        self.mmap_path = project_path / ".side" / "sovereign.mmap"
        self._mmap = None
        self._fd = None
        self._count = 0

    def open(self):
        """Map the binary store into memory."""
        if not self.mmap_path.exists():
            self.mmap_path.touch()
            
        file_size = self.mmap_path.stat().st_size
        if file_size == 0:
            return

        self._fd = os.open(self.mmap_path, os.O_RDWR)
        self._mmap = mmap.mmap(self._fd, 0)
        
        # [PERFORMANCE SPRINT I] Pre-fault the memory map to break the "Disk-Read Wall"
        # This hints the OS to load the entire index into RAM now.
        if hasattr(mmap, "MADV_WILLNEED"):
            try:
                self._mmap.madvise(mmap.MADV_WILLNEED)
            except Exception:
                pass
        else:
            # Fallback: Touch every page to force I/O
            _ = self._mmap[:] 

        # Calculate count based on record size (8 + 16 = 24 bytes total)
        self._count = file_size // (HASH_SIZE + UUID_SIZE)
        logger.info(f"💾 [MMAP]: Loaded {self._count} fragments. Disk-Read Wall BROKEN.")

    def close(self):
        """Saferly close the mmap, allowing for active buffers to be garbage collected."""
        try:
            m = self._mmap
            self._mmap = None
            if m:
                # We don't explicitly call close() if views might be active
                # Python will close it when ref count hits 0.
                pass
            if self._fd is not None:
                os.close(self._fd)
                self._fd = None
        except Exception:
            pass

    def sync_from_ledger(self, fragments: List[Tuple[int, bytes]]):
        """
        Writes signals in split-contiguous blocks: [Hashes...][UUIDs...]
        """
        self.close()
        
        with open(self.mmap_path, "wb") as f:
            # 1. Write all hashes (Contiguous Block)
            for signal_hash, _ in fragments:
                f.write(struct.pack("<q", signal_hash))
            
            # 2. Write all UUIDs (Contiguous Block)
            for _, uuid_bytes in fragments:
                f.write(uuid_bytes)
        
        self.open()

    def get_hash_array(self) -> np.ndarray:
        """
        Returns the contiguous hash block from the mmap buffer.
        Zero overhead, perfectly aligned for SIMD.
        """
        if not self._mmap or len(self._mmap) == 0:
            return np.array([], dtype=np.int64)
            
        hash_block_size = self._count * HASH_SIZE
        return np.frombuffer(self._mmap, dtype=np.int64, count=self._count)

    def get_uuid_at(self, index: int) -> bytes:
        """Retrieve the UUID from the offset contiguous block."""
        if self._mmap is None or index >= self._count:
            return b""
        hash_block_offset = self._count * HASH_SIZE
        offset = hash_block_offset + (index * UUID_SIZE)
        return self._mmap[offset : offset + UUID_SIZE]
