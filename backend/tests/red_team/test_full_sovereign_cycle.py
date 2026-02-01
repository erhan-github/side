
import pytest
import sqlite3
import time
from pathlib import Path
from side.pulse import pulse, PulseStatus, PulseResult
from side.storage.simple_db import SimplifiedDatabase

# -----------------------------------------------------------------------------
# THE KARPATHY PROTOCOL: FULL LOOP VERIFICATION
# -----------------------------------------------------------------------------
# We simulate the 7-Phase Sovereign Cycle in a single rigorous test.
# No mocking of the core logic. We use the real Pulse Engine and Real DB.

def test_full_sovereign_cycle():
    """
    Step-by-Step Proof of the Sidelith Cycle.
    """
    print("\n\n🔱 INITIATING KARPATHY PROTOCOL: FULL CYCLE TEST")
    
    # -------------------------------------------------------------------------
    # PHASE 0: AMNESIA (Clean Slate)
    # -------------------------------------------------------------------------
    print("\n[PHASE 0] AMNESIA: Initializing Clean Sovereign State...")
    db_path = Path("/tmp/side_cycle_test.db")
    if db_path.exists(): db_path.unlink()
    
    db = SimplifiedDatabase(db_path)
    # Ensure rules are loaded
    pulse.sync_prime_rules()
    pulse._load_dynamic_rules()
    
    # MOCK STRICT MODE (Karpathy Protocol requires absolute enforcement)
    def mock_load_anchor(self):
        return {
            "moat_pulse": {"enforcement_mode": "STRICT"},
            "constitution": {"invariants": []}, 
            "gold_standards": {}
        }
    import types
    pulse._load_anchor = types.MethodType(mock_load_anchor, pulse)
    
    # -------------------------------------------------------------------------
    # PHASE 1 & 2: INGESTION & PERCEPTION (The Attack)
    # -------------------------------------------------------------------------
    print("[PHASE 1] DRIFT: Injecting Architectural Violation...")
    
    # ATTACK: We inject a "FastAPI Async Blocking" violation.
    # This matches the 'fastapi_async_safety' rule in pulse.py
    bad_code = """
import time
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    # VIOLATION: Blocking sleep in async route
    time.sleep(5) 
    return {"message": "Laggy"}
    """
    
    ctx = {
        "target_file": "main.py",
        "file_content": bad_code,
        "metadata": {"frameworks": ["fastapi"]} # Context injection
    }
    
    print("[PHASE 2] PULSE: Detecting Violation...")
    result = pulse.check_pulse(ctx)
    
    # ASSERTION: Must find the violation
    print(f"   > Pulse Status: {result.status}")
    print(f"   > Violations: {result.violations}")
    
    assert result.status == PulseStatus.VIOLATION, "Failed to block Async violation!"
    assert "fastapi_async_safety" in str(result.violations), "Wrong rule triggered!"
    print("   ✅ PERCEPTION CONFIRMED. Pulse blocked the drift.")
    
    # -------------------------------------------------------------------------
    # PHASE 3: TRANSLATION & SYNTHESIS (The Strategist)
    # -------------------------------------------------------------------------
    print("[PHASE 3] SYNTHESIS: Identifying Fix Strategy...")
    # In a real loop, AutoIntelligence does this. Here we query the Rule Rationale.
    
    # Find the specific rule that triggered
    triggered_rule = next(r for r in pulse.rules_cache if r.id == "fastapi_async_safety")
    print(f"   > Identified Fix: {triggered_rule.fix}")
    
    assert "asyncio.sleep" in triggered_rule.fix, "Strategic Fix is incorrect!"
    print("   ✅ SYNTHESIS CONFIRMED. System knows the cure.")

    # -------------------------------------------------------------------------
    # PHASE 4 & 5: ACTION (The Fix)
    # -------------------------------------------------------------------------
    print("[PHASE 4] ACTION: Applying Sovereign Remediation...")
    
    # Simulate the fix application (Replace synchronous sleep)
    fixed_code = bad_code.replace("time.sleep(5)", "await asyncio.sleep(5)")
    
    print("   > Code Modified. Re-scanning...")
    
    # -------------------------------------------------------------------------
    # PHASE 6: VERIFICATION (The WFW Loop)
    # -------------------------------------------------------------------------
    print("[PHASE 6] VERIFICATION: Confirming Resolution...")
    
    ctx_fixed = {
        "target_file": "main.py",
        "file_content": fixed_code,
        "metadata": {"frameworks": ["fastapi"]}
    }
    
    result_fixed = pulse.check_pulse(ctx_fixed)
    
    # ASSERTION: Must be CLEAN
    assert result_fixed.status == PulseStatus.SECURE, "Fix failed to clear violation!"
    print("   ✅ WFW CONFIRMED. Violation cleared.")
    
    # -------------------------------------------------------------------------
    # PHASE 7: REFINEMENT (The ROI)
    # -------------------------------------------------------------------------
    print("[PHASE 7] ROI: Logging Averted Disaster...")
    
    # Simulate Logging the ROI (outcome_verifier logic)
    # log_averted_disaster(project_id, reason, su_saved)
    db.forensic.log_averted_disaster(
        project_id="test_cycle_proj",
        reason="fastapi_async_safety",
        su_saved=50,
        technical_debt="High Latency Endpoint"
    )
    
    # Verify Ledger
    with db.engine.connection() as conn:
        row = conn.execute("SELECT * FROM averted_disasters WHERE project_id = 'test_cycle_proj'").fetchone()
        saved = row['su_saved']
        reason = row['reason']
        
    print(f"   > Ledger Entry: {reason} | Saved: {saved} SU")
    assert saved == 50, "Ledger failed to record value!"
    print("   ✅ LEDGER CONFIRMED. Value captured.")

    print("\n🔱 FULL SOVEREIGN CYCLE VERIFIED.")
    
    # Cleanup
    import os
    os.remove(db_path)

if __name__ == "__main__":
    try:
        test_full_sovereign_cycle()
    except AssertionError as e:
        print(f"\n❌ CYCLE FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        exit(1)
