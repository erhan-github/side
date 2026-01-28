"""
Audit tool handler for Side.
Handles: run_audit
Implements Forensic-level audit using Software 2.0 (LLM) engine.
"""

import logging
from pathlib import Path
from typing import Any
from side.tools.forensics_tool import ForensicsTool

logger = logging.getLogger(__name__)

async def handle_run_audit(arguments: dict[str, Any]) -> str:
    """
    Run Side Forensic Audit on the codebase using LLM Forensics.
    """
    dimension = arguments.get('dimension', 'general')
    
    print(f"🛡️  Initating Forensic Scan (Dimension: {dimension})...")
    
    tool = ForensicsTool(Path("."))
    
    # Construct a prompt-engineered query
    if dimension == "security":
        query = "Identify CRITICAL security vulnerabilities (OWASP Top 10), secrets, and auth flaws."
    elif dimension == "performance":
        query = "Identify performance bottlenecks, N+1 queries, and blocking loops."
    elif dimension == "architecture":
        query = "Identify architectural violations, circular dependencies, and monolithic coupling."
    else:
        query = "Identify critical code quality issues, bugs, and security risks."
        
    report = await tool.scan_codebase(query)
    
    return report

if __name__ == "__main__":
    import asyncio
    import sys
    
    args = {}
    if len(sys.argv) > 1:
        args['dimension'] = sys.argv[1]
    
    try:
        result = asyncio.run(handle_run_audit(args))
        print("\n" + result)
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
