import asyncio
from pathlib import Path
from .utils import ux

def handle_health(args):
    from side.health import health
    ux.display_status("Initiating real-time system scan...", level="info")
    
    target_path = Path(args.path).resolve()
    # Simplified Health Logic
    health_context = {
        "PORT": "3999", 
        "BRANCH": "main", 
        "target_file": str(target_path)
    }
    result = health.check_health(health_context)
    
    ux.display_header("System Health Report")
    if result.violations:
        for v in result.violations:
            ux.display_status(v, level="error")
    else:
        ux.display_status("No anomalies detected.", level="success")
        ux.display_status("Codebase is aligned with configured rules.", level="info")
    ux.display_footer()

def handle_audit(args):
    """Codebase Audit Wrapper"""
    from side.tools.audit import handle_run_audit
    
    ux.display_status(f"Starting Codebase Audit (Dimension: {args.dimension})...", level="info")
    
    severity = args.severity
    if severity == "all":
        severity = "critical,high,medium,low,info"
        
    result = asyncio.run(handle_run_audit({
        "dimension": args.dimension,
        "severity": severity
    }))
    ux.display_header(f"Audit Report: {args.dimension.upper()}")
    ux.display_panel(result)
    ux.display_footer()
