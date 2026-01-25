
import asyncio
import sys
from pathlib import Path

# Mock sys.path to find backend
sys.path.append(str(Path.cwd() / "backend" / "src"))

from side.server import prompt_manager

async def test_truth():
    print("🔍 Testing Truth Engine...")
    
    # 1. Call the Prompt Handler
    try:
        # We trigger the logic inside get_prompt_result
        result = prompt_manager.get_prompt_result("check_truth", {})
        
        print("\n✅ Prompt Generated Successfully:")
        print(f"--- Description: {result.description} ---")
        msg = result.messages[0].content.text
        # print(msg)
        
        if "MISSION.md" in msg or "VISION.md" in msg or "README.md" in msg:
            print("\n✅ SUCCESS: Documentation context detected.")
            return

        # It might be empty if files don't exist in the current mock setup, 
        # but the prompt should still have the preamble.
        if "Reality Check" in msg:
            print("\n✅ SUCCESS: Prompt template is correct.")
            return

        print("\n❌ FAILURE: Prompt content is unexpected.")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(test_truth())
