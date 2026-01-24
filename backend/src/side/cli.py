import argparse
import asyncio
import sys
import uvicorn
from pathlib import Path

from side.forensic_audit.runner import ForensicAuditRunner
from side.intel.intelligence_store import IntelligenceStore
from side.storage.simple_db import SimplifiedDatabase
from side.ui.dashboard_server import app as dashboard_app

def run_audit(project_path="."):
    """Run the forensic audit."""
    print(f"🔍 [Side Intelligence] Auditing {project_path}...")
    runner = ForensicAuditRunner(project_path)
    asyncio.run(runner.run_and_report()) # Using existing method

def promote_finding(finding_id: str, project_path="."):
    """Promote a finding to a strategic plan."""
    db = SimplifiedDatabase(Path(project_path) / ".side" / "local.db")
    store = IntelligenceStore(db)
    
    # Need project_id
    project_id = db.get_project_id(Path(project_path))
    
    plan_id = store.promote_finding_to_plan(project_id, finding_id)
    
    if plan_id:
        print(f"✅ Promoted Finding {finding_id[:8]} -> Plan {plan_id}")
    else:
        print(f"❌ Failed to promote finding {finding_id} (Not found or error).")

def serve_dashboard(port=8080):
    """Serve the War Room dashboard."""
    print(f"🚀 [Side Intelligence] Dashboard live at http://0.0.0.0:{port}")
    uvicorn.run(dashboard_app, host="0.0.0.0", port=port)

def main():
    parser = argparse.ArgumentParser(description="Side Intelligence CLI - Your Silent Partner.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Audit Command
    audit_parser = subparsers.add_parser("audit", help="Run forensic audit")
    audit_parser.add_argument("path", nargs="?", default=".", help="Project path")
    
    # Promote Command
    promote_parser = subparsers.add_parser("promote", help="Promote a Finding to a Plan")
    promote_parser.add_argument("finding_id", help="The ID of the finding to promote")
    
    # Serve Command
    serve_parser = subparsers.add_parser("serve", help="Launch the Visual Graph Dashboard")
    serve_parser.add_argument("--port", type=int, default=8080, help="Port to bind to")

    args = parser.parse_args()
    
    if args.command == "audit":
        run_audit(args.path)
    elif args.command == "promote":
        promote_finding(args.finding_id)
    elif args.command == "serve":
        serve_dashboard(args.port)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
