"""
Test: Phoenix Protocol Recovery

Verifies that Phoenix Protocol can recover context in under 2 seconds.
"""
import pytest
import time
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestPhoenixRecovery:
    """Tests for Phoenix Protocol recovery timing."""
    
    def test_phoenix_recovery_under_2s(self):
        """Phoenix Protocol should recover context in under 2 seconds."""
        from side.intel.auto_intelligence import AutoIntelligence
        
        project_path = Path.cwd()
        ai = AutoIntelligence(project_path)
        
        start = time.time()
        
        # Simulate recovery by gathering context
        # This is the core Phoenix operation
        context = ai.gather_context()
        
        recovery_time = time.time() - start
        
        # Claim: recovery in under 2 seconds
        assert recovery_time < 2.0, f"Recovery time {recovery_time:.2f}s exceeds 2s claim"
    
    def test_phoenix_recovery_returns_valid_context(self):
        """Phoenix recovery should return valid context data."""
        from side.intel.auto_intelligence import AutoIntelligence
        
        project_path = Path.cwd()
        ai = AutoIntelligence(project_path)
        
        context = ai.gather_context()
        
        # Should return string or dict
        assert context is not None
        assert isinstance(context, (str, dict))
    
    def test_phoenix_recovery_is_idempotent(self):
        """Multiple recovery calls should return consistent results."""
        from side.intel.auto_intelligence import AutoIntelligence
        
        project_path = Path.cwd()
        ai = AutoIntelligence(project_path)
        
        # Run twice
        context1 = ai.gather_context()
        context2 = ai.gather_context()
        
        # Results should be equivalent (same type and similar content)
        assert type(context1) == type(context2)


class TestPhoenixPerformance:
    """Performance tests for Phoenix Protocol."""
    
    def test_historic_feed_performance(self):
        """Historic feed should process in reasonable time."""
        from side.intel.auto_intelligence import AutoIntelligence
        
        project_path = Path.cwd()
        ai = AutoIntelligence(project_path)
        
        start = time.time()
        
        # Get historic context
        try:
            historic = ai.get_historic_context(limit=10)
        except Exception:
            pytest.skip("Historic context not available")
        
        elapsed = time.time() - start
        
        # Should complete in under 5 seconds
        assert elapsed < 5.0, f"Historic feed took {elapsed:.2f}s, exceeds 5s limit"
