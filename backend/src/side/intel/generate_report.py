"""
Generate Intent Fusion Report.

Runs the Ingester and Verifier on the CURRENT session to demonstrate the full cycle.
"""

import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime

from side.intel.conversation_ingester import ConversationIngester
from side.intel.outcome_verifier import OutcomeVerifier
from side.storage.simple_db import SimplifiedDatabase
from side.intel.conversation_session import ClaimedOutcome

# Setup
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("report")
logger.setLevel(logging.INFO)

CURRENT_SESSION_ID = "961563dd-1539-429e-91a0-fea6661096cd"

async def generate_report():
    print(f"🕵️  GENERATING INTENT FUSION REPORT FOR SESSION: {CURRENT_SESSION_ID}\n")
    
    db = SimplifiedDatabase()
    
    # 1. Ingest
    print("👉 Phase 1: Ingestion (MetaJSON Extraction)")
    ingester = ConversationIngester(db=db)
    # Force ingest of this specific session if possible, or just scan all
    await ingester.ingest_all()
    
    session = db.intent_fusion.get_session(CURRENT_SESSION_ID)
    if not session:
        print("❌ Session not found in DB! (Check if task.md exists and bridge is working)")
        # Attempt manual hydration for debugging if bridge fails
        return

    print(f"   ✅ Detected Intent: '{session['raw_intent'][:60]}...'")
    print(f"   ✅ Categorized As: {session['intent_category']}")
    print(f"   ✅ Claimed Outcome: {session['claimed_outcome']}")

    # 2. Verify
    print("\n👉 Phase 2: Verification (Audit Triangulation)")
    verifier = OutcomeVerifier(db)
    
    # Convert dict back to dataclass for verification logic
    from side.intel.conversation_session import ConversationSession, ClaimedOutcome as EnumClaimedOutcome
    
    # Check if claimed outcome is set; if not (maybe bridge didn't sync walkthrough yet), force it for demo
    if session['claimed_outcome'] == "UNKNOWN":
        print("   ⚠️  Walkthrough not fully synced? Forcing check based on artifacts...")
        # In a real run, we'd wait for bridge. Here we simulate the bridge update
        session['claimed_outcome'] = "FIXED" 

    session_obj = ConversationSession(
        session_id=session['session_id'],
        project_id=session['project_id'],
        started_at=datetime.fromisoformat(session['started_at']) if session.get('started_at') else None,
        ended_at=datetime.fromisoformat(session['ended_at']) if session.get('ended_at') else datetime.now(),
        # Hack to handle string vs enum if needed, but constructor expects enum
        claimed_outcome=EnumClaimedOutcome(session['claimed_outcome']),
        raw_intent=session['raw_intent']
    )
    
    verification = verifier.verify_session(session_obj)
    print(f"   🛡️  Verdict: {verification.value}")
    
    # 3. Signals
    print("\n👉 Phase 3: Derived Signals")
    signals = db.intent_fusion.get_signals_for_session(CURRENT_SESSION_ID)
    if signals:
        for idx, sig in enumerate(signals):
            print(f"   📡 Signal {idx+1}: [{sig['signal_type']}] {sig['context_snippet'][:60]}...")
    else:
        print("   (No repetition or anomalies detected)")

    print("\n✅ REPORT GENERATION COMPLETE.")

if __name__ == "__main__":
    asyncio.run(generate_report())
