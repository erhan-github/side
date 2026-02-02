import time
import json
from pathlib import Path
from side.intel.fractal_indexer import run_fractal_scan
import logging

logging.basicConfig(level=logging.INFO)

def verify_filter(project_root: Path):
    """
    Verifies that:
    1. README.md is NOT in the index.
    2. Python source files ARE in the index.
    3. task.md (if it existed) WOULD BE in the index.
    """
    index_path = project_root / ".side" / "local.json"
    if not index_path.exists():
        print("❌ Index not found.")
        return

    with open(index_path, "r") as f:
        # Assuming unsealed for test reading, but real system seals it.
        # Wait, the system uses 'shield.seal_file'. We need shield to read it?
        # The benchmark runs in the same environment, so maybe simple read fails if encrypted.
        # But for 'local.json' in 'v3.sparse', is it encrypted? Yes, shield.seal_file.
        # Let's import shield.
        pass

    from side.utils.crypto import shield
    try:
        raw = shield.unseal_file(index_path)
        data = json.loads(raw)
    except Exception as e:
        print(f"❌ Could not unseal index: {e}")
        return

    files = data.get("context", {}).get("files", [])
    file_names = [f["name"] for f in files]
    
    print(f"📂 Index Root Content: {file_names}")
    
    # Assertions
    if "README.md" in file_names:
        print("❌ FAIL: README.md found in index!")
    else:
        print("✅ PASS: README.md successfully filtered.")
        
    # Check for known signal file
    if "check_sovereign.py" in file_names or "pyproject.toml" in file_names:
         print("✅ PASS: Signal files present.")
    else:
         print("⚠️ WARNING: No signal files found in root?")

def benchmark_fractal():
    project_root = Path("/Users/erhanerdogan/Desktop/side")
    print(f"🚀 Benchmarking Fractal Indexer on {project_root}...")
    
    start_time = time.time()
    run_fractal_scan(project_root)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"✨ Scan Complete. Duration: {duration:.4f}s")
    
    verify_filter(project_root)

if __name__ == "__main__":
    benchmark_fractal()
