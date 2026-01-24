import logging
import json
import sqlite3
from typing import List, Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from side.storage.simple_db import SimplifiedDatabase
from side.intel.intelligence_store import IntelligenceStore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sidelith God-View Dashboard")

# Paths
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"

# Initialize DB connection (Global Intelligence)
db = SimplifiedDatabase() 
store = IntelligenceStore(db)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/graph")
async def get_graph():
    """Returns the LIVE graph from local.db."""
    nodes = []
    links = []
    
    project_id = db.get_project_id()
    
    with db._connection() as conn:
        # 1. FETCH PLANS (Strategic Backbone)
        cursor = conn.execute("SELECT id, title, type, status, parent_id FROM plans WHERE project_id = ?", (project_id,))
        plans = cursor.fetchall()
        for p in plans:
            nodes.append({
                "id": p["id"],
                "type": "plan",
                "label": p["title"],
                "group": "strategy",
                "properties": {"status": p["status"], "type": p["type"]}
            })
            # Plan Hierarchy
            if p["parent_id"]:
                links.append({
                    "source": p["parent_id"],
                    "target": p["id"],
                    "type": "parent_of"
                })

        # 2. FETCH DECISIONS (Guard Rails)
        cursor = conn.execute("SELECT id, question, answer, plan_id FROM decisions WHERE project_id = ?", (project_id,))
        decisions = cursor.fetchall()
        for d in decisions:
            nodes.append({
                "id": d["id"],
                "type": "decision",
                "label": d["question"],
                "group": "logic",
                "properties": {"answer": d["answer"]}
            })
            # Link to Plan
            if d["plan_id"]:
                links.append({
                    "source": d["id"],
                    "target": d["plan_id"],
                    "type": "supports"
                })

        # 3. FETCH FINDINGS (Forensic Evidence)
        # Using store helper for consistent filtering
        findings = store.get_active_findings(project_id)
        for f in findings:
            # Shorten label
            label = f["type"]
            nodes.append({
                "id": f["id"],
                "type": "finding",
                "label": label,
                "group": "forensic",
                "properties": {
                    "severity": f["severity"],
                    "file": f["file"]
                }
            })
            # Heuristic Linking: If file matches any plan title keywords? (Future AI Linker)
            # For now, findings are separate clusters floating around the project center?
            # Let's create a "PROJECT" node to center them.
            
    # Center Node (The Project)
    nodes.append({
        "id": "PROJECT_ROOT",
        "type": "project",
        "label": "Current Project",
        "group": "core",
        "properties": {}
    })
    
    # Link orphans to Project Root
    for n in nodes:
        if n["id"] != "PROJECT_ROOT":
            # If it has no other links targeting it? 
            # Simple approach: Link all top-level Plans and Findings to Project
            is_linked = False
            for l in links:
                if l["target"] == n["id"] or l["source"] == n["id"]:
                    is_linked = True # It has some connection
                    break
            
            # Findings always link to project for now
            if n["type"] == "finding":
                 links.append({"source": "PROJECT_ROOT", "target": n["id"], "type": "affects"})
            # Root plans
            elif n["type"] == "plan" and not n["properties"].get("parent_id"): # Logic check needed, but let's just link if 'parent_id' was None above
                 # We need to check if it WAS linked above. P["parent_id"] covers it.
                 # Re-looping isn't efficient.
                 pass

    # Re-pass to link top-level plans
    for p in plans:
        if not p["parent_id"]:
             links.append({"source": "PROJECT_ROOT", "target": p["id"], "type": "strategic_goal"})

    return {"nodes": nodes, "links": links}

@app.get("/api/stats")
async def get_stats():
    """Returns high-level forensic metrics from Real DB."""
    project_id = db.get_project_id()
    
    # Use Store for stats
    f_stats = store.get_finding_stats(project_id)
    
    # Count plans/decisions manually
    with db._connection() as conn:
        plan_count = conn.execute("SELECT COUNT(*) FROM plans WHERE project_id = ?", (project_id,)).fetchone()[0]
        decision_count = conn.execute("SELECT COUNT(*) FROM decisions WHERE project_id = ?", (project_id,)).fetchone()[0]

    return {
        "finding_count": f_stats["total"],
        "critical_issues": f_stats["critical"],
        "plans_active": plan_count,
        "decisions_logged": decision_count,
        "health_grade": store.get_strategic_iq(project_id) # Reuse the scoring logic
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
