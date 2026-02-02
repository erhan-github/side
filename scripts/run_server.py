import os
import sys
from pathlib import Path

# Add src to path for absolute imports
# FIXED: Pointing to Sidelith Prime Universal Server
src_path = str(Path(__file__).parent / "backend" / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from side.server import main

if __name__ == "__main__":
    # Local dev entrypoint
    # Set default transport to stdio for Cursor/Mac dev if not specified
    if "MCP_TRANSPORT" not in os.environ:
        os.environ["MCP_TRANSPORT"] = "stdio"
        
    main()
