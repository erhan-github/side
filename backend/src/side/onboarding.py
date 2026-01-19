"""
Side Onboarding - Day 1 Magic.

Auto-creates .side/plan.md and runs baseline audit on first use.
"""
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


PLAN_TEMPLATE = '''# Side Project Plan

## Project
- **Name**: {project_name}
- **Stack**: {stack}
- **Created**: {created_date}
- **Side Version**: 1.0.0

## Health Checks
{health_checks}

## Goals
<!-- Add your goals here. Example: -->
<!-- - [ ] Launch MVP by March 1 -->
<!-- - [ ] Get 100 users -->

## Audit History
| Date | Score | Change |
|------|-------|--------|
| {created_date} | {baseline_score}% | Baseline |
'''


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


def create_side_directory(project_root: Path) -> Path:
    """Create .side directory if it doesn't exist."""
    side_dir = project_root / ".side"
    side_dir.mkdir(parents=True, exist_ok=True)
    
    # Create history subdirectory
    (side_dir / "history").mkdir(exist_ok=True)
    
    # Add to .gitignore if not already there
    gitignore = project_root / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".side/" not in content:
            with open(gitignore, "a") as f:
                f.write("\n# Side AI\n.side/\n")
    else:
        gitignore.write_text("# Side AI\n.side/\n")
        
    return side_dir


def create_plan_md(
    project_root: Path,
    baseline_score: int = 0,
    health_checks: Optional[list[str]] = None
) -> Path:
    """Create .side/plan.md with project info."""
    side_dir = create_side_directory(project_root)
    plan_path = side_dir / "plan.md"
    
    project_name = detect_project_name(project_root)
    stack = detect_stack(project_root)
    
    # Default health checks
    if health_checks is None:
        health_checks = [
            "- [ ] Security Score > 80%",
            "- [ ] No hardcoded secrets",
            "- [ ] Performance Score > 80%",
            "- [ ] All tests passing",
        ]
    
    content = PLAN_TEMPLATE.format(
        project_name=project_name,
        stack=", ".join(stack),
        created_date=datetime.now().strftime("%Y-%m-%d"),
        health_checks="\n".join(health_checks),
        baseline_score=baseline_score,
    )
    
    plan_path.write_text(content)
    return plan_path


def run_onboarding(project_root: str) -> dict:
    """
    Run the Day 1 onboarding flow.
    
    Returns dict with onboarding results.
    """
    root = Path(project_root)
    
    # 1. Create .side directory and plan.md
    plan_path = create_plan_md(root)
    
    # 2. Return results
    return {
        "success": True,
        "plan_path": str(plan_path),
        "project_name": detect_project_name(root),
        "stack": detect_stack(root),
        "message": f"✅ Side is ready! Your plan is at .side/plan.md",
    }


def is_side_initialized(project_root: str) -> bool:
    """Check if Side has been initialized for this project."""
    return (Path(project_root) / ".side" / "plan.md").exists()
