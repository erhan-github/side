"""
Proactive Telemetry Service for sideMCP.

Monitors the codebase for technical signals (HACK, TODO) that might indicate
strategic friction or objective drift.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any

from side.storage.modules.strategy import DecisionStore
from side.utils.llm_helpers import extract_json
from side.prompts import Personas, StrategicFrictionPrompt, LLMConfigs

logger = logging.getLogger(__name__)

class BackgroundService:
    """
    Monitors for 'Strategic Friction' signals in the codebase.
    Checks for TODO/HACK comments and cross-references them with active goals.
    """

    def __init__(self, plans: DecisionStore, project_path: Path):
        self.plans = plans
        self.project_path = project_path
        self.config = LLMConfigs.get_config("strategic_auditor")

    async def check_for_friction(self) -> List[Dict[str, Any]]:
        """
        Scans for strategic friction and OSS Leverage opportunities.
        """
        findings = []
        
        # 1. Get Strategic Context
        from side.storage.modules.base import ContextEngine
        project_id = ContextEngine.get_project_id(self.project_path)
        active_plans = self.plans.list_plans(project_id, status="active")
        
        # 2. Scan for Technical Signals (TODO, HACK, FIXME)
        extensions = {'.py', '.js', '.ts', '.tsx', '.go', '.rs', '.java'}
        excludes = {'.git', 'node_modules', '__pycache__', 'venv', 'env', 'dist', 'build'}
        
        for path in self.project_path.rglob('*'):
            if path.is_file() and path.suffix in extensions:
                if any(part in excludes for part in path.parts):
                    continue
                    
                try:
                    content = path.read_text(errors='ignore')
                    lines = content.splitlines()
                    for i, line in enumerate(lines):
                        if any(marker in line for marker in ["TODO", "HACK", "FIXME", "XXX"]):
                            clean_line = line.strip()[:200]
                            rel_path = str(path.relative_to(self.project_path))
                            
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
        Uses the LLM to judge if a technical signal is a strategic risk.
        """
        from side.storage.modules.base import ContextEngine
        project_id = ContextEngine.get_project_id(self.project_path)
        active_plans = self.plans.list_plans(project_id, status="active")
        context_str = "\n".join([f"- {p['title']}" for p in active_plans])
        
        prompt = StrategicFrictionPrompt.format(
            context_str=context_str,
            file_path=file_path,
            line_no=line_no,
            comment=comment
        )
        try:
            from side.llm.client import LLMClient
            client = LLMClient()
            response = await client.complete_async(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=Personas.STRATEGIC_AUDITOR,
                **self.config
            )
            
            if "NONE" in response.upper():
                return None
            
            return extract_json(response)
                
        except Exception as e:
            logger.warning(f"Background analysis failed: {e}")
            
        return None
