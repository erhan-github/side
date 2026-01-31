"""
Verify Log Scavenger Integration.

Simulates a "Log Friction" event and checks if Verification fails.
"""

import asyncio
from datetime import datetime, timedelta
from side.intel.outcome_verifier import OutcomeVerifier, VerifiedOutcome, ClaimedOutcome
from side.intel.conversation_session import ConversationSession, IntentCategory
from side.storage.simple_db import SimplifiedDatabase

async def run_verifier_drill():
    print("👉 Setting up Scavenger Drill...")
    db = SimplifiedDatabase()
    verifier = OutcomeVerifier(db)
    
    # 1. Create a fake session that just ended
    session = ConversationSession(
        session_id="SCAVENGER-TEST-01",
        project_id="default",
        started_at=datetime.utcnow() - timedelta(minutes=30),
        ended_at=datetime.utcnow() - timedelta(minutes=5),
        raw_intent="Fixing Python Bug",
        claimed_outcome=ClaimedOutcome.FIXED,
        intent_category=IntentCategory.DEBUGGING
    )
    
    # 2. Inject a FAKE Scavenger Log
    print("👉 Injecting Fake 'Runtime Error' from LogScavenger...")
    db.forensic.log_activity(
        project_id="default",
        tool="LOG_SCAVENGER",
        action="capture_generic_signal",
        cost_tokens=0,
        payload={"type": "RUNTIME_ERROR", "data": {"snippet": "Traceback (most recent call last)..."}}
    )
    
    # DEBUG: Check DB
    acts = db.forensic.get_recent_activities("default")
    print(f"DEBUG: Found {len(acts)} activities in DB.")
    for a in acts:
        print(f"   - Tool: {a['tool']}, Action: {a['action']}, Created: {a['created_at']}")

    # 3. Run Verification
    print("👉 Verifying Session...")
    result = verifier.verify_session(session)
    
    if result == VerifiedOutcome.FALSE_POSITIVE:
        print("✅ SUCCESS: Verifier caught the LogScavenger signal!")
        print(f"   Verdict: {result.value}")
    else:
        print(f"❌ FAILURE: Verifier missed it. Verdict: {result.value}")

if __name__ == "__main__":
    asyncio.run(run_verifier_drill())
