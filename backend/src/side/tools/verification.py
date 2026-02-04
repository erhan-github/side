
from typing import Any, Dict
import time
from dataclasses import dataclass
from side.tools.forensics_tool import ForensicsTool
from side.qa.generator import TestGenerator
from pathlib import Path

@dataclass
class ToolResult:
    content: str
    metadata: Dict[str, Any]

class VerificationTool:
    """
    Tool to verify if a specific finding has been fixed.
    """
    async def run(self, args: Dict[str, Any]) -> ToolResult:
        finding_type = args.get("finding_type")
        file_path = args.get("file_path")
        
        finding_type = args.get("finding_type")
        file_path = args.get("file_path")
        
        # 1. Run targeted scan using ForensicsTool (LLM-based)
        tool = ForensicsTool(Path("."))
        query = f"Check specifically for '{finding_type}' issues in {file_path or 'the codebase'}."
        
        report = await tool.scan_codebase(query)
        
        # 2. Heuristic check of the report
        if "No issues found" in report or "Clean" in report:
             return ToolResult(
                content=f"✅ VERIFICATION PASSED: Report indicates fix.\n\n{report}",
                metadata={"status": "pass"}
            )
        else:
            return ToolResult(
                content=f"❌ VERIFICATION FAILED: Report indicates remaining issues.\n\n{report}",
                metadata={"status": "fail"}
            )

            )
