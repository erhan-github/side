import asyncio
import logging
import uuid
from pathlib import Path
from side.storage.modules.base import ContextEngine
from side.intel.context_service import ContextService
from side.intel.decision_history import HistoryManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY_CAUSAL")

async def test_causal_integrity():
    project_path = Path("/Users/erhanerdogan/Desktop/side")
    engine = ContextEngine(project_path)
    service = ContextService(project_path, engine)
    
    session_id = f"test-enterprise-{uuid.uuid4().hex[:8]}"
    fix_id = f"fix-{uuid.uuid4().hex[:4]}"
    
    logger.info(f"🚀 Starting Enterprise-Level Causal Test. Session: {session_id}")
    
    # 1. Trigger a Friction Signal (A Crash)
    logger.info("📡 Step 1: Simulating log crash signal...")
    await service.log_friction_event(
        source="XCODE_SCAVENGER",
        event_type="CRASH_DETECTED",
        payload={
            "file": "AppDelegate.swift",
            "content": "Fatal error: Unexpectedly found nil",
            "fix_id": fix_id
        }
    )
    
    # 2. Record Decision History
    logger.info("🧠 Step 2: Simulating AI history chain...")
    history = HistoryManager.get(fix_id)
    if not history:
        raise Exception("History not created automatically by service!")
    
    history.session_id = session_id # Explicitly set for test
    history.record_context_injected(5, 1200)
    history.record_fix_applied("AppDelegate.swift", 42, "Added optional binding")
    history.record_verification_passed()
    
    # 3. Verify Relational Persistence
    logger.info("💾 Step 3: Verifying relational persistence in SQLite...")
    causal_timeline = engine.audits.get_causal_timeline(session_id)
    
    has_signal = any(t["type"] == "SIGNAL" and t["data"]["tool"] == "XCODE_SCAVENGER" for t in causal_timeline)
    has_reasoning = any(t["type"] == "REASONING" and t["data"]["event_type"] == "FIX_APPLIED" for t in causal_timeline)
    
    logger.info(f"Results: SignalsFound={has_signal}, ReasoningFound={has_reasoning}")
    
    if has_signal and has_reasoning:
        logger.info("✅ [CAUSAL INTEGRITY PASSED]: All signals and decisions are perfectly linked and preserved.")
    else:
        logger.error("❌ [CAUSAL INTEGRITY FAILED]: Disconnect found in the causal chain.")
        exit(1)

if __name__ == "__main__":
    asyncio.run(test_causal_integrity())
