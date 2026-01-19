"""
Cost Probe - Cost efficiency audit.
"""

import re
from pathlib import Path
from typing import List
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier


class CostProbe:
    """Forensic-level cost audit probe."""
    
    id = "forensic.cost"
    name = "Cost Audit"
    tier = Tier.FAST
    dimension = "Cost & Efficiency"
    
    def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_cost_tracking(context),
            self._check_caching(context),
            self._check_token_limits(context),
        ]
    
    def _check_cost_tracking(self, context: ProbeContext) -> AuditResult:
        """Check for cost tracking."""
        patterns = ['cost_tokens', 'token_cost', 'log_activity', 'usage_tracking']
        has_tracking = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns):
                    has_tracking = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="COST-001",
            check_name="Cost Tracking",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_tracking else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Track costs per feature for optimization"
        )
    
    def _check_caching(self, context: ProbeContext) -> AuditResult:
        """Check for caching to reduce costs."""
        patterns = ['@cache', '@lru_cache', 'cache_key', 'get_cached', 'InsightCache']
        has_caching = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns):
                    has_caching = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="COST-002",
            check_name="Caching Strategy",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_caching else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            recommendation="Cache expensive operations (LLM calls, API requests)"
        )
    
    def _check_token_limits(self, context: ProbeContext) -> AuditResult:
        """Check for token limit handling."""
        patterns = ['max_tokens', 'token_limit', 'token_budget', 'truncate']
        has_limits = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns):
                    has_limits = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="COST-003",
            check_name="Token Limits",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_limits else AuditStatus.WARN,
            severity=Severity.HIGH,
            recommendation="Set max_tokens to prevent runaway costs"
        )
