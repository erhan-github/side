import asyncio
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

import pytest
from side.storage.simple_db import SimplifiedDatabase
from side.intel.auditor import Auditor
from side.intel.strategist import Strategist
from side.intel.simulator import Simulator
from side.cloud.limiter import TokenLimiter

@pytest.fixture
def temp_project():
    """Create a temporary project environment."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create a mock project structure
        src = tmp_path / "src"
        src.mkdir()
        (src / "main.py").write_text("def main():\n    print('Hello World')\n")
        (src / "utils.py").write_text("def helper():\n    pass\n")
        
        # Create .cso dir for local db
        cso_dir = tmp_path / ".cso"
        cso_dir.mkdir()
        
        yield tmp_path

@pytest.mark.asyncio
async def test_full_lifecycle_stress(temp_project):
    """
    Stress test the full CSO.ai lifecycle:
    Audit -> Strategy -> Simulate -> Debit/Log
    """
    project_root = temp_project
    db_path = str(project_root / ".cso" / "local.db")
    db = SimplifiedDatabase(db_path)
    
    # 1. Setup User & Tokens
    project_id = SimplifiedDatabase.get_project_id(project_root)
    db.set_token_balance(10000) # Start with 10k tokens
    
    # [Hardening] Fail early if key is missing (No fakes!)
    if not os.environ.get("GROQ_API_KEY"):
        pytest.fail("❌ GROQ_API_KEY is missing! Stress test MUST run with real AI for validation.")

    print(f"\n[E2E] Starting Stress Test for Project: {project_id}")
    
    # 2. RUN AUDIT
    print("[E2E] Running Forensic Audit...")
    # Auditor expects (db, project_path)
    auditor = Auditor(db, project_root)
    audit_results = await auditor.run_full_audit()
    
    # Verify Audit Logging
    activities = db.get_recent_activities(project_id, limit=10)
    audit_logs = [a for a in activities if a["tool"] == "audit"]
    assert len(audit_logs) > 0, "Audit activity not logged!"
    print(f"✅ Audit completed and logged. Cost: {audit_logs[0]['cost_tokens']} tokens.")
    
    # 3. GENERATE STRATEGY
    print("[E2E] Generating Strategy...")
    # [Zero Fallback] Set allow_fallbacks=False
    strategist = Strategist(db, project_root, allow_fallbacks=False)
    # Mock profile for strategy
    profile = {
        "technical": {"primary_language": "python"},
        "business": {"domain": "productivity", "product_type": "CLI"}
    }
    
    # We use a simple strategy call
    query = "How should I structure my CLI tool for maximum velocity?"
    result = await strategist.get_strategy(query, profile)
    
    # [Zero Fallback] Assert no fallback markers
    assert "fallback" not in result.lower(), "Strategy returned a generic fallback!"
    
    # Verify Strategy Logging
    activities = db.get_recent_activities(project_id, limit=10)
    strategy_logs = [a for a in activities if a["tool"] == "strategy"]
    assert len(strategy_logs) > 0, "Strategy activity not logged!"
    print(f"✅ Strategy generated and logged. Cost: {strategy_logs[0]['cost_tokens']} tokens.")
    
    # 4. SIMULATE FEEDBACK
    print("[E2E] Running User Simulation...")
    # [Zero Fallback] Set allow_fallbacks=False
    simulator = Simulator(db, project_root, allow_fallbacks=False)
    sim_result = await simulator.simulate_feedback("Automatic Forensic Auditing", "FinTech")
    
    # [Zero Fallback] Assert no fallback markers
    assert "fallback" not in sim_result.lower(), "Simulation returned a generic fallback!"
    
    # Verify Simulation Logging
    activities = db.get_recent_activities(project_id, limit=10)
    simulation_logs = [a for a in activities if a["tool"] == "simulator"]
    assert len(simulation_logs) > 0, "Simulation activity not logged!"
    print(f"✅ Simulations completed and logged. Cost: {simulation_logs[0]['cost_tokens']} tokens.")
    
    # 5. VERIFY TOKEN DEPLETION
    final_balance = db.get_token_balance()
    total_cost = sum(a["cost_tokens"] for a in db.get_recent_activities(project_id, limit=100))
    expected_balance = 10000 - total_cost
    
    assert final_balance == expected_balance, f"Token mismatch! Expected {expected_balance}, got {final_balance}"
    print(f"✅ Token balance reconciled perfectly: {final_balance} tokens remaining.")
    
    # 6. TEST HARD STOP (Lockdown)
    print("[E2E] Testing Zero-Balance Lockdown...")
    db.set_token_balance(0)
    
    # Try another audit - Should fail due to zero balance in log_activity
    # Note: run_full_audit calls _persist_findings which calls log_activity
    with pytest.raises(Exception) as excinfo:
        await auditor.run_full_audit()
    
    # Check if the error message is correct (TokenEmpty case)
    assert "Insufficient tokens" in str(excinfo.value)
    print(f"✅ Lockdown verified. Tool execution blocked with expected error.")

if __name__ == "__main__":
    # Allow running as a script for manual stress testing
    if not os.environ.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY") == "MOCK":
        print("⚠️ GROQ_API_KEY not found or mock. Results will be heuristic/fallback.")
        
    asyncio.run(test_full_lifecycle_stress(Path(tempfile.mkdtemp())))

if __name__ == "__main__":
    # Allow running as a script
    # We need to set env vars if running manually
    if not os.environ.get("GROQ_API_KEY"):
        os.environ["GROQ_API_KEY"] = "mock_key" # For plumbing test
        
    asyncio.run(test_full_lifecycle_stress(Path(tempfile.mkdtemp())))
