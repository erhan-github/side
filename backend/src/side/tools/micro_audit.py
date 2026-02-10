"""
Micro Audit Tool.
Designed for Agent/MCP use.
Runs a specific audit probe on a specific file instantly.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[3]))

    from side.tools.audit_tool import AuditTool
    
    # Project root assumption: 3 levels up from tools/
    project_root = Path(__file__).parents[3]
    
    auditor = AuditTool(project_root)
    
    # Simple direct scan for now
    print(f"Running audit on {file_path}...")
    # AuditTool.scan_codebase expects a query, not a probe_id in this version
    # Adapting to use scan_codebase with a specific query
    result = await auditor.scan_codebase(f"Audit file {file_path} for issues related to {probe_id}")
    print(result[0]) # print report

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Execution Error: {e}")
