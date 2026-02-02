import os
import sys
from pathlib import Path

# Add src to path for absolute imports
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from side.server import main

if __name__ == "__main__":
    # The Sovereign entrypoint
    main()
