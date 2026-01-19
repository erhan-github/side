import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from side.storage.simple_db import SimplifiedDatabase
from side.tools.audit import handle_run_audit
from side.tools.strategy import handle_decide
from side.tools.simulation import handle_simulate_users

async def prove_transparency():
    print("🚀 CSO.AI TRANSPARENCY PROOF\n" + "="*40)
    
    project_root = Path.cwd()
    db = SimplifiedDatabase() # Use system default ~/.side/local.db
    
    # ensure main profile exists for wallet
    with db._connection() as conn:
        conn.execute("INSERT OR IGNORE INTO profile (id, token_balance, tier) VALUES ('main', 50000, 'pro')")
    
    balance_before = db.get_token_balance()
    print(f"💰 STARTING BALANCE: {balance_before:,} TKNS")
    print(f"📄 TRACKING PROJECT: {project_root.name}\n")

    # 1. RUN AUDIT
    print("🔍 [STEP 1] Running Forensic Audit...")
    await handle_run_audit({}) # Scans CWD
    
    # 2. RUN STRATEGY
    print("🧠 [STEP 2] Requesting Strategic Decision...")
    await handle_decide({"question": "Should we switch from SQL to NoSQL for higher velocity?"})
    
    # 3. RUN SIMULATION
    print("👥 [STEP 3] running user Simulation...")
    await handle_simulate_users({
        "target_audience": "developers",
        "content": "A developer tool that generates strategy and fixes O(n^2) loops automatically.",
        "content_type": "Product Pitch"
    })
    
    balance_after = db.get_token_balance()
    diff = balance_before - balance_after
    
    print("\n" + "="*40)
    print(f"✅ OPERATIONS COMPLETE")
    print(f"💰 FINAL BALANCE:    {balance_after:,} TKNS")
    print(f"📉 TOTAL DEBITED:    {diff:,} TKNS")
    print("="*40 + "\n")

    print("📊 OPERATIONAL LEDGER (Last 5 Events):")
    print("-" * 60)
    activities = db.get_recent_activities(SimplifiedDatabase.get_project_id(project_root), limit=5)
    
    for act in activities:
        timestamp = act['created_at'].split(' ')[1] if ' ' in act['created_at'] else act['created_at']
        print(f"[{timestamp}] {act['tool'].upper():<10} | {act['action']:<30} | -{act['cost_tokens']:>4} TKNS")

if __name__ == "__main__":
    asyncio.run(prove_transparency())
