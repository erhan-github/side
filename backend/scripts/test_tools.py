#!/usr/bin/env python3
"""
CSO.ai Tool Tester - Test tools without restarting Cursor.

Usage:
    python scripts/test_tools.py ping
    python scripts/test_tools.py analyze_codebase --path /path/to/project
    python scripts/test_tools.py whats_new
    python scripts/test_tools.py ask_strategy --question "What should we focus on?"
    python scripts/test_tools.py stats
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("'\"")
                if key and value:
                    os.environ[key] = value
    print(f"✅ Loaded .env from {env_path}\n")


async def main():
    from side.tools import handle_tool_call

    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable tools:")
        print("  - ping")
        print("  - analyze_codebase [--path PATH]")
        print("  - show_profile")
        print("  - whats_new [--days N]")
        print("  - business_insights [--days N]")
        print("  - analyze_url --url URL")
        print("  - explore --topic TOPIC")
        print("  - ask_strategy --question QUESTION")
        print("  - refresh")
        print("  - stats")
        return

    tool_name = sys.argv[1]
    args = {}

    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i].startswith("--"):
            key = sys.argv[i][2:]
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--"):
                args[key] = sys.argv[i + 1]
                i += 2
            else:
                args[key] = True
                i += 1
        else:
            i += 1

    print(f"🧠 CSO.ai Tool Tester")
    print(f"{'─' * 50}")
    print(f"Tool: {tool_name}")
    print(f"Args: {args}")
    print(f"{'─' * 50}\n")

    try:
        result = await handle_tool_call(tool_name, args)
        print(result)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
