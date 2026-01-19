#!/usr/bin/env python3
import sys
import argparse
import asyncio
from pathlib import Path

# Add backend/src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from side.sim.session import FocusGroup
from side.server import load_env_file

async def run_sim(audience: str, content_file: str):
    print(f"🚀 Starting Virtual Focus Group ({audience})...")
    load_env_file()
    
    # Read content
    if content_file:
        try:
            content = Path(content_file).read_text()
            print(f"📖 Loaded content from {content_file} ({len(content)} chars)")
        except Exception as e:
            print(f"❌ Failed to read file: {e}")
            return
    else:
        print("❌ Please provide a file to review (e.g. README.md)")
        return

    # Run Session
    group = FocusGroup(audience)
    result = await group.run_session(f"File: {content_file}", content)
    
    # Print formatted output
    print(f"\n📊 Focus Group Score: {result['average_score']}/10")
    print("-" * 50)
    
    for item in result['details']:
        p_name = item['persona']
        p_role = item['role']
        fb = item['feedback']
        
        print(f"\n👤 {p_name} ({p_role})")
        print(f"   Rating: {fb.get('rating')}/10")
        print(f"   Impression: \"{fb.get('first_impression')}\"")
        if fb.get("likes"):
            print(f"   ❤️ Likes: {', '.join(fb.get('likes', []))}")
        if fb.get("dislikes"):
            print(f"   👎 Dislikes: {', '.join(fb.get('dislikes', []))}")

def main():
    parser = argparse.ArgumentParser(description="Run a Virtual Focus Group")
    parser.add_argument("audience", choices=["teachers", "developers", "general"], help="Target Audience")
    parser.add_argument("file", help="Path to file to review")
    
    args = parser.parse_args()
    
    asyncio.run(run_sim(args.audience, args.file))

if __name__ == "__main__":
    main()
