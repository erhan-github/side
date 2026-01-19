import os
import sys
import asyncio
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from side.sim.session import FocusGroup
from side.server import load_env_file

# Setup
logging.basicConfig(level=logging.ERROR) # Quiet logs
load_env_file()

async def run_demo():
    print("🚀 Starting Virtual Focus Group (Engineers)...")
    
    # 1. Content to test: A Landing Page Value Prop
    landing_page_text = """
    SIDE.AI - THE CHIEF STRATEGY OFFICER IN YOUR POCKET.
    
    Stop coding blind. Side reads your entire codebase and tells you what to build next.
    It's like having a Palantir-level strategist in your terminal.
    
    - Monorepo aware
    - Market aware
    - Totally private (Local DB)
    
    Pricing: $500/month.
    """
    
    # 2. Run Focus Group
    group = FocusGroup("developers")
    result = await group.run_session("Landing Page Copy", landing_page_text)
    
    # 3. Print Results
    print(f"\n📊 {result['summary']}")
    print("-" * 40)
    
    for item in result['details']:
        p_name = item['persona']
        p_role = item['role']
        fb = item['feedback']
        
        print(f"\n[DEBUG] Raw Feedback for {p_name}: {fb}")
        
        print(f"\n👤 {p_name} ({p_role})")
        print(f"   Rating: {fb.get('rating')}/10")
        print(f"   Impression: \"{fb.get('first_impression')}\"")
        print(f"   ❤️ Likes: {', '.join(fb.get('likes', []))}")
        print(f"   👎 Dislikes: {', '.join(fb.get('dislikes', []))}")

if __name__ == "__main__":
    asyncio.run(run_demo())
