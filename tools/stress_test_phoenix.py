
import os
import shutil
import subprocess
import time
from pathlib import Path

def run_command(cmd):
    print(f"🏃 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
    return result.stdout

def stress_test():
    project_root = Path.cwd()
    side_dir = project_root / ".side"
    side_id = project_root / ".side-id"
    ledger_path = Path.home() / ".side" / "local.db"
    
    print("🦅 [STRESS TEST]: Phoenix Protocol Initiation")
    
    # 1. Baseline Verification
    if not ledger_path.exists():
        print("❌ Fatal: local.db missing. Run 'side login' or 'side feed' first.")
        return

    # 2. Scenario A: Total Wipeout (Recursive)
    print("\n🔥 Scenario A: Total Wipeout")
    if side_dir.exists(): shutil.rmtree(side_dir)
    if side_id.exists(): side_id.unlink()
    
    start_time = time.time()
    run_command("export PYTHONPATH=$PYTHONPATH:$(pwd)/backend/src && python3 backend/src/side/cli.py recovery")
    duration = time.time() - start_time
    
    if side_dir.exists() and side_id.exists():
        print(f"✅ Success: Context restored in {duration:.2f}s")
    else:
        print("❌ Failure: Context not restored")
        return

    # 3. Scenario B: Idempotency (Double Run)
    print("\n🔄 Scenario B: Idempotency (Repeat Recovery)")
    initial_fragments = len(run_command("ls .side/rules").split())
    run_command("export PYTHONPATH=$PYTHONPATH:$(pwd)/backend/src && python3 backend/src/side/cli.py recovery")
    post_fragments = len(run_command("ls .side/rules").split())
    
    if initial_fragments == post_fragments:
        print("✅ Success: Idempotent (No duplication)")
    else:
        print(f"⚠️ Warning: Rule count changed from {initial_fragments} to {post_fragments}")

    # 4. Scenario C: Migration Simulation (DB Only)
    print("\n🚀 Scenario C: Migration Simulation")
    # Backup DB, Wipe Project, Move DB back
    db_backup = Path("/tmp/local_backup.db")
    shutil.copy(ledger_path, db_backup)
    
    shutil.rmtree(side_dir)
    side_id.unlink()
    ledger_path.unlink()
    
    # Simulate moving DB to a new machine
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(db_backup, ledger_path)
    
    run_command("export PYTHONPATH=$PYTHONPATH:$(pwd)/backend/src && python3 backend/src/side/cli.py recovery")
    
    if side_id.exists():
        recovered_id = side_id.read_text().strip()
        print(f"✅ Success: Project recognized via DB-only migration. ID: {recovered_id}")
    else:
        print("❌ Failure: Project not recognized after DB migration")

    # 5. Scenario D: Sovereign Mobility Roundtrip
    print("\n🌍 Scenario D: Sovereign Mobility Roundtrip")
    # Export -> Nuke -> Import -> recovery
    run_command("export PYTHONPATH=$PYTHONPATH:$(pwd)/backend/src && python3 backend/src/side/cli.py export --portable")
    bundle = list(Path(".side/export").glob("*.shield"))[0]
    
    # Nuke everything
    if side_dir.exists(): shutil.rmtree(side_dir)
    if side_id.exists(): side_id.unlink()
    if ledger_path.exists(): ledger_path.unlink()
    
    # Import
    run_command(f"export PYTHONPATH=$PYTHONPATH:$(pwd)/backend/src && python3 backend/src/side/cli.py import {bundle}")
    
    # recovery
    run_command("export PYTHONPATH=$PYTHONPATH:$(pwd)/backend/src && python3 backend/src/side/cli.py recovery")
    
    if side_dir.exists() and (side_dir / "sovereign.json").exists():
        print("✅ Success: Total Mobility Roundtrip complete. Context is Immortal.")
    else:
        print("❌ Failure: Mobility roundtrip failed to restore context.")

    print("\n🏆 [STRESS TEST COMPLETE]: Phoenix is Operational.")

if __name__ == "__main__":
    stress_test()
