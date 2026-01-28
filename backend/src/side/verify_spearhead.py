import sys
from pathlib import Path
import asyncio
import tempfile
import os

# Add backend python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root / "backend" / "src"))

from side.tools.forensics_tool import ForensicsTool

async def verify_spearhead():
    print("⚔️ Verifying the Spearhead (Semantic Foreman Logic)...")
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        root = Path(tmpdirname)
        
        # 1. PLANT THE EVIDENCE (Create a "Bad" Project)
        
        # A. The Arrow Pattern (Deep Logic Violation)
        (root / "arrow.py").write_text("""
def terrible_nesting(x):
    if x > 0:
        if x < 100:
            if x % 2 == 0:
                print("Even")
            else:
                if x % 3 == 0:
                    print("Div 3")
        else:
            print("Too big")
""")
        
        # B. The Hardcoded Secret (Security Violation)
        (root / "config.py").write_text("""
AWS_SECRET = "AKIA1234567890ABCDEF" 
MESSAGE = "This is a secret"
""")
        
        print(f"📂 Created dummy project at {root}")
        
        # 2. RUN THE AUDIT (Using Semantic Forensics)
        tool = ForensicsTool(project_path=root)
        print("🕵️  Running Forensic Audit (LLM Powered)...")
        
        # We run specific queries to prove "Intent" checking
        # 1. Architectural Check
        print("   > Checking for Cognitive Complexity (Arrow Pattern)...")
        res_arch = await tool.scan_codebase("Identify nested logic and arrow patterns that violate clean code.")
        
        # 2. Security Check
        print("   > Checking for Hardcoded Secrets...")
        res_sec = await tool.scan_codebase("Find all hardcoded secrets and API keys.")
        
        # 3. VERIFY FINDINGS
        print("\n🔍 Analyzing Findings...")
        
        # We check for "Violation" or specific file markers, avoiding the query echo.
        # The result string usually contains "[FILE]:" or "Violation" if issues are found.
        # "Forensics Clean" means nothing found.
        
        res_arch_str = str(res_arch).lower()
        res_sec_str = str(res_sec).lower()
        
        is_clean_arch = "forensics clean" in res_arch_str
        is_clean_sec = "forensics clean" in res_sec_str
        
        found_arrow = (not is_clean_arch) and ("arrow" in res_arch_str or "nested" in res_arch_str)
        found_secret = (not is_clean_sec) and ("secret" in res_sec_str or "key" in res_sec_str)
        
        if found_arrow:
            print(f"✅ DETECTED: Deep Logic (Arrow Pattern)")
            print(f"   Evidence: {str(res_arch)[:100]}...")
        else:
            print(f"❌ MISSED: Arrow Pattern not found.")
            print(f"   Raw: {res_arch}")
            
        if found_secret:
            print(f"✅ DETECTED: Security (Hardcoded Secret)")
            print(f"   Evidence: {str(res_sec)[:100]}...")
        else:
            print(f"❌ MISSED: Secrets not found.")
            
        # 4. REPORT CARD
        print("\n🏆 Spearhead Status:")
        print(f"[{'x' if found_arrow else ' '}] Deep Logic (Arrow Pattern)")
        print(f"[{'x' if found_secret else ' '}] Security (Hardcoded Secrets)")
        
        if found_arrow and found_secret:
            print("\n✅ V1 LAUNCH READY: The Spear is Sharp.")
            return True
        else:
            print("\n❌ NOT READY: Gaps detected in Forensic Engine.")
            return False

if __name__ == "__main__":
    asyncio.run(verify_spearhead())
