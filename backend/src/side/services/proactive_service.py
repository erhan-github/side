"""
Proactive IAnonymous Telemetry Service for sideMCP.deMCP.

Monitors the codebase for technical signals (HACK, TODO) that might indicate
strategic friction or vision drift.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any

from side.storage.modules.strategy import StrategyStore
from side.utils.llm_helpers import extract_json

logger = logging.getLogger(__name__)

class ProactiveService:
    """
    Monitors for 'Strategic Friction' signals in the codebase.
    Checks for TODO/HACK comments and cross-references them with active goals.
    """

    def __init__(self, strategic: StrategyStore, project_path: Path):
        self.strategic = strategic
        self.project_path = project_path

    async def check_for_friction(self) -> List[Dict[str, Any]]:
        """
        Scans for strategic friction and OSS Leverage opportunities.
        """
        findings = []
        
        # 1. Get Strategic Context from the Hub
        from side.storage.modules.base import ContextEngine
        project_id = ContextEngine.get_project_id(self.project_path)
        active_plans = self.strategic.list_plans(project_id, status="active")
        
        # 2. Scan for Technical Signals (TODO, HACK, FIXME)
        # We limit scan to source files
        extensions = {'.py', '.js', '.ts', '.tsx', '.go', '.rs', '.java'}
        excludes = {'.git', 'node_modules', '__pycache__', 'venv', 'env', 'dist', 'build'}
        
        for path in self.project_path.rglob('*'):
            if path.is_file() and path.suffix in extensions:
                # Basic exclude check
                if any(part in excludes for part in path.parts):
                    continue
                    
                try:
                    content = path.read_text(errors='ignore')
                    lines = content.splitlines()
                    for i, line in enumerate(lines):
                        if any(marker in line for marker in ["TODO", "HACK", "FIXME", "XXX"]):
                            clean_line = line.strip()[:200]
                            rel_path = str(path.relative_to(self.project_path))
                            
                            # Software 2.0 Analysis
                            judgement = await self.analyze_signal(clean_line, rel_path, i + 1)
                            
                            if judgement:
                                findings.append({
                                    "type": judgement.get("type", "risk"),
                                    "message": judgement.get("message"),
                                    "file": rel_path,
                                    "line": i + 1,
                                    "context": clean_line
                                })
                except Exception:
                    pass
                    
        return findings

    async def analyze_signal(self, comment: str, file_path: str, line_no: int) -> Dict[str, Any] | None:
        """
        [Software 2.0] Uses the LLM to judge if a technical signal is a strategic risk.
        Replaces the fragile Regex/Dictionary lookups with a Virtual CTO.
        """
        # 1. Fetch Strategic Context (The Hub)
        from side.storage.modules.base import ContextEngine
        project_id = ContextEngine.get_project_id(self.project_path)
        active_plans = self.strategic.list_plans(project_id, status="active")
        context_str = "\n".join([f"- {p['title']}" for p in active_plans])
        
        prompt = f"""
Analyze if this technical comment represents a strategic risk.
        
STRATEGIC CONTEXT (Current Goals):
{context_str}

THE FINDING:
File: {file_path}:{line_no}
Comment: "{comment}"

YOUR MISSION:
Analyze if this comment represents:
1. **Vision Drift**: Building features we didn't plan?
2. **Reinventing the Wheel**: Building something that exists as OSS?
3. **Dead End**: Implementing a pattern we explicitly rejected?
4. **Strategic Risk**: A 'HACK' in a critical path?

OUTPUT:
If minor/irrelevant, output NONE.
If it is a strategic violation, output strictly a JSON object.

Format:
{{
    "type": "drift|leverage|risk",
    "severity": "high|medium",
    "message": "A concise, technical explanation of the risk and remediation."
}}
"""
        try:
            from side.llm.client import LLMClient
            client = LLMClient()
            # We use a lower latency model if possible, or standard.
            # Temperature 0.3 for consistent but creative roasts.
            response = await client.complete_async(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are a Strategic Auditor. Be concise and technical.",
                temperature=0.3
            )
            
            if "NONE" in response.upper():
                return None
            
            return extract_json(response)
                
        except Exception as e:
            logger.warning(f"Provocateur failed: {e}")
            
        return None
