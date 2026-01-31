"""
Test: Pulse Latency Benchmark

Verifies that the Pulse Engine operates under 1ms latency claim.
"""
import pytest
import time
from side.pulse import pulse


class TestPulseLatency:
    """Tests for Pulse Engine latency claims."""
    
    def test_pulse_check_under_1ms(self):
        """Pulse check should complete in under 1ms average."""
        latencies = []
        iterations = 100
        
        for _ in range(iterations):
            start = time.time()
            result = pulse.check_pulse()
            elapsed_ms = (time.time() - start) * 1000
            latencies.append(elapsed_ms)
        
        avg_latency = sum(latencies) / len(latencies)
        
        # Claim: <1ms average
        assert avg_latency < 1.0, f"Average latency {avg_latency:.3f}ms exceeds 1ms claim"
        
        # Additional check: P95 should be under 5ms
        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        assert p95 < 5.0, f"P95 latency {p95:.3f}ms exceeds 5ms threshold"
    
    def test_pulse_check_returns_secure_status(self):
        """Pulse check should return SECURE status on clean code."""
        result = pulse.check_pulse()
        assert result.status.name == "SECURE"
    
    def test_pulse_check_is_deterministic(self):
        """Multiple pulse checks should return consistent results."""
        results = [pulse.check_pulse() for _ in range(10)]
        statuses = [r.status for r in results]
        
        # All should be the same
        assert len(set(s.name for s in statuses)) == 1
    
    def test_pulse_violations_empty_on_clean(self):
        """Clean code should have no violations."""
        result = pulse.check_pulse()
        assert len(result.violations) == 0


class TestPulsePerformance:
    """Performance benchmarks for CI validation."""
    
    @pytest.mark.benchmark
    def test_1000_iterations_performance(self):
        """Run 1000 pulse checks and measure aggregate performance."""
        start = time.time()
        
        for _ in range(1000):
            pulse.check_pulse()
        
        total_ms = (time.time() - start) * 1000
        avg_ms = total_ms / 1000
        
        # Assert average under 1ms
        assert avg_ms < 1.0, f"Average {avg_ms:.3f}ms over 1000 iterations exceeds 1ms"
        
        # Throughput check: at least 1000 checks/second
        checks_per_sec = 1000 / (total_ms / 1000)
        assert checks_per_sec > 1000, f"Throughput {checks_per_sec:.0f}/sec below 1000/sec minimum"
