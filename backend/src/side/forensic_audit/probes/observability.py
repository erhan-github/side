"""
Observability Probe - Logging and monitoring audit.
"""

import re
from pathlib import Path
from typing import List
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier


class ObservabilityProbe:
    """Forensic-level observability audit probe."""
    
    id = "forensic.observability"
    name = "Observability Audit"
    tier = Tier.FAST
    dimension = "Observability"
    
    def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_structured_logging(context),
            self._check_log_levels(context),
            self._check_error_logging(context),
            self._check_metrics(context),
        ]
    
    def _check_structured_logging(self, context: ProbeContext) -> AuditResult:
        """Check for structured logging."""
        patterns = ['structlog', 'logging.config', 'jsonlog', 'json_logger']
        has_structured = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content for p in patterns):
                    has_structured = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="OBS-001",
            check_name="Structured Logging",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_structured else AuditStatus.INFO,
            severity=Severity.LOW,
            recommendation="Use structlog for JSON-formatted logs"
        )
    
    def _check_log_levels(self, context: ProbeContext) -> AuditResult:
        """Check for proper log level usage."""
        log_levels = ['debug', 'info', 'warning', 'error', 'critical']
        levels_found = set()
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            try:
                content = Path(file_path).read_text()
                for level in log_levels:
                    if f'logger.{level}' in content or f'logging.{level}' in content:
                        levels_found.add(level)
            except Exception:
                continue
        
        return AuditResult(
            check_id="OBS-002",
            check_name="Log Level Usage",
            dimension=self.dimension,
            status=AuditStatus.PASS if len(levels_found) >= 3 else AuditStatus.INFO,
            severity=Severity.LOW,
            notes=f"Log levels used: {', '.join(levels_found)}",
            recommendation="Use appropriate log levels (debug < info < warning < error)"
        )
    
    def _check_error_logging(self, context: ProbeContext) -> AuditResult:
        """Check for error logging in exception handlers."""
        evidence = []
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            try:
                content = Path(file_path).read_text()
                lines = content.splitlines()
                
                for i, line in enumerate(lines):
                    if 'except' in line and ':' in line:
                        # Check next 5 lines for logging
                        next_lines = lines[i:i+5]
                        has_logging = any('log' in nl.lower() for nl in next_lines)
                        if not has_logging and 'pass' in ''.join(next_lines):
                            evidence.append(AuditEvidence(
                                description="Exception caught but not logged",
                                file_path=file_path,
                                line_number=i + 1
                            ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="OBS-003",
            check_name="Error Logging",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence[:10],
            recommendation="Log all caught exceptions"
        )
    
    def _check_metrics(self, context: ProbeContext) -> AuditResult:
        """Check for metrics/monitoring."""
        patterns = ['prometheus', 'statsd', 'metrics', 'datadog', 'opentelemetry']
        has_metrics = False
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(p in content.lower() for p in patterns):
                    has_metrics = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="OBS-004",
            check_name="Metrics Collection",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_metrics else AuditStatus.INFO,
            severity=Severity.LOW,
            recommendation="Add Prometheus or similar for metrics"
        )
