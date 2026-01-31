"""
Sparse Semantic Hashing for Sidelith.

Implements SimHash for bit-level similarity detection.
Used by the Synergy engine to correlate architectural patterns across projects.
"""

import hashlib
import re
import numpy as np
from typing import List, Set, Optional
try:
    from numba import njit, prange
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

class SparseSimHash:
    """
    Fingerprints text/code into a 64-bit integer.
    Similar content generates hashes with small Hamming Distances.
    """

    def __init__(self, bits: int = 64):
        self.bits = bits

    def fingerprint(self, text: str, salt: Optional[str] = None) -> int:
        """
        Generates a 64-bit SimHash of the input text.
        [SILO PROTOCOL]: Supports optional salting to ensure project-level isolation.
        """
        features = self._tokenize(text)
        if not features:
            return 0

        # Initialize weight vector
        v = [0] * self.bits
        
        for feature in features:
            # Hash feature to bit-length using md5 for stability
            # [SILO]: Incorporate salt into the feature hash
            feature_to_hash = f"{salt}:{feature}" if salt else feature
            h = int(hashlib.sha256(feature_to_hash.encode()).hexdigest(), 16)
            
            for i in range(self.bits):
                bitmask = 1 << i
                if h & bitmask:
                    v[i] += 1
                else:
                    v[i] -= 1
        
        # Build final bit-hash
        fingerprint = 0
        for i in range(self.bits):
            if v[i] > 0:
                fingerprint |= (1 << i)
        
        # [INTEL]: Ensure it fits in SQLite signed 64-bit range
        if self.bits == 64 and fingerprint & (1 << 63):
            fingerprint -= (1 << 64)
            
        return fingerprint

    def hamming_distance(self, hash1: int, hash2: int) -> int:
        """Calculates distance between two hashes (0 to 64)."""
        # Python 3.10+ hardware accelerated bit counting (POPCNT)
        if hasattr(int, "bit_count"):
            return (hash1 ^ hash2).bit_count()
            
        # Fallback (Software 1.0)
        x = hash1 ^ hash2
        distance = 0
        while x:
            distance += 1
            x &= x - 1
        return distance

    def similarity(self, hash1: int, hash2: int) -> float:
        """Calculates normalized similarity (0.0 to 1.0)."""
        dist = self.hamming_distance(hash1, hash2)
        return 1.0 - (dist / self.bits)

    def bulk_similarity(self, query: int, hashes: List[int] | np.ndarray) -> np.ndarray:
        """
        [INTEL-1/3/4] Bulk similarity search.
        Leverages Numba JIT and ARM NEON SIMD on Apple Silicon.
        Supports zero-copy mmap buffers via NumPy pass-through.
        """
        if not HAS_NUMBA:
            # Software Fallback
            if isinstance(hashes, np.ndarray):
                return np.array([self.similarity(query, int(h)) for h in hashes])
            return np.array([self.similarity(query, h) for h in hashes])
            
        # Optimization: If it's already a numpy array (e.g. from mmap), use it directly
        if isinstance(hashes, np.ndarray):
            if hashes.dtype == np.int64:
                hash_array = hashes
            else:
                hash_array = hashes.astype(np.int64)
        else:
            hash_array = np.array(hashes, dtype=np.int64)
            
        distances = _bulk_hamming_neon(query, hash_array)
        return 1.0 - (distances / self.bits)

    def _tokenize(self, text: str) -> List[str]:
        """Simple n-gram tokenizer for code/text."""
        # Remove whitespace and punctuation for base tokens
        text = text.lower()
        # Extract alphanumeric chunks (words/identifiers)
        tokens = re.findall(r'[a-z0-9_]+', text)
        
        # Generate trigrams for better semantic overlap
        # Example: "fastapi" -> ["fas", "ast", "sta", "tap", "api"]
        features = []
        for t in tokens:
            if len(t) < 3:
                features.append(t)
                continue
            for i in range(len(t) - 2):
                features.append(t[i:i+3])
        
        return features

# Global Instance
sparse_hasher = SparseSimHash()

# ─────────────────────────────────────────────────────────────
# [INTEL] HARDWARE ACCELERATION LAYER (NEON / SIMD)
# ─────────────────────────────────────────────────────────────

if HAS_NUMBA:
    @njit(parallel=True, cache=True)
    def _bulk_hamming_neon(query: int, hashes: np.ndarray) -> np.ndarray:
        """
        Optimized JIT function using unsigned 64-bit integers to ensure
        correct SIMD vectorization and logical shifts on M2 Pro.
        """
        n = hashes.shape[0]
        distances = np.zeros(n, dtype=np.int64)
        
        # Force unsigned 64-bit for bitwise safety
        u_query = np.uint64(query)
        u_hashes = hashes.view(np.uint64)
        
        # Constants for bit counting
        m1 = np.uint64(0x5555555555555555)
        m2 = np.uint64(0x3333333333333333)
        m4 = np.uint64(0x0f0f0f0f0f0f0f0f)
        h01 = np.uint64(0x0101010101010101)
        
        for i in prange(n):
            x = u_query ^ u_hashes[i]
            
            # Unsigned popcount algorithm
            x -= (x >> np.uint64(1)) & m1
            x = (x & m2) + ((x >> np.uint64(2)) & m2)
            x = (x + (x >> np.uint64(4))) & m4
            distances[i] = np.int64((x * h01) >> np.uint64(56))
            
        return distances
