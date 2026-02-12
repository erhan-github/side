"""
Palantir Readiness Auditor - SQLite Power Extension Verification.
"""
import sys

try:
    import pysqlite3 as sqlite3
    print("✓ Driver: pysqlite3-binary (High-Fidelity)")
except ImportError:
    import sqlite3
    print("! Driver: standard sqlite3 (Potential Degraded Search)")

def check_extension(name: str):
    try:
        conn = sqlite3.connect(":memory:")
        res = conn.execute(f"SELECT count(*) FROM sqlite_master WHERE name='x' AND type='table'").fetchall()
        
        if name == "fts5":
            conn.execute("CREATE VIRTUAL TABLE x USING fts5(y)")
        elif name == "json1":
            conn.execute("SELECT json('{\"a\":1}')")
            
        print(f"✓ Extension: {name.upper()}")
        return True
    except Exception as e:
        print(f"✕ Extension: {name.upper()} - {e}")
        return False

print(f"System SQLite Version: {sqlite3.sqlite_version}")
print("-" * 40)

all_ok = True
all_ok &= check_extension("fts5")
all_ok &= check_extension("json1")

print("-" * 40)
if all_ok:
    print("💎 PALANTIR READINESS: CRYSTAL CLEAR")
else:
    print("⚠️  SYSTEM DEGRADATION: Search performance may be throttled.")
