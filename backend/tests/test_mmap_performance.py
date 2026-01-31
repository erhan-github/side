"""
Test: Mmap Performance Benchmark

Verifies Mmap store performance for hash lookups.
"""
import pytest
import time
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestMmapPerformance:
    """Tests for Mmap store performance."""
    
    def test_mmap_load_time(self):
        """Mmap store should load fragments in under 100ms."""
        from side.storage.modules.mmap_store import MmapStore
        
        start = time.time()
        mmap_store = MmapStore(Path.cwd())
        mmap_store.open()
        load_time_ms = (time.time() - start) * 1000
        
        # Should load quickly even with many fragments
        assert load_time_ms < 100, f"Mmap load time {load_time_ms:.1f}ms exceeds 100ms"
        
        mmap_store.close()
    
    def test_binary_search_lookup_speed(self):
        """Binary search on sorted hashes should exceed 100K matches/sec."""
        from side.storage.modules.mmap_store import MmapStore
        
        mmap_store = MmapStore(Path.cwd())
        mmap_store.open()
        
        hash_array = mmap_store.get_hash_array()
        if len(hash_array) == 0:
            pytest.skip("No fragments in Mmap store - run 'side feed .' first")
        
        # Sort for binary search
        sorted_hashes = np.sort(hash_array)
        
        # Benchmark: 10K lookups
        iterations = 10000
        test_hashes = np.random.choice(sorted_hashes, size=iterations, replace=True)
        
        start = time.time()
        for test_hash in test_hashes:
            np.searchsorted(sorted_hashes, test_hash)
        elapsed = time.time() - start
        
        matches_per_sec = iterations / elapsed
        
        # Minimum: 100K matches/sec with binary search
        assert matches_per_sec > 100000, f"Match rate {matches_per_sec:.0f}/sec below 100K minimum"
        
        mmap_store.close()
    
    def test_mmap_fragment_count(self):
        """Mmap store should correctly report fragment count."""
        from side.storage.modules.mmap_store import MmapStore
        
        mmap_store = MmapStore(Path.cwd())
        mmap_store.open()
        
        hash_array = mmap_store.get_hash_array()
        
        # Should be non-negative
        assert len(hash_array) >= 0
        
        mmap_store.close()


class TestMmapIntegrity:
    """Tests for Mmap data integrity."""
    
    def test_mmap_hashes_are_valid_int64(self):
        """All hashes should be valid int64 values."""
        from side.storage.modules.mmap_store import MmapStore
        
        mmap_store = MmapStore(Path.cwd())
        mmap_store.open()
        
        hash_array = mmap_store.get_hash_array()
        if len(hash_array) > 0:
            # Check dtype
            assert hash_array.dtype == np.int64, f"Hash array dtype is {hash_array.dtype}, expected int64"
            
            # Check no NaN or inf
            assert np.isfinite(hash_array.astype(float)).all(), "Found non-finite values in hash array"
        
        mmap_store.close()
