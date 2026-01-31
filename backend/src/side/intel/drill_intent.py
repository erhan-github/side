"""
Intent Fusion Drill - Simulation of a Real Summit Task.
"""

import asyncio
import logging
import shutil
import json
import time
from pathlib import Path
from datetime import datetime, timezone

from side.intel.conversation_ingester import ConversationIngester
from side.intel.outcome_verifier import OutcomeVerifier
from side.intel.conversation_session import ClaimedOutcome
from side.storage.simple_db import SimplifiedDatabase

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("drill")

async def run_drill():
    print("\n⚔️  INTENT FUSION DRILL: 'Cluster Caching' Simulation  ⚔️\n")
    
    # 1. Setup Simulation Environment
    fake_brain = Path("/tmp/side_drill_brain")
    if fake_brain.exists(): shutil.rmtree(fake_brain)
    fake_brain.mkdir(parents=True)
    
    project_path = Path.cwd()
    db = SimplifiedDatabase(project_path / ".side" / "local.db")
    
    # 2. Simulate User Intent (Task Creation)
    # Task: [P1] Performant UX: Cluster caching for Mesh signals
    session_id = "DRILL-SESSION-001"
    session_dir = fake_brain / session_id
    session_dir.mkdir()
    
    print(f"👉 Step 1: User creates task 'Implement Cluster Caching'...")
    task_meta = {
        "artifactType": "ARTIFACT_TYPE_TASK",
        "summary": "Implement cluster caching for Mesh signals to improve UX performance. This maps to the P1 task in SUMMIT_DAY_01.",
        "updatedAt": datetime.now(timezone.utc).isoformat()
    }
    (session_dir / "task.md.metadata.json").write_text(json.dumps(task_meta))
    (session_dir / "task.md").write_text("# Dummy Task\n- [ ] Implement Caching")
    
    # 3. Simulate Ingestion
    print(f"👉 Step 2: Ingester detects artifact...")
    ingester = ConversationIngester(brain_path=fake_brain, db=db)
    # We cheat and bypass the loop for speed, calling process directly 
    # But usually we'd wait. Let's trigger the internal logic.
    await ingester.ingest_all()
    
    # Verify Ingestion
    session = db.intent_fusion.get_session(session_id)
    if session:
        print(f"   ✅ Ingested Session: {session['raw_intent']}")
        print(f"   ✅ Intent Category: {session['intent_category']}")
    else:
        print("   ❌ Ingestion Failed!")
        return

    # 4. Simulate Work & Verification Logic (The Outcome)
    print(f"👉 Step 3: User completes work and verification...")
    
    # Write Walkthrough (The Claim)
    walk_meta = {
        "artifactType": "ARTIFACT_TYPE_WALKTHROUGH",
        "summary": "Implemented LRU cache for signal clusters. Verified 50ms latency improvement."
    }
    (session_dir / "walkthrough.md.metadata.json").write_text(json.dumps(walk_meta))
    
    # Update Session in DB to reflect "FIXED" claim (Simulating what Bridge would do on next pass)
    # In real life, Bridge updates the 'claimed_outcome' field.
    db.intent_fusion.save_session_dict({
        **session,
        "claimed_outcome": ClaimedOutcome.FIXED.value,
        "ended_at": datetime.now(timezone.utc).isoformat()
    })
    
    # 5. Run Outcome Verifier
    print(f"👉 Step 4: Outcome Verifier triangulates truth...")
    verifier = OutcomeVerifier(db)
    
    # We need to simulate NO errors in the forensic log for this to pass.
    # Since we are using the real DB, we hope no recent errors exist for this fake project.
    # We can inject a fake clean audit if needed, or just run it.
    
    # Hydrate object for verifier
    from side.intel.conversation_session import ConversationSession
    session_obj = verifier.store.get_session(session_id)
    # Convert dict to object (hack for drill)
    session_dataclass = ConversationSession(
        session_id=session_obj['session_id'],
        project_id=session_obj['project_id'],
        started_at=datetime.fromisoformat(session_obj['started_at']),
        ended_at=datetime.fromisoformat(session_obj['ended_at']),
        claimed_outcome=ClaimedOutcome(session_obj['claimed_outcome']),
        raw_intent=session_obj['raw_intent']
    )
    print(f"DEBUG: Claimed Outcome in DB: {session_obj['claimed_outcome']}")
    print(f"DEBUG: Claimed Outcome Enum: {session_dataclass.claimed_outcome}")
    
    result = verifier.verify_session(session_dataclass)
    print(f"   🛡️  Verification Result: {result.value}")
    
    if result.value == "CONFIRMED":
        print("\n✅ DRILL PASSED: Cycle is complete. Intent -> Work -> Verification -> Truth.")
    else:
        print(f"\n⚠️ DRILL STATUS: {result.value} (Check forensic logs)")

    # Cleanup
    shutil.rmtree(fake_brain)

if __name__ == "__main__":
    asyncio.run(run_drill())
