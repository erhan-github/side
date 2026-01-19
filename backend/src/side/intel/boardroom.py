import logging
import asyncio
from typing import List, Any
from pathlib import Path
from side.intel.forensic_engine import Finding
from side.audit.experts.security import SecurityExpert
from side.audit.experts.architect import ChiefArchitect
from side.audit.experts.performance import PerformanceLead
from side.audit.experts.engineer import SeniorEngineer
from side.audit.experts.sre import SREOperator
from side.audit.experts.stack import Frontender, Pythonista
from side.audit.experts.base import ExpertContext

logger = logging.getLogger(__name__)

class BoardroomOrchestrator:
    """Orchestrates specialized expert reviews for forensic findings."""
    
    def __init__(self):
        self.experts = {
            'sentinel': SecurityExpert(),
            'architect': ChiefArchitect(),
            'scaler': PerformanceLead(),
            'builder': SeniorEngineer(),
            'operator': SREOperator(),
            'frontender': Frontender(),
            'pythonista': Pythonista()
        }

    def select_candidates(self, findings: List[Finding], limit: int = 5) -> List[Finding]:
        """Select top finding candidates for expert review (Round Robin)."""
        candidates = []
        seen_files = set()
        
        buckets = {
            'sentinel': [], 'architect': [], 'scaler': [], 'builder': []
        }
        
        for f in findings:
            target = 'builder'
            if f.type in ('SECURITY_PURITY', 'SECRETS'): target = 'sentinel'
            elif f.type in ('COMPLEXITY', 'ARCH_PURITY', 'MONOLITH'): target = 'architect'
            elif f.type in ('PERFORMANCE', 'SCALABILITY', 'NOISE'): target = 'scaler'
            buckets[target].append(f)

        expert_order = ['sentinel', 'architect', 'scaler', 'builder']
        for _ in range(2):
            for expert in expert_order:
                if buckets[expert] and len(candidates) < limit:
                    # Pick highest severity finding
                    best = sorted(buckets[expert], key=lambda x: {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}[x.severity])[0]
                    if best.file not in seen_files:
                        candidates.append(best)
                        seen_files.add(best.file)
                        buckets[expert].remove(best)
        
        return candidates

    async def run_reviews(self, project_root: Path, candidates: List[Finding]) -> List[dict]:
        """Execute reviews for candidates in parallel (ASYNC for speed)."""
        # Limit to top 3 for speed (smart routing)
        top_candidates = candidates[:3]
        
        # Run all reviews in parallel
        tasks = [
            self._run_single_review(project_root, finding)
            for finding in top_candidates
        ]
        
        # Execute all at once with error handling
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and None values
        reviews = [r for r in results if r is not None and not isinstance(r, Exception)]
        
        return reviews
    
    async def _run_single_review(self, project_root: Path, finding: Finding) -> dict | None:
        """Execute a single expert review (async-safe)."""
        try:
            file_path = project_root / finding.file
            if not file_path.exists():
                return None
            
            content = file_path.read_text(encoding='utf-8', errors='replace')
            expert_key = self._get_expert_key(finding)
            expert = self.experts[expert_key]
            
            snippet = content[:2000] + ("\n... (truncated)" if len(content) > 2000 else "")
            ctx = ExpertContext(
                check_id=finding.type,
                file_path=finding.file,
                content_snippet=snippet,
                language=file_path.suffix.lstrip('.') or 'txt'
            )
            
            result = expert.review(ctx)
            if result.status != 'SKIPPED':
                return {
                    "expert": expert.NAME,
                    "role": expert.ROLE,
                    "finding": finding,
                    "verdict": result.status.value,
                    "notes": result.notes,
                    "icon": self._get_icon(expert_key)
                }
            return None
        except Exception as e:
            logger.error(f"Failed review for {finding.file}: {e}")
            return None

    def _get_expert_key(self, finding: Finding) -> str:
        if finding.type in ('SECURITY_PURITY', 'SECRETS'): return 'sentinel'
        if finding.type in ('COMPLEXITY', 'ARCH_PURITY', 'MONOLITH'): return 'architect'
        if finding.type in ('PERFORMANCE', 'SCALABILITY'): return 'scaler'
        return 'builder'

    def _get_icon(self, key: str) -> str:
        return {'sentinel': "🔒", 'architect': "🏗️", 'scaler': "⚡", 'builder': "👤"}.get(key, "👤")
