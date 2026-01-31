"""
Summit Phase 3 Drill: Intelligence & Cloud.
"""

import asyncio
from side.mesh.s3_protocol import s3
from side.intel.reasoning import timeline

async def run_phase_3_drill():
    print("☁️ [PHASE 3]: Cloud Mesh & Reasoning...")
    
    # 1. MESH SYNC CHECK
    print("\n🌐 [TEST 1]: S3 Protocol Sync")
    peers = s3.discover_peers()
    print(f"   Peers: {peers}")
    
    fix = {"pattern": "NPE", "fix": "check null"}
    s3.propagate_fix(fix)
    count = s3.sync()
    print(f"   Synced Items: {count}")
    
    if count >= 1 and len(peers) > 0:
        print("✅ PASS: Mesh Propagation Active.")
    else:
        print("❌ FAIL: Mesh Silent.")
        exit(1)

    # 2. TIMELINE INTEGRITY
    print("\n🔗 [TEST 2]: Reasoning Timeline Audit")
    h1 = timeline.add_event("AutoIntelligence", "Fix", "Detected NPE")
    h2 = timeline.add_event("User", "Approve", "LGTM")
    print(f"   Block 1 Hash: {h1[:8]}...")
    print(f"   Block 2 Hash: {h2[:8]}...")
    
    is_valid = timeline.verify_integrity()
    if is_valid:
        print("✅ PASS: Audit Chain Intact.")
    else:
        print("❌ FAIL: Chain Tampered.")
        exit(1)

    print("\n🏆 PHASE 3 DRILL COMPLETE.")

if __name__ == "__main__":
    asyncio.run(run_phase_3_drill())
