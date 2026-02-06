"""
Side Onboarding - Day 1 Magic.

[SOVEREIGN ARCHITECTURE]: All strategic context is stored in the database.
"""
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


def detect_project_name(project_root: Path) -> str:
    """Detect project name from package.json or pyproject.toml."""
    # Try package.json
    pkg_json = project_root / "package.json"
    if pkg_json.exists():
        import json
        try:
            data = json.loads(pkg_json.read_text())
            return data.get("name", project_root.name)
        except Exception:
            pass
            
    # Try pyproject.toml
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            for line in content.split("\n"):
                if line.strip().startswith("name"):
                    return line.split("=")[1].strip().strip('"').strip("'")
        except Exception:
            pass
            
    return project_root.name


def detect_stack(project_root: Path) -> list[str]:
    """Detect tech stack from project files."""
    stack = []
    
    if (project_root / "package.json").exists():
        stack.append("Node.js")
        # Check for specific frameworks
        try:
            import json
            pkg = json.loads((project_root / "package.json").read_text())
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "next" in deps:
                stack.append("Next.js")
            if "react" in deps:
                stack.append("React")
            if "typescript" in deps:
                stack.append("TypeScript")
        except Exception:
            pass
            
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        stack.append("Python")
        
    if (project_root / "Cargo.toml").exists():
        stack.append("Rust")
        
    if (project_root / "go.mod").exists():
        stack.append("Go")
        
    return stack if stack else ["Unknown"]


def ensure_gitignore_entry(project_root: Path) -> None:
    """Ensure .side-id is in gitignore."""
    gitignore = project_root / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".side-id" not in content:
            with open(gitignore, "a") as f:
                f.write("\n# Side AI\n.side-id\n")
    else:
        gitignore.write_text("# Side AI\n.side-id\n")


async def run_onboarding(project_root: str) -> dict:
    """
    Run the Day 1 onboarding flow with a LIVE Baseline Audit.
    
    [SOVEREIGN ARCHITECTURE]: Stores all data in the Strategic Database.
    
    Returns dict with onboarding results.
    """
    from collections import Counter
    from side.tools.core import get_database, get_auto_intel
    from side.services.billing import BillingService
    
    root = Path(project_root)
    db = get_database()
    
    # 1. Detect project info
    project_name = detect_project_name(root)
    stack = detect_stack(root)
    
    # 2. Get/Create Profile (this creates .side-id)
    auto_intel = get_auto_intel()
    profile = await auto_intel.get_or_create_profile(project_root)
    project_id = db.get_project_id()
    
    # 3. Real Forensics Audit (The Spear)
    from side.tools.forensics_tool import ForensicsTool
    spear = ForensicsTool()
    findings = spear.scan_project(str(project_root))
    
    # 4. [Anti-Abuse] Claim Trial (Repo Lock)
    billing = BillingService(db)
    billing.claim_trial(project_root)
    
    # 5. Calculate Strategic IQ
    iq_score = 100  # Default starter score
    max_iq = 400
    baseline_score = int((iq_score / max_iq) * 100)
    
    # 6. Store baseline in Strategic Database
    # Save as a strategic fact for future reference
    from uuid import uuid4
    db.strategic.save_fact(
        fact_id=str(uuid4()),
        project_id=project_id,
        content=f"Day 1 Baseline: {project_name} ({', '.join(stack)}) - Score: {baseline_score}%",
        tags=["baseline", "onboarding", "day1"],
        metadata={
            "project_name": project_name,
            "stack": stack,
            "baseline_score": baseline_score,
            "findings_count": len(findings),
            "onboarded_at": datetime.now().isoformat()
        }
    )
    
    # 7. Store initial findings as audits (already happens in forensics tool)
    # No need to duplicate in .md file
    
    # 8. Ensure gitignore has .side-id entry
    ensure_gitignore_entry(root)
    
    # 9. Return results (no file path since we don't create .md files)
    return {
        "success": True,
        "project_id": project_id,
        "project_name": project_name,
        "stack": stack,
        "iq_score": iq_score,
        "max_iq": max_iq,
        "baseline_score": baseline_score,
        "grade": "B",  # Default
        "findings_count": len(findings),
        "message": f"✅ Live Diagnostic Complete! Data stored in Sovereign Ledger.",
    }


def is_side_initialized(project_root: str) -> bool:
    """Check if Side has been initialized for this project."""
    # Check for the .side-id identity anchor
    return (Path(project_root) / ".side-id").exists()
