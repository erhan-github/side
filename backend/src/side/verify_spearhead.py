import sys
from pathlib import Path
import asyncio
import tempfile
import os

# Add backend python path
project_root = Path("/Users/erhanerdogan/Desktop/side")
backend_path = project_root / "backend" / "src"
sys.path.append(str(backend_path))

from side.forensic_audit.runner import ForensicAuditRunner

async def verify_spearhead():
    print("⚔️ Verifying the Spearhead (V1 Launch Logic)...")
    
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
        
        # C. Missing Strategy (No VISION.md)
        # We just don't create it.
        
        print(f"📂 Created dummy project at {root}")
        
        # 2. RUN THE AUDIT
        runner = ForensicAuditRunner(str(root)) # Pass project root to init
        print("🕵️  Running Forensic Audit...")
        
        results = await runner.run(
            only_fast=False
        )
        
        # 3. VERIFY FINDINGS
        print("\n🔍 Analyzing Findings...")
        
        found_arrow = False
        found_secret = False
        found_vision = False
        
        # Flatten results
        all_results = []
        for dim, res_list in results.results_by_dimension.items():
            all_results.extend(res_list)
            
        for res in all_results:
            # Aggregate all text from the result
            text_corpus = f"{res.check_name} {res.notes or ''} {res.recommendation or ''}".lower()
            if res.evidence:
                for ev in res.evidence:
                    text_corpus += f" {ev.description} {ev.context or ''}"
            
            text_corpus = text_corpus.lower()
            
            # Check Arrow Pattern
            if "cognitive complexity" in text_corpus or "nested" in text_corpus:
                path = res.evidence[0].file_path if res.evidence else '?'
                print(f"✅ DETECTED: Deep Logic (Arrow Pattern) in {path}")
                found_arrow = True
                
            # Check Secret
            if "secret" in text_corpus or "credential" in text_corpus or "api key" in text_corpus:
                 path = res.evidence[0].file_path if res.evidence else '?'
                 print(f"✅ DETECTED: Security (Hardcoded Secret) in {path}")
                 found_secret = True

            # Check Missing Vision
            if "vision" in text_corpus and "missing" in text_corpus:
                print(f"✅ DETECTED: Strategy (Missing Vision)")
                found_vision = True
                
        # 4. REPORT CARD
        print("\n🏆 Spearhead Status:")
        print(f"[{'x' if found_arrow else ' '}] Deep Logic (Arrow Pattern)")
        print(f"[{'x' if found_secret else ' '}] Security (Hardcoded Secrets)")
        print(f"[{'x' if found_vision else ' '}] Strategy (Missing Vision Doc)")
        
        if found_arrow and found_secret and found_vision:
            print("\n✅ V1 LAUNCH READY: The Spear is Sharp.")
            return True
        else:
            print("\n❌ NOT READY: Gaps detected in Forensic Engine.")
            return False

if __name__ == "__main__":
    asyncio.run(verify_spearhead())
