import os
import sys
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from side.audit.experts.architect import ChiefArchitect
from side.audit.experts.base import ExpertContext
from side.audit.core import AuditStatus
from side.server import load_env_file

# Setup
logging.basicConfig(level=logging.ERROR)
load_env_file()

def verify_architect():
    print("🚀 Initializing The Architect...")
    expert = ChiefArchitect()
    
    # 1. Test Case: God Class (Bad Architecture)
    god_class_code = """
class UserManager:
    def __init__(self):
        self.db = "postgres://"
        
    def create_user(self, name, email):
        # Validate email
        if "@" not in email:
            raise ValueError("Bad email")
        
        # Connect DB
        print("Connecting...")
        
        # Send Welcome Email
        import smtplib
        server = smtplib.SMTP('localhost')
        server.sendmail("admin@side.ai", email, "Welcome!")
        
        # Generate Invoice
        tax = 0.2
        print(f"Invoice generated for {name}")
        
        # Update Analytics
        with open("logs.txt", "a") as f:
            f.write(f"User {name} created")
"""
    
    print("\n🏗️ Analyzing 'God Class' Snippet...")
    ctx_bad = ExpertContext(
        check_id="ARCH-001",
        file_path="src/managers/user_manager.py",
        content_snippet=god_class_code,
        language="python"
    )
    
    result_bad = expert.review(ctx_bad)
    
    print(f"\n[RESULT] Status: {result_bad.status}")
    print(f"[RESULT] Notes: {result_bad.notes}")
    
    if result_bad.status in [AuditStatus.FAIL, AuditStatus.WARNING]:
        print("✅ SUCCESS: Architect identified the SRP violation (bloated class).")
    else:
        print("❌ FAILURE: Architect missed the bad design.")

    # 2. Test Case: Clean Code (Repository Pattern)
    clean_code = """
from typing import Protocol

class UserRepository(Protocol):
    def save(self, user: User) -> None:
        ...

class SqlUserRepository(UserRepository):
    def __init__(self, db_session):
        self.session = db_session
        
    def save(self, user: User) -> None:
        self.session.add(user)
        self.session.commit()
"""
    
    print("\n🏗️ Analyzing 'Clean Code' Snippet...")
    ctx_good = ExpertContext(
        check_id="ARCH-002",
        file_path="src/repositories/user.py",
        content_snippet=clean_code,
        language="python"
    )
    
    result_good = expert.review(ctx_good)
    
    print(f"\n[RESULT] Status: {result_good.status}")
    print(f"[RESULT] Notes: {result_good.notes}")
    
    if result_good.status == AuditStatus.PASS:
        print("✅ SUCCESS: Architect approved the clean design.")
    else:
        print(f"❌ FAILURE: Architect complained about clean code: {result_good.status}")

if __name__ == "__main__":
    verify_architect()
