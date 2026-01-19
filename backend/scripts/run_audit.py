#!/usr/bin/env python3
import sys
from pathlib import Path

# Add backend/src to path so we can import 'side'
# We walk up from backend/scripts/run_audit.py -> backend/src
sys.path.append(str(Path(__file__).parent.parent / "src"))

from side.audit import AuditRunner
from side.audit.probes import SecretsProbe, GitIgnoreProbe, NextJSProbe, PythonProbe

def main():
    # Detect Project Root (root of the repo)
    project_root = Path(__file__).parent.parent.parent.resolve()
    print(f"🚀 Starting Side Auditor on: {project_root}")
    
    # Initialize Runner
    runner = AuditRunner(str(project_root))
    
    # Register Probes
    # Phase 1: Security
    runner.register_probe(SecretsProbe())
    runner.register_probe(GitIgnoreProbe())
    
    # Phase 2: Stack
    runner.register_probe(NextJSProbe())
    runner.register_probe(PythonProbe())
    
    # Phase 4: Virtual Personnel
    # Loads .env internally via Side's config logic, or expects environment variables
    # We should ensure env is loaded if running as script
    from side.server import load_env_file
    load_env_file()
    
    # Import locally to avoid issues if optional deps missing
    try:
        from side.audit.probes.expert import SecurityExpertProbe, PerformanceExpertProbe
        runner.register_probe(SecurityExpertProbe())
        runner.register_probe(PerformanceExpertProbe())
        print("✅ Registered Virtual Personnel: Sentinel & The Scaler")
    except ImportError:
        print("⚠️ Failed to register Virtual Personnel")
    
    # Run Audit
    # Using the pre_launch_v1 template
    report_markdown = runner.run(template_name="pre_launch_v1")
    
    # Output to docs/AUDIT_REPORT.md
    output_path = project_root / "backend/docs/AUDIT_REPORT.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_markdown)
    
    print(f"\n✅ Audit Complete! Report generated at: {output_path}")

if __name__ == "__main__":
    main()
