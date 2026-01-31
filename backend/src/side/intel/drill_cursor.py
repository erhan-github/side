"""
Cursor Integration Drill.

Verifies that the Ingester can read Cursor plans.
"""

import asyncio
import logging
import shutil
from pathlib import Path
from side.intel.conversation_ingester import ConversationIngester
from side.storage.simple_db import SimplifiedDatabase

logging.basicConfig(level=logging.INFO)

async def run_cursor_drill():
    # 1. Setup Mock Cursor Environment
    mock_cursor_dir = Path("/tmp/side_drill_cursor/plans")
    if mock_cursor_dir.exists(): shutil.rmtree(mock_cursor_dir)
    mock_cursor_dir.mkdir(parents=True)
    
    # 2. Create Dummy Cursor Plan
    print("👉 Creating Mock Cursor Plan...")
    plan_content = """---
name: Mock Cursor Task
overview: This is a test plan created by the drill script to verify parsing logic.
---

# Details
Some details here.
"""
    (mock_cursor_dir / "test_plan_001.plan.md").write_text(plan_content)
    
    # 3. Patch Ingester to look at mock dir
    print("👉 Running Ingester...")
    ingester = ConversationIngester()
    # Hack: Inject mock path into the CursorSource instance
    # We know CursorSource is index 1
    ingester.sources[1].plans_dir = mock_cursor_dir
    
    await ingester.ingest_all()
    
    # 4. Verify DB
    db = SimplifiedDatabase()
    session = db.intent_fusion.get_session("test_plan_001")
    
    if session:
        print(f"✅ SUCCESS: Ingested Session: {session['raw_intent']}")
        print(f"   Source: CURSOR (deduced)")
    else:
        print("❌ FAILURE: Session not found.")
        
    # Cleanup
    shutil.rmtree(Path("/tmp/side_drill_cursor"))

if __name__ == "__main__":
    asyncio.run(run_cursor_drill())
