#!/usr/bin/env python3
"""
Pulse Engine Latency Benchmark

Proves that the Sovereign Pulse Engine operates at <1ms latency.
"""
import time
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from side.pulse import pulse

def benchmark_pulse(iterations: int = 1000):
    """Run pulse check N times and measure latency."""
    latencies = []
    
    print(f"Running {iterations} pulse checks...")
    for i in range(iterations):
        start = time.time()
        result = pulse.check_pulse()
        elapsed_ms = (time.time() - start) * 1000
        latencies.append(elapsed_ms)
        
        if i % 100 == 0:
            print(f"  Progress: {i}/{iterations}")
    
    # Statistics
    avg_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    p50 = sorted(latencies)[len(latencies) // 2]
    p95 = sorted(latencies)[int(len(latencies) * 0.95)]
    p99 = sorted(latencies)[int(len(latencies) * 0.99)]
    
    print("\n" + "="*50)
    print("PULSE ENGINE LATENCY BENCHMARK")
    print("="*50)
    print(f"Iterations: {iterations}")
    print(f"Average:    {avg_latency:.3f}ms")
    print(f"Min:        {min_latency:.3f}ms")
    print(f"Max:        {max_latency:.3f}ms")
    print(f"P50:        {p50:.3f}ms")
    print(f"P95:        {p95:.3f}ms")
    print(f"P99:        {p99:.3f}ms")
    print("="*50)
    
    # Verdict
    if avg_latency < 1.0:
        print(f"✅ PASS: Average latency {avg_latency:.3f}ms < 1ms claim")
    else:
        print(f"❌ FAIL: Average latency {avg_latency:.3f}ms >= 1ms claim")
    
    return avg_latency < 1.0

if __name__ == "__main__":
    success = benchmark_pulse(1000)
    sys.exit(0 if success else 1)
