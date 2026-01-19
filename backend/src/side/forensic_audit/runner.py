"""
Forensic Audit Runner - Orchestrates all probes.

Runs all probes, aggregates results, generates reports.
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timezone
import json

from .core import (
    AuditResult, AuditStatus, AuditSummary, 
    ProbeContext, Severity
)
from .probes import (
    SecurityProbe,
    PerformanceProbe,
    CodeQualityProbe,
    DatabaseProbe,
    APIDesignProbe,
    TestingProbe,
    DevOpsProbe,
    DependencyProbe,
    CostProbe,
    ObservabilityProbe,
    ComplianceProbe,
    LLMQualityProbe,
    InfrastructureProbe,
    FrontendProbe,
    CrawlerProbe,
    ReadinessProbe
)


class ForensicAuditRunner:
    """
    Forensic-level audit orchestrator.
    
    Runs all 14 dimension probes (80+ checks total).
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        
        # Initialize all probes
        self.probes = [
            SecurityProbe(),
            PerformanceProbe(),
            CodeQualityProbe(),
            DatabaseProbe(),
            APIDesignProbe(),
            TestingProbe(),
            DevOpsProbe(),
            DependencyProbe(),
            CostProbe(),
            ObservabilityProbe(),
            ComplianceProbe(),
            LLMQualityProbe(),
            InfrastructureProbe(),
            FrontendProbe(),
            CrawlerProbe(),
            ReadinessProbe()
        ]
    
    def run_dimension(self, dimension_name: str) -> Optional[AuditSummary]:
        """Run only probes for a specific dimension."""
        context = self._create_context()
        target_dim = dimension_name.lower()
        
        selected_probes = [p for p in self.probes if getattr(p, 'dimension', '').lower() == target_dim]
        
        if not selected_probes:
            return None
            
        return self._run_probes(selected_probes, context)

    def run(self) -> AuditSummary:
        """Run all probes and generate summary."""
        context = self._create_context()
        return self._run_probes(self.probes, context)
    
    def _run_probes(self, probes: list, context: ProbeContext) -> AuditSummary:
        """Run probes and aggregate results."""
        all_results: List[AuditResult] = []
        results_by_dimension: Dict[str, List[AuditResult]] = {}
        
        for probe in probes:
            try:
                probe_results = probe.run(context)
                all_results.extend(probe_results)
                
                dimension = getattr(probe, 'dimension', 'Unknown')
                if dimension not in results_by_dimension:
                    results_by_dimension[dimension] = []
                results_by_dimension[dimension].extend(probe_results)
            except Exception as e:
                print(f"Error running {probe.name}: {e}")
        
        # Calculate summary
        total = len(all_results)
        passed = sum(1 for r in all_results if r.status == AuditStatus.PASS)
        failed = sum(1 for r in all_results if r.status == AuditStatus.FAIL)
        warnings = sum(1 for r in all_results if r.status == AuditStatus.WARN)
        skipped = sum(1 for r in all_results if r.status == AuditStatus.SKIP)
        
        score = (passed / total * 100) if total > 0 else 0
        critical = sum(1 for r in all_results if r.status == AuditStatus.FAIL and r.severity == Severity.CRITICAL)
        high = sum(1 for r in all_results if r.status == AuditStatus.FAIL and r.severity == Severity.HIGH)
        
        return AuditSummary(
            total_checks=total,
            passed=passed,
            failed=failed,
            warnings=warnings,
            skipped=skipped,
            score_percentage=round(score, 1),
            critical_findings=critical,
            high_findings=high,
            results_by_dimension=results_by_dimension,
            timestamp=datetime.now(timezone.utc)
        )
    
    def run_and_report(self, output_format: str = "markdown") -> str:
        """
        Run audit and generate report.
        
        Args:
            output_format: 'markdown' or 'json'
            
        Returns:
            Formatted report string
        """
        summary = self.run()
        
        if output_format == "json":
            return self._generate_json_report(summary)
        else:
            return self._generate_markdown_report(summary)
    
    def _create_context(self) -> ProbeContext:
        """Create probe context with all files."""
        files = []
        ignored_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build', '.next'}
        
        for p in self.project_root.rglob("*"):
            if p.is_file():
                if not any(part in ignored_dirs for part in p.parts):
                    files.append(str(p))
        
        return ProbeContext(
            project_root=str(self.project_root),
            files=files
        )
    
    def _generate_markdown_report(self, summary: AuditSummary) -> str:
        """Generate markdown report."""
        lines = [
            "# 🛡️ Side Forensic Audit Report",
            f"**Run Date**: {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC",
            f"**Project**: {self.project_root}",
            "",
            "---",
            "",
            "## 📊 Executive Summary",
            "",
            f"| Metric | Value |",
            f"| :--- | :---: |",
            f"| **Score** | **{summary.score_percentage}%** ({summary.grade}) |",
            f"| Total Checks | {summary.total_checks} |",
            f"| Passed | ✅ {summary.passed} |",
            f"| Failed | ❌ {summary.failed} |",
            f"| Warnings | ⚠️ {summary.warnings} |",
            f"| Critical Findings | 🔴 {summary.critical_findings} |",
            f"| High Findings | 🟠 {summary.high_findings} |",
            "",
            "---",
            "",
            "## 📈 Score by Dimension",
            "",
            "| Dimension | Checks | Passed | Score |",
            "| :--- | :---: | :---: | :---: |",
        ]
        
        for dimension, results in summary.results_by_dimension.items():
            total = len(results)
            passed = sum(1 for r in results if r.status == AuditStatus.PASS)
            score = (passed / total * 100) if total > 0 else 0
            lines.append(f"| {dimension} | {total} | {passed} | {score:.0f}% |")
        
        lines.extend([
            "",
            "---",
            "",
            "## ❌ Failed Checks",
            "",
        ])
        
        for dimension, results in summary.results_by_dimension.items():
            failed = [r for r in results if r.status == AuditStatus.FAIL]
            if failed:
                lines.append(f"### {dimension}")
                for r in failed:
                    severity_emoji = "🔴" if r.severity == Severity.CRITICAL else "🟠" if r.severity == Severity.HIGH else "🟡"
                    lines.append(f"- {severity_emoji} **{r.check_id}**: {r.check_name}")
                    if r.recommendation:
                        lines.append(f"  - Recommendation: {r.recommendation}")
                lines.append("")
        
        lines.extend([
            "---",
            "",
            "## ⚠️ Warnings",
            "",
        ])
        
        for dimension, results in summary.results_by_dimension.items():
            warnings = [r for r in results if r.status == AuditStatus.WARN]
            if warnings:
                lines.append(f"### {dimension}")
                for r in warnings:
                    lines.append(f"- ⚠️ **{r.check_id}**: {r.check_name}")
                    if r.notes:
                        lines.append(f"  - {r.notes}")
                lines.append("")
        
        lines.extend([
            "---",
            "",
            f"*Generated by Side Forensic Engine // {summary.timestamp.strftime('%Y-%m-%d')}*"
        ])
        
        return "\n".join(lines)
    
    def _generate_json_report(self, summary: AuditSummary) -> str:
        """Generate JSON report."""
        data = {
            "timestamp": summary.timestamp.isoformat(),
            "project_root": str(self.project_root),
            "summary": {
                "total_checks": summary.total_checks,
                "passed": summary.passed,
                "failed": summary.failed,
                "warnings": summary.warnings,
                "skipped": summary.skipped,
                "score_percentage": summary.score_percentage,
                "grade": summary.grade,
                "critical_findings": summary.critical_findings,
                "high_findings": summary.high_findings
            },
            "results_by_dimension": {
                dim: [r.to_dict() for r in results]
                for dim, results in summary.results_by_dimension.items()
            }
        }
        return json.dumps(data, indent=2)
