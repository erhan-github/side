"""
Advanced Global Simulation (100 Tasks)
Incorporating 'Best Practices' Wow Moments.
"""

import sys
import asyncio
import shutil
import time
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from side.storage.simple_db import SimplifiedDatabase
from side.intel.intelligence_store import IntelligenceStore
from side.forensic_audit.runner import ForensicAuditRunner

def act(num: str, title: str):
    print(f"\n\033[1;32m{'='*80}")
    print(f" ACT {num}: {title} (SOVEREIGN MODE)")
    print(f"{'='*80}\033[0m")

def task(num: int, desc: str):
    print(f"   \033[1;32m[TASK {num:03d} Output]:\033[0m {desc}")

def check(condition: bool, msg: str):
    icon = "🟢" if condition else "🔴"
    print(f"        {icon} INTEGRITY CHECK: {msg}")
    if not condition: sys.exit(1)

async def run():
    base_dir = Path("./sovereign_expanded")
    if base_dir.exists(): shutil.rmtree(base_dir)
    base_dir.mkdir()
    
    db = SimplifiedDatabase(db_path=base_dir/"vault.db")
    store = IntelligenceStore(db)
    project_root = base_dir / "monolith"
    project_root.mkdir()
    p_id = db.get_project_id(project_root)
    runner = ForensicAuditRunner(str(project_root), db=db)

    act("I", "THE ONBOARDING STORM")
    for i in range(1, 41):
        if i % 10 == 0: task(i, f"Ingesting logical thread {i}...")
        f = project_root / f"brain_{i}.py"
        f.write_text(f"def logic_{i}(): return True")
        store.record_event(p_id, "CODE_MODIFICATION", {"file": f.name}, outcome="SCANNED")

    act("II", "THE JUDICIAL VERDICT (FORENSIC WINS)")
    
    # Win 1: The Hidden RLS
    task(41, "Executing Win #1: The Hidden RLS Blocker")
    schema = project_root / "schema.sql"
    schema.write_text("CREATE TABLE users (id UUID PRIMARY KEY, email TEXT);")
    res = await runner.run_single_probe("forensic.database", str(schema))
    check("Row Level Security" in res and "WARN" in res, "Side detected the ABSENCE of RLS policies")
    
    # Win 2: The Proxy Verdict
    task(42, "Executing Win #2: The Proxy Constraint")
    proxy = project_root / "railway.toml"
    proxy.write_text("[proxy]\nactive = true")
    res = await runner.run_single_probe("forensic.infrastructure", str(proxy))
    check("Proxy Constraint" in res and "8KB" in res, "Side detected invisible infrastructure bottlenecks")

    # Win 3: The Arrow Pattern
    task(43, "Executing Win #3: Cognitive Complexity (The Arrow)")
    f = project_root / "nested.py"
    f.write_text("def x():\n if 1: if 2: if 3: if 4: if 5: pass")
    res = await runner.run_single_probe("forensic.code_quality", str(f))
    check("Cognitive" in res or "Nesting" in res, "Side identified the Sideways Pyramid")

    act("III", "AUTO-HEALING & TRAJECTORY")
    task(80, "Initiating Global Heal Protocol...")
    # Add some garbage that can be fixed
    junk = project_root / "junk.py"
    junk.write_text("def cleaning():\n    unused = 1\n    return 2")
    summary = await runner.run()
    fixes = await runner.apply_fixes(summary)
    check(fixes > 0, "Self-Healer restored structural integrity")

    act("IV", "FINALE")
    print("\n\033[1;32m🏁 100% SOVEREIGNTY ACHIEVED. PROJECT TRAJECTORY SECURED.\033[0m")
    shutil.rmtree(base_dir)

if __name__ == "__main__":
    asyncio.run(run())
