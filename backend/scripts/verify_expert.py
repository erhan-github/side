import os
import logging
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from side.audit.experts.security import SecurityExpert
from side.audit.experts.base import ExpertContext
from side.audit.core import AuditStatus

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_expert():
    print("🚀 Initializing Sentinel (Security Expert)...")
    
    # Check for API Key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ SKIPPING: GROQ_API_KEY not found in environment.")
        print("Please add GROQ_API_KEY to backend/.env")
        return

    expert = SecurityExpert()
    
    # 1. Test Case: Vulnerable Code (Hardcoded Secret)
    vulnerable_code = """
def connect_db():
    # TODO: Move to env var
    db_password = "[REDACTED_BY_FORENSICS]" 
    return db.connect("postgres", password=db_password)
"""
    
    print("\n🧐 Analyzing Vulnerable Snippet...")
    ctx = ExpertContext(
        check_id="TEST-001",
        file_path="src/db/connection.py",
        content_snippet=vulnerable_code,
        language="python"
    )
    
    result = expert.review(ctx)
    
    print(f"\n[RESULT] Status: {result.status}")
    print(f"[RESULT] Notes: {result.notes}")
    if result.evidence:
        print(f"[RESULT] Evidence: {result.evidence[0].description}")
        
    if result.status == AuditStatus.FAIL:
        print("✅ SUCCESS: Expert correctly identified the vulnerability.")
    else:
        print("❌ FAILURE: Expert missed the vulnerability.")

    # 2. Test Case: Safe Code
    safe_code = """
import os
def connect_db():
    db_password = os.getenv("DB_PASSWORD")
    if not db_password:
        raise ValueError("DB_PASSWORD required")
    return db.connect("postgres", password=db_password)
"""
    
    print("\n🧐 Analyzing Safe Snippet...")
    ctx_safe = ExpertContext(
        check_id="TEST-002",
        file_path="src/db/connection.py",
        content_snippet=safe_code,
        language="python"
    )
    
    result_safe = expert.review(ctx_safe)
    
    print(f"\n[RESULT] Status: {result_safe.status}")
    print(f"[RESULT] Notes: {result_safe.notes}")
    
    if result_safe.status == AuditStatus.PASS:
        print("✅ SUCCESS: Expert correctly passed the safe code.")
    else:
        print(f"❌ FAILURE: Expert flagged safe code as {result_safe.status}.")

if __name__ == "__main__":
    verify_expert()
