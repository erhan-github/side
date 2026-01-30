import asyncio
import logging
import uuid
from pathlib import Path
from side.storage.modules.base import SovereignEngine
from side.intel.auto_intelligence import AutoIntelligence

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

async def verify_intent_and_roi():
    project_path = Path.cwd()
    engine = SovereignEngine()
    intel = AutoIntelligence(project_path)
    project_id = engine.get_project_id()
    
    logger.info("🏛️ [VERIFY]: Starting Strategic Intent & ROI Audit...")
    
    # 1. Setup a Test Objective
    # We'll create a plan that mentions 'AccountingStore' to test correlation
    plan_id = str(uuid.uuid4())
    engine.strategic.save_plan(
        project_id=project_id,
        plan_id=plan_id,
        title="Implement SU Accounting Module",
        plan_type="objective",
        description="Engineering objective to track Sovereign Units across the mesh."
    )
    logger.info(f"🎯 [PLAN]: Created Test Objective: 'Implement SU Accounting Module' ({plan_id})")
    
    # 2. Verify Intent Correlation
    # We'll manually test the bridging logic
    symbols = ["AccountingStore", "deduct_su"]
    objectives = engine.strategic.find_objectives_by_symbols(project_id, symbols)
    
    logger.info(f"🔗 [CORRELATION]: Searching objectives for symbols {symbols}...")
    for obj in objectives:
        logger.info(f"  - Matched: '{obj['title']}' (ID: {obj['id']})")
    
    if any(obj['id'] == plan_id for obj in objectives):
        logger.info("✅ [VERIFY]: Intent Correlation Successful.")
    else:
        logger.error("❌ [VERIFY]: Intent Correlation Failed.")

    # 3. Verify Averted Disaster Ledger (ROI)
    logger.info("🛡️ [ROI]: Simulating an Averted Disaster...")
    engine.forensic.log_averted_disaster(
        project_id=project_id,
        reason="Blocked non-local network egress from Pulse Engine.",
        su_saved=100,
        technical_debt="Prevented potential $5k security breach/leakage."
    )
    
    # Check if it's in the DB
    with engine.connection() as conn:
        row = conn.execute("SELECT * FROM averted_disasters WHERE project_id = ? ORDER BY created_at DESC LIMIT 1", (project_id,)).fetchone()
        if row:
            logger.info(f"✅ [VERIFY]: Averted Disaster Logged. ROI: {row['su_saved']} SU saved.")
            logger.info(f"📖 [REASON]: {row['reason']}")
        else:
            logger.error("❌ [VERIFY]: Averted Disaster logging failed.")

if __name__ == "__main__":
    asyncio.run(verify_intent_and_roi())
