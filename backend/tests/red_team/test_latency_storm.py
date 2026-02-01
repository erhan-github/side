
import asyncio
import time
import random
from side.intel.conversation_ingester import ConversationIngester
from side.storage.simple_db import SimplifiedDatabase
from pathlib import Path

# -----------------------------------------------------------------------------
# THE STORM PROTOCOL
# -----------------------------------------------------------------------------

async def run_latency_storm(requests: int = 100):
    """
    Simulates a burst of Intent Ingestions to measure "Zero-Latency" claim.
    """
    print(f"\n🌪️  INITIATING LATENCY STORM ({requests} requests)...")
    
    # 1. Setup
    fake_brain = Path("/tmp/side_storm_brain")
    fake_brain.mkdir(parents=True, exist_ok=True)
    db_path = fake_brain / "load_test.db"
    db = SimplifiedDatabase(db_path)
    
    # Warmer
    # db.init_all_tables() # Auto-init in __init__
    
    # 2. The Loop
    start_time = time.time()
    latencies = []
    
    for i in range(requests):
        req_start = time.time()
        
        # Simulate: Tool Call -> DB Write
        # We assume the 'Ingester' is the bottleneck
        
        # Create a dummy session payload (Simulating MCP Payload)
        intent = f"Refactor Auth Module Step {i}"
        session_id = f"STORM-{i}"
        
        # Direct DB Write (which is what the Tool does)
        # record_strategic_intent(tool="MCP", action="record_intent", ...)
        
        # Using Forensic Store mimicking
        db.forensic.log_activity(
            project_id="storm_proj",
            tool="MCP_STORM",
            action="INTENT_CAPTURE",
            cost_tokens=1,
            payload={"intent": intent, "vector": [0.1, 0.2]}
        )
        
        req_end = time.time()
        latencies.append((req_end - req_start) * 1000) # ms
        
    total_time = time.time() - start_time
    
    # 3. Analysis
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    p99_latency = sorted(latencies)[int(len(latencies)*0.99)]
    
    print(f"--------------------------------------------------")
    print(f"⚡ STORM REPORT:")
    print(f"   Total Requests: {requests}")
    print(f"   Total Time:     {total_time:.4f}s")
    print(f"   Throughput:     {requests / total_time:.1f} ops/sec")
    print(f"--------------------------------------------------")
    print(f"   Avg Latency:    {avg_latency:.3f} ms")
    print(f"   P99 Latency:    {p99_latency:.3f} ms")
    print(f"   Max Latency:    {max_latency:.3f} ms")
    print(f"--------------------------------------------------")
    
    # 4. The Verdict
    # Website Claim: "Zero-Latency" (< 5ms implied)
    if avg_latency < 5.0:
        print("✅ VERDICT: CLAIM VALID (Sub-5ms Perception)")
    else:
        print("❌ VERDICT: CLAIM FAILED (System is sluggish)")
        
    # Cleanup
    import shutil
    shutil.rmtree(fake_brain)

if __name__ == "__main__":
    asyncio.run(run_latency_storm(1000))
