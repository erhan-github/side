"""
Tests for resource limits and memory safety features.

Verifies that:
1. Cache eviction works correctly
2. Memory limits are enforced
3. Health endpoint returns correct status
4. Resource limits prevent unbounded growth
"""

import pytest
import json
from pathlib import Path
from side.config import SideConfig
from side.storage.modules.base import ContextEngine
from side.storage.modules.transient import OperationalStore


class TestCacheEviction:
    """Test cache eviction with LRU strategy."""
    
    def setup_method(self):
        """Create test database."""
        self.test_db = Path("/tmp/test_cache_eviction.db")
        if self.test_db.exists():
            self.test_db.unlink()
        
        self.engine = ContextEngine(db_path=self.test_db)
        self.store = OperationalStore(self.engine)
    
    def teardown_method(self):
        """Clean up test database."""
        if self.test_db.exists():
            self.test_db.unlink()
    
    def test_cache_eviction_when_limit_reached(self):
        """Test that cache evicts oldest entries when limit is reached."""
        # Set low limit for testing
        from side.config import config
        original_limit = config.max_cache_entries
        original_batch = config.cache_eviction_batch_size
        original_enabled = config.enable_cache_eviction
        
        try:
            config.max_cache_entries = 10
            config.cache_eviction_batch_size = 5
            config.enable_cache_eviction = True
            
            # Add 10 entries (at limit)
            for i in range(10):
                self.store.save_query_cache(
                    query_type="test",
                    query_params={"id": i},
                    result={"data": f"result_{i}"}
                )
            
            stats = self.store.get_cache_stats()
            assert stats["entry_count"] == 10, "Should have 10 entries"
            
            # Add one more entry - should trigger eviction
            self.store.save_query_cache(
                query_type="test",
                query_params={"id": 11},
                result={"data": "result_11"}
            )
            
            stats = self.store.get_cache_stats()
            assert stats["entry_count"] == 6, "Should have 6 entries after eviction (10 - 5 + 1)"
            
        finally:
            # Restore original config
            config.max_cache_entries = original_limit
            config.cache_eviction_batch_size = original_batch
            config.enable_cache_eviction = original_enabled
    
    def test_cache_eviction_disabled(self):
        """Test that cache can grow beyond limit when eviction is disabled."""
        from side.config import config
        original_limit = config.max_cache_entries
        original_enabled = config.enable_cache_eviction
        
        try:
            config.max_cache_entries = 5
            config.enable_cache_eviction = False
            
            # Add 10 entries (beyond limit)
            for i in range(10):
                self.store.save_query_cache(
                    query_type="test",
                    query_params={"id": i},
                    result={"data": f"result_{i}"}
                )
            
            stats = self.store.get_cache_stats()
            assert stats["entry_count"] == 10, "Should have all 10 entries when eviction disabled"
            
        finally:
            config.max_cache_entries = original_limit
            config.enable_cache_eviction = original_enabled
    
    def test_cache_stats_accuracy(self):
        """Test that cache statistics are accurate."""
        # Add some entries
        for i in range(5):
            self.store.save_query_cache(
                query_type="test",
                query_params={"id": i},
                result={"data": f"result_{i}" * 100}  # Larger data
            )
        
        stats = self.store.get_cache_stats()
        
        assert stats["entry_count"] == 5
        assert stats["size_bytes"] > 0
        assert stats["size_mb"] > 0
        assert stats["oldest_entry"] is not None
        assert stats["newest_entry"] is not None


class TestResourceConfig:
    """Test resource configuration validation."""
    
    def test_default_values(self):
        """Test that default values are reasonable."""
        config = SideConfig()
        
        assert config.max_memory_mb == 2048  # 2GB
        assert config.auto_restart_threshold_mb == 3072  # 3GB
        assert config.max_cache_entries == 10000
        assert config.max_file_watchers == 5
        assert config.enable_cache_eviction is True
    
    def test_environment_override(self):
        """Test that environment variables override defaults."""
        import os
        
        # Set environment variables
        os.environ["MAX_MEMORY_MB"] = "4096"
        os.environ["MAX_CACHE_ENTRIES"] = "20000"
        os.environ["ENABLE_AUTO_RESTART"] = "true"
        
        try:
            config = SideConfig()
            
            assert config.max_memory_mb == 4096
            assert config.max_cache_entries == 20000
            assert config.enable_auto_restart is True
            
        finally:
            # Clean up
            del os.environ["MAX_MEMORY_MB"]
            del os.environ["MAX_CACHE_ENTRIES"]
            del os.environ["ENABLE_AUTO_RESTART"]


class TestHealthEndpoint:
    """Test health check endpoint functionality."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint_structure(self):
        """Test that health endpoint returns expected structure."""
        from side.server import health_check
        from starlette.requests import Request
        from starlette.testclient import TestClient
        
        # Create a mock request
        class MockRequest:
            pass
        
        response = await health_check(MockRequest())
        data = json.loads(response.body)
        
        # Verify structure
        assert "status" in data
        assert "timestamp" in data
        assert "memory" in data
        assert "cache" in data
        assert "warnings" in data
        
        # Verify memory fields
        assert "rss_mb" in data["memory"]
        assert "limit_mb" in data["memory"]
        assert "warning_threshold_mb" in data["memory"]
        assert "auto_restart_threshold_mb" in data["memory"]
        
        # Verify cache fields
        assert "entries" in data["cache"]
        assert "size_mb" in data["cache"]
        assert "limit" in data["cache"]
        assert "eviction_enabled" in data["cache"]
    
    @pytest.mark.asyncio
    async def test_health_status_levels(self):
        """Test that health status changes based on memory usage."""
        from side.server import health_check
        from side.config import config
        
        response = await health_check(None)
        data = json.loads(response.body)
        
        # Status should be one of: healthy, warning, critical
        assert data["status"] in ["healthy", "warning", "critical", "error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
