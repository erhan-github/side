
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

    async def generate_repro(self, args: Dict[str, Any]) -> ToolResult:
        """
        Generate a reproduction test case for a specific finding.
        """
        finding_id = args.get("finding_id")
        
        # 1. Look up the finding details
        # Since we don't have a FindingStore yet, we'll re-scan and fuzzy match
        # OR accept full finding details in args.
        # For V1, let's assume the agent passes the finding object structure or we quick scan.
        
        # Simpler V1: Agent passes the finding as a dict because it just saw it.
        finding = args.get("finding")
        if not finding:
            return ToolResult("❌ Error: No finding detail provided.", {})
            
        generator = TestGenerator(Path("."))
        repro_code = await generator.generate_repro(finding)
        
        # Save to file
        repro_path = Path("tests/repro")
        repro_path.mkdir(parents=True, exist_ok=True)
        
        check_name = finding.get("check_name", "issue").lower().replace(" ", "_")
        filename = f"test_repro_{check_name}_{int(time.time())}.py"
        file_path = repro_path / filename
        file_path.write_text(repro_code)
        
        return ToolResult(
            content=f"✅ Red Test Generated: {file_path}\n\nRun with: `pytest {file_path}`",
            metadata={"file_path": str(file_path), "code": repro_code}
        )
