
import logging
import sys
import os

# Mock the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY")

# Import the ContextEngine
try:
    from side.storage.modules.base import ContextEngine
except ImportError:
    # Adjust path if needed
    sys.path.append(os.path.join(os.getcwd(), "src"))
    from side.storage.modules.base import ContextEngine

def test_fts5_powers():
    print("--- 🦅 POWER VERIFICATION ---")
    engine = ContextEngine(db_path=":memory:")
    
    with engine.connection() as conn:
        try:
            print(f"Testing FTS5 on driver: {conn.__class__.__module__}")
            conn.execute("CREATE VIRTUAL TABLE fts_test USING fts5(content, tokenize='porter unicode61')")
            conn.execute("INSERT INTO fts_test(content) VALUES ('The sovereign eagle flies fast')")
            res = conn.execute("SELECT * FROM fts_test WHERE fts_test MATCH 'sovereign'").fetchone()
            if res:
                print("✅ FTS5 Power: ACTIVE (Search successful)")
            else:
                print("❌ FTS5 Power: DEGRADED (Query returned no results)")
        except Exception as e:
            print(f"❌ FTS5 Power: FAILED ({e})")

if __name__ == "__main__":
    test_fts5_powers()
