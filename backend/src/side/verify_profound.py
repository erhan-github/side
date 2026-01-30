import asyncio
import logging
import sys
from pathlib import Path
from side.storage.modules.base import SovereignEngine
from side.intel.auto_intelligence import AutoIntelligence

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

async def verify_profound():
    project_path = Path.cwd()
    engine = SovereignEngine()
    intel = AutoIntelligence(project_path)
    project_id = engine.get_project_id()
    
    logger.info("🏛️ [VERIFY]: Initializing Profound Intelligence Audit...")
    
    # 1. Verify Balance Tracking
    balance = engine.accounting.get_balance(project_id)
    logger.info(f"🏦 [BALANCE]: Current Project Balance: {balance} SU")
    
    # 2. Verify AST Gating (Simulated Routine Commits)
    # We will run a small historic feed and look for GATED logs
    logger.info("🕰️ [FEED]: Running Historic Feed (Lookback 1 month)...")
    await intel.historic_feed(months=1)
    
    # 3. Check Balance After Feed
    new_balance = engine.accounting.get_balance(project_id)
    logger.info(f"🏦 [BALANCE]: New Balance: {new_balance} SU (Delta: {balance - new_balance})")
    
    # 4. Verify Accounting History
    history = engine.accounting.get_history(project_id, limit=5)
    logger.info("📜 [HISTORY]: Recent Transactions:")
    for entry in history:
        logger.info(f"  - {entry['amount']} SU | {entry['reason']}")

if __name__ == "__main__":
    asyncio.run(verify_profound())
