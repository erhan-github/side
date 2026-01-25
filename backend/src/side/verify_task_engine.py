import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from side.storage.simple_db import SimplifiedDatabase
from side.workers.queue import JobQueue
from side.workers.decomposer import TaskDecomposer

def verify():
    # 1. Setup
    db = SimplifiedDatabase()
    queue = JobQueue(db)
    decomposer = TaskDecomposer(queue, "test_project")
    
    # 2. Action
    print("🤖 Requesting Refactor for 'auth.py'...")
    decomposer.decompose_request("Refactor auth.py", context={'file': 'auth.py'})
    
    # 3. Verify
    with db._connection() as conn:
        rows = conn.execute("SELECT type, priority FROM jobs WHERE status='pending'").fetchall()
        print(f"✅ Enqueued {len(rows)} micro-tasks:")
        for r in rows:
            print(f"   - {r['type']} (Priority {r['priority']})")
            
    if len(rows) >= 4:
        print("🎉 SUCCESS: Task Decomposer is operational.")
    else:
        print("❌ FAILURE: Jobs not found.")

if __name__ == "__main__":
    verify()
