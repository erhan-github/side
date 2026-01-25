import sys
from pathlib import Path
import json

# Add backend python path
project_root = Path("/Users/erhanerdogan/Desktop/side")
backend_path = project_root / "backend" / "src"
sys.path.append(str(backend_path))

from side.strategic_engine import StrategicDecisionEngine, StrategicContext, DecisionType
from side.storage.simple_db import SimplifiedDatabase

def test_persistence():
    print("🧠 Testing Brain Persistence...")
    
    # 1. Setup Context
    context = StrategicContext(
        tech_stack=["Python", "FastAPI"],
        team_size=5,
        team_skills=["Python"],
        stage="pmf",
        users=1000,
        revenue=100.0,
        runway_months=12,
        focus_area="backend",
        recent_commits=10,
        open_issues=2,
        project_path=str(project_root)
    )
    
    engine = StrategicDecisionEngine()
    
    # 2. Trigger Heuristic Decision (Monolith vs Microservices)
    print("🤖 Asking: Monolith vs Microservices...")
    rec = engine.analyze_architecture_decision("Should I use a monolith?", context)
    print(f"✅ Recommendation: {rec.recommendation}")
    
    # 3. Verify Database
    print("\n🔍 Checking Database...")
    db = SimplifiedDatabase()
    project_id = db.get_project_id(project_root)
    print(f"📂 Project ID: {project_id}")
    
    with db._connection() as conn:
        rows = conn.execute(
            "SELECT * FROM decisions WHERE project_id = ? ORDER BY created_at DESC LIMIT 1",
            (project_id,)
        ).fetchall()
        
        if not rows:
            print("❌ FAIL: No decision found in database!")
            return False
            
        row = rows[0]
        print(f"✅ SUCCESS: Decision found!")
        print(f"   - Question: {row['question']}")
        print(f"   - Answer: {row['answer']}")
        print(f"   - Reasoning: {row['reasoning']}")
        
        if row['answer'] == rec.recommendation:
            print("✅ Data Integrity: Match confirmed.")
            return True
        else:
            print(f"❌ FAIL: Mismatch. DB: {row['answer']} vs Rec: {rec.recommendation}")
            return False

if __name__ == "__main__":
    test_persistence()
