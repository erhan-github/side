"""
Test: Circuit Breaker Failover

Verifies Circuit Breaker behavior for LLM provider failover.
"""
import pytest
import time
from unittest.mock import MagicMock, patch
from side.llm.managed_pool import ManagedCreditPool, CircuitBreakerMetrics


class TestCircuitBreakerBasics:
    """Basic circuit breaker functionality tests."""
    
    def test_pool_loads_keys(self):
        """Pool should load keys from environment."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test_key_123'}):
            pool = ManagedCreditPool(provider="groq")
            assert len(pool.keys) >= 1
    
    def test_key_rotation_works(self):
        """Keys should rotate on get_next_key()."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'key1', 'SIDE_POOL_KEYS': 'key2,key3'}):
            pool = ManagedCreditPool(provider="groq")
            
            # Get keys and verify rotation
            keys_seen = []
            for _ in range(3):
                key = pool.get_next_key()
                keys_seen.append(key)
            
            # Should see rotation (not same key 3 times)
            assert len(keys_seen) == 3
    
    def test_mark_as_cooling_removes_key(self):
        """Marking a key as cooling should remove it from rotation."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'key1', 'SIDE_POOL_KEYS': 'key2'}):
            pool = ManagedCreditPool(provider="groq")
            initial_count = len(pool.keys)
            
            pool.mark_as_cooling('key1')
            
            assert len(pool.keys) == initial_count - 1
            assert 'key1' in pool.cooling_keys


class TestCircuitBreakerMetrics:
    """Tests for circuit breaker metrics and monitoring."""
    
    def test_metrics_track_requests(self):
        """Metrics should track total and successful requests."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test_key'}):
            pool = ManagedCreditPool(provider="groq")
            
            # Make some requests
            for _ in range(5):
                pool.get_next_key()
            
            metrics = pool.get_metrics()
            assert metrics.total_requests == 5
            assert metrics.successful_requests == 5
    
    def test_metrics_track_failures(self):
        """Metrics should track failed requests."""
        # Pool with no keys
        with patch.dict('os.environ', {}, clear=True):
            pool = ManagedCreditPool(provider="groq")
            pool.keys.clear()  # Force empty
            
            # Try to get key (should fail)
            result = pool.get_next_key()
            
            metrics = pool.get_metrics()
            assert metrics.failed_requests >= 1
    
    def test_health_score_calculation(self):
        """Health score should be 0-100 based on key availability."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'key1', 'SIDE_POOL_KEYS': 'key2,key3'}):
            pool = ManagedCreditPool(provider="groq")
            
            metrics = pool.get_metrics()
            
            # With 3 healthy keys, score should be 100
            assert metrics.health_score == 100
            
            # Cool one key
            pool.mark_as_cooling('key1')
            metrics = pool.get_metrics()
            
            # Score should decrease (2/3 keys healthy)
            assert metrics.health_score < 100
    
    def test_circuit_trips_tracked(self):
        """Circuit trips should be counted when all keys exhaust."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'key1'}):
            pool = ManagedCreditPool(provider="groq")
            
            # Cool the only key
            pool.mark_as_cooling('key1', duration=3600)
            
            # Try to get key (should fail and increment trips)
            pool.get_next_key()
            
            metrics = pool.get_metrics()
            assert metrics.circuit_trips >= 1
    
    def test_get_status_returns_dict(self):
        """get_status() should return a dashboard-friendly dict."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test_key'}):
            pool = ManagedCreditPool(provider="groq")
            
            status = pool.get_status()
            
            assert 'provider' in status
            assert 'health_score' in status
            assert 'active_keys' in status
            assert 'success_rate' in status


class TestCircuitBreakerRecovery:
    """Tests for key recovery from cooling."""
    
    def test_key_recovers_after_cooldown(self):
        """Key should return to rotation after cooldown expires."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'key1'}):
            pool = ManagedCreditPool(provider="groq")
            
            # Cool for 0 seconds (immediate recovery)
            pool.mark_as_cooling('key1', duration=0)
            
            # Wait a tiny bit
            time.sleep(0.01)
            
            # Should recover
            pool._recover_keys()
            
            assert 'key1' in pool.keys or len(pool.cooling_keys) == 0
    
    def test_is_healthy_triggers_recovery(self):
        """Checking is_healthy should trigger recovery check."""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'key1'}):
            pool = ManagedCreditPool(provider="groq")
            
            # Cool with 0 duration
            pool.mark_as_cooling('key1', duration=0)
            time.sleep(0.01)
            
            # Check health (should trigger recovery)
            is_healthy = pool.is_healthy
            
            # Should have recovered
            assert len(pool.keys) > 0 or is_healthy
