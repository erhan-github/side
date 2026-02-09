import os
import sys
from pathlib import Path

# Add src to PYTHONPATH if not already there (handled by Docker but good for local)
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from side.server import main

if __name__ == "__main__":
    # Ensure port is handled correctly (Railway standard)
    # The side.server:main() already handles os.getenv("PORT")
    main()
