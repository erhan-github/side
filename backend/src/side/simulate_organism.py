"""
Simulation of the Living Organism.
Verifies the end-to-end flow of the Silent Architect.
"""
import sys
import asyncio
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from side.storage.simple_db import SimplifiedDatabase
from side.workers.queue import JobQueue
from side.workers.decomposer import TaskDecomposer
from side.workers.engine import WorkerEngine, handle_security_scan, handle_complexity_gauge, handle_dependency_map
from side.llm.orchestrator import LLMOrchestrator

async def run_simulation():
    print("🚀 Starting Organism Simulation...")
    
    # 1. Init Core
    db = SimplifiedDatabase()
    queue = JobQueue(db)
    decomposer = TaskDecomposer(queue, "sim_project")
    
    # 1.5 Clear old jobs for clean test
    with db._connection() as conn:
        conn.execute("DELETE FROM jobs")
        conn.commit()
    
    # 2. Trigger Strategy (The Trojan Horse)
    print("🧠 Decomposing 'Deep Audit' Request...")
    batch_id = decomposer.decompose_request("Audit Project", {})
    print(f"   -> Batch ID: {batch_id}")
    
    # 3. Start Worker (The Muscle)
    engine = WorkerEngine(queue)
    # Register mock handlers for v0.1
    # Full mapping for Decomposer outputs
    engine.register_handler("audit_dimension", handle_security_scan) 
    engine.register_handler("context_search", handle_dependency_map)
    engine.register_handler("dependency_map", handle_dependency_map)
    engine.register_handler("discover_tests", handle_complexity_gauge) # Mock
    engine.register_handler("security_scan", handle_security_scan)
    engine.register_handler("complexity_gauge", handle_complexity_gauge)
    
    # Run loop briefly
    scan_task = asyncio.create_task(engine.start())
    print("⚙️  Worker Running for 3 seconds...")
    await asyncio.sleep(3)
    engine.stop()
    await scan_task
    
    # 4. Synthesize (The Brain)
    orchestrator = LLMOrchestrator()
    # Fetch results from DB
    with db._connection() as conn:
        rows = conn.execute("SELECT result FROM jobs WHERE status='completed'").fetchall()
        results = [dict(row) for row in rows]
        
    print(f"📊 Completed Jobs: {len(results)}")
    
    # 5. Check Telemetry
    with db._connection() as conn:
        ops = conn.execute("SELECT type, context FROM events WHERE type LIKE 'OP_%' ORDER BY id DESC LIMIT 5").fetchall()
        print(f"📡 Telemetry Captured ({len(ops)} events):")
        for op in ops:
            print(f"   [{op['type']}] {op['context']}")

    insight = await orchestrator.synthesize_findings(results)
    print(f"💡 Orchestrator Insight:\n{insight}")
    
    if len(results) > 0:
        print("✅ SIMULATION SUCCESS: The Organism is Alive.")
    else:
        print("❌ SIMULATION FAILED: No jobs completed.")

if __name__ == "__main__":
    asyncio.run(run_simulation())
