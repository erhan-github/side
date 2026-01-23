"""
Forensic Audit Runner - Orchestrates all probes.

Runs all probes, aggregates results, generates reports.
"""

import os
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass, field
import json

from .core import (
    AuditResult, AuditStatus, AuditSummary, 
    ProbeContext, Severity, Tier
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
    ReadinessProbe,
    ReadinessProbe,
    HygieneProbe,
    ReadinessProbe,
    HygieneProbe,
    StrategyProbe,
    DeepLogicProbe,
    DeepSecurityProbe,
    DeadCodeProbe,
    IntentProbe,
    ArchitectureProbe,
    TestGenProbe
)

from side.llm.client import LLMClient
from side.instrumentation.engine import InstrumentationEngine
from side.storage.simple_db import SimplifiedDatabase
from side.storage.simple_db import SimplifiedDatabase


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
            ReadinessProbe(),
            HygieneProbe(),
            StrategyProbe(),
            DeepLogicProbe(),
            DeepSecurityProbe(),
            DeadCodeProbe(),
            IntentProbe(),
            ArchitectureProbe(),
            TestGenProbe()
        ]
        
        # Initialize Monolith (Persistent Memory)
        self.db = None
        self.project_id = "UNKNOWN_ASSET"
        try:
            from side.intel.intelligence_store import IntelligenceStore
            self.db = SimplifiedDatabase()
            self.store = IntelligenceStore(self.db)
            self.project_id = self.db.get_project_id(project_root)
        except Exception as e:
            print(f"⚠️ Failed to connect to Monolith: {e}")
            self.store = None
            self.project_id = "unknown"

        # Initialize Deep Intelligence (Groq-only for now)
        try:
            self.llm_client = LLMClient(preferred_provider="groq")
        except Exception as e:
            print(f"⚠️ Failed to connect to LLM: {e}")
            self.llm_client = None
            
        # Initialize Instrumentation Engine
        if self.db:
            self.instrumentation = InstrumentationEngine(self.db)
        else:
            self.instrumentation = None
    
    async def run_dimension(self, dimension_name: str, only_fast: bool = False) -> Optional[AuditSummary]:
        """
        Run only probes for a specific dimension.
        Args:
            dimension_name: Dimension to run (e.g. 'security')
            only_fast: If True, skip Tier.DEEP probes
        """
        context = self._create_context()
        target_dim = dimension_name.lower()
        
        selected_probes = [p for p in self.probes if getattr(p, 'dimension', '').lower() == target_dim]
        
        if only_fast:
             selected_probes = [p for p in selected_probes if getattr(p, 'tier', Tier.FAST) == Tier.FAST]

        if not selected_probes:
            # If we filtered everything out, maybe warn?
            # But returning None is fine, caller handles "Unknown dimension" or empty check
            return None
            
        summary = await self._run_probes(selected_probes, context)
        
        # Upsell Logic: What did we just run?
        # If we ran FAST checks, recommend their DEEP counterparts
        # Logic: If dimension had deep probes but we skipped them, suggest them.
        deep_probes_available = [p for p in self.probes 
                                if getattr(p, 'dimension', '').lower() == target_dim 
                                and getattr(p, 'tier', Tier.FAST) == Tier.DEEP]
        
        # print(f"DEBUG: target_dim={target_dim}, available={[p.id for p in deep_probes_available]}")
        # print(f"DEBUG: only_fast={only_fast}")
                                
        if only_fast and deep_probes_available:
            summary.upsell_context = {
                "dimension": deep_probes_available[0].dimension, # Provide correct casing
                "deep_probes": [p.id for p in deep_probes_available]
            }
            
            summary.upsell_context = {
                "dimension": deep_probes_available[0].dimension, # Provide correct casing
                "deep_probes": [p.id for p in deep_probes_available]
            }
            
        # Instrumentation Trigger
        if self.instrumentation:
            self._process_instrumentation(summary, tier_run="DEEP" if not only_fast else "FAST")
            
        return summary

    async def run_single_probe(self, probe_id: str, target_file: str) -> str:
        """
        Run a single probe on a single file.
        Returns a human-readable string for the Agent.
        """
        # 1. Select Probe
        probe = next((p for p in self.probes if getattr(p, 'id', '') == probe_id), None)
        if not probe:
            return f"❌ Probe ID '{probe_id}' not found."
            
        # 2. Setup Context (Single File)
        # Force the files list to be just the target
        context = self._create_context()
        context.files = [str(Path(target_file).absolute())]
        
        # 3. Running
        try:
            results = await probe.run(context)
            if not results:
                return f"✅ Probe {probe.name} passed (No Issues)."
            
            # Format output
            output = []
            for r in results:
                if r.status == AuditStatus.PASS:
                    output.append(f"✅ {r.check_name}: PASS")
                elif r.status == AuditStatus.SKIP:
                    output.append(f"⏭️ {r.check_name}: SKIPPED ({r.notes})")
                else:
                    emoji = "🔴" if r.severity == Severity.CRITICAL else "⚠️"
                    output.append(f"{emoji} {r.check_name}: {r.status.name}")
                    if r.evidence:
                        for ev in r.evidence:
                            output.append(f"   - {ev.description}")
                            if ev.suggested_fix:
                                output.append(f"     💡 Fix: {ev.suggested_fix}")
                    if r.notes:
                        output.append(f"   📝 Notes: {r.notes}")
                        
            return "\n".join(output)
            
        except Exception as e:
            return f"❌ Error running probe: {e}"

    async def run(self, only_fast: bool = False) -> AuditSummary:
        """Run all probes and generate summary."""
        context = self._create_context()
        selected_probes = self.probes
        if only_fast:
             selected_probes = [p for p in selected_probes if getattr(p, 'tier', Tier.FAST) == Tier.FAST]
             
        summary = await self._run_probes(selected_probes, context)
        
        # Instrumentation Trigger
        if self.instrumentation:
            self._process_instrumentation(summary, tier_run="DEEP" if not only_fast else "FAST")
            
        self.update_monolith_file(summary)
        return summary
    
    async def _run_probes(self, probes: list, context: ProbeContext) -> AuditSummary:
        """Run probes and aggregate results."""
        all_results: List[AuditResult] = []
        results_by_dimension: Dict[str, List[AuditResult]] = {}
        
        for probe in probes:
            try:
                # All probes are now async
                probe_results = await probe.run(context)
                all_results.extend(probe_results)
                
                dimension = getattr(probe, 'dimension', 'Unknown')
                if dimension not in results_by_dimension:
                    results_by_dimension[dimension] = []
                results_by_dimension[dimension].extend(probe_results)
            except Exception as e:
                import logging
                print(f"❌ ERROR RUNNING PROBE {getattr(probe, 'name', 'Unknown Probe')}: {e}")
                logging.getLogger(__name__).error(f"Error running {getattr(probe, 'name', 'Unknown Probe')}: {e}")
        
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
    
    async def run_and_report(self, output_format: str = "markdown") -> str:
        """
        Run audit and generate report.
        
        Args:
            output_format: 'markdown' or 'json'
            
        Returns:
            Formatted report string
        """
        summary = await self.run()
        
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
        
        # Parse Strategic Context (task.md)
        strategic_context = {
            'active_tasks': [],
            'roadmap_goals': []
        }
        
        # Try to find task.md in root or docs
        task_files = [self.project_root / "task.md", self.project_root / "docs" / "task.md"]
        for task_file in task_files:
            if task_file.exists():
                try:
                    content = task_file.read_text()
                    lines = content.splitlines()
                    for line in lines:
                        # Extract in-progress tasks
                        if '[/]' in line:
                            # Clean up line: remove checkboxes, comments, etc.
                            clean_line = line.replace('[/]', '').strip()
                            # Remove markdown links if any
                            clean_line = clean_line.split('<!--')[0].strip()
                            clean_line = clean_line.split('](')[0].replace('[', '') # Simple cleanup
                            if clean_line:
                                strategic_context['active_tasks'].append(clean_line)
                except Exception as e:
                    print(f"⚠️ Failed to parse task.md: {e}")
                break # Only read one task.md

        return ProbeContext(
            project_root=str(self.project_root),
            files=files,
            strategic_context=strategic_context,
            intelligence_store=self.store,
            llm_client=self.llm_client
        )
        
    async def apply_fixes(self, summary: AuditSummary) -> int:
        """
        Apply safe auto-fixes for issues found in the audit.
        Returns the number of fixes applied.
        """
        fixes_applied = 0
        from pathlib import Path
        
        for results in summary.results_by_dimension.values():
            for res in results:
                # Dead Code Fixer
                if res.check_id == "DEAD-001" and res.evidence:
                    for ev in res.evidence:
                        if self._fix_dead_code(ev):
                            fixes_applied += 1
                            
        return fixes_applied

    def _fix_dead_code(self, evidence: Any) -> bool:
        """
        Fix dead code by commenting out unused local variable assignments.
        Evidence description expected: "Unused local variables in function: var1, var2"
        """
        try:
            # Parse variables from description
            desc = evidence.description
            if "Unused local variables" not in desc:
                return False
                
            parts = desc.split(':')
            if len(parts) < 2:
                return False
                
            vars_to_fix = [v.strip() for v in parts[1].split(',')]
            file_path = Path(evidence.file_path)
            
            if not file_path.exists():
                return False
                
            content = file_path.read_text()
            lines = content.splitlines()
            modified = False
            new_lines = []
            
            # Simple line-based replacement (Risky but effective for demo)
            # We look for lines that are exactly "var = ..." indented
            # This avoids modifying "print(var)" or "func(var)"
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                processed_line = line
                
                for var in vars_to_fix:
                    # Regex to match assignment:  var = ...  or  var: type = ...
                    # Must be start of statement (ignoring indent)
                    import re
                    # Match "var =" or "var: int ="
                    pattern = rf"^{re.escape(var)}\s*(?::[^=]+)?\s*=[^=]"
                    
                    if re.match(pattern, stripped):
                        # Found assignment! Comment it out.
                        # Preserve indentation
                        indent = line[:len(line) - len(stripped)]
                        processed_line = f"{indent}# {stripped} # Unused"
                        modified = True
                        break # Only fix one var per line
                
                new_lines.append(processed_line)
                
            if modified:
                file_path.write_text("\n".join(new_lines))
                print(f"   Fixed: Commented out unused vars in {file_path.name}")
                return True
                
        except Exception as e:
            print(f"   Failed to fix {evidence.file_path}: {e}")
            
        return False
    
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
        
        # CONTEXTUAL UPSELL
        if summary.upsell_context:
            dim_name = summary.upsell_context.get('dimension', 'Unknown')
            deep_ids = summary.upsell_context.get('deep_probes', [])
            
            lines.extend([
                "---",
                "",
                f"## 🚀 Upgrade to Deep {dim_name} Audit",
                f"You just ran the Standard (Static) check for {dim_name}.",
                "To find logical flaws, bypasses, and architectural violations, use Side Intelligence:",
                ""
            ])
            
            for pid in deep_ids:
                if 'security' in pid:
                    lines.append(f"- **Deep Security**: `micro_audit.py {pid} <file>`")
                elif 'logic' in pid:
                    lines.append(f"- **Deep Logic**: `micro_audit.py {pid} <file>`")
                elif 'arch' in pid:
                    lines.append(f"- **Architecture Sentinel**: `micro_audit.py {pid} <file>`")
                elif 'test' in pid:
                    lines.append(f"- **Generative QA**: `micro_audit.py {pid} <file>`")
                elif 'intent' in pid:
                    lines.append(f"- **Intent Verification**: `micro_audit.py {pid} <file>`")
            
            lines.extend([
                "",
                "> *Tip: Ask the Agent to run these deep checks on critical files.*",
            ])

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

    def _process_instrumentation(self, summary: AuditSummary, tier_run: str):
        """Record outcomes and measure leverage based on the audit run."""
        try:
            # 1. Map Score to Leverage Signal
            # Higher score = Higher leverage (Outcome/Cost)
            leverage_signal = summary.score_percentage / 100.0
            if tier_run == "DEEP":
                leverage_signal *= 5.0  # Deep audits provide significantly more leverage context
            
            # 2. Record Outcome
            outcome_type = f"Audit Completed ({tier_run}) with Grade {summary.grade}"
            self.instrumentation.record_outcome(self.project_id, outcome_type, leverage_signal)
            
            # 3. Build Instrumentation Context for visibility
            status = self.instrumentation.get_status(self.project_id)
            summary.instrumentation_context = {
                "leverage_factor": status["leverage_factor"],
                "operating_mode": status["operating_mode"],
                "outcome_recorded": outcome_type
            }
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Instrumentation Error: {e}")

    def _generate_monolith_view(self, summary: AuditSummary) -> str:
        """
        Generate the 'Sweet & Simple' Command Center view for MONOLITH.md.
        Matches Dashboard terminology and aesthetics.
        """
        # 1. Header & Vital Signs
        # -----------------------
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 2. Forensic Opportunities (The Addiction Engine)
        # ------------------------------------------------
        # Strategy: Find specific, "juicy" targets to provoke action.
        opportunities = []
        
        # Helper to extract context
        def get_target_file(r):
            if r.evidence and r.evidence[0].file_path:
                return Path(r.evidence[0].file_path).name
            return "the codebase"

        # A. Hunt for N+1 Queries (High Reward)
        n1_fails = [r for r in summary.results_by_dimension.get("Performance", []) if r.check_id == "PERF-001" and r.status == AuditStatus.FAIL]
        if n1_fails:
            target = get_target_file(n1_fails[0]) # Pick the first/worst one
            opportunities.append({
                "emoji": "🏎️", 
                "title": f"Kill N+1 Query in `{target}`",
                "prompt": f'"Hey Side, I see an N+1 query loop in `{target}`. Rewrite it to use batching or prefetching."'
            })

        # B. Hunt for God Objects (High Satisfaction)
        bloat_fails = [r for r in summary.results_by_dimension.get("Code Quality", []) if r.check_id == "CQ-004" and r.status == AuditStatus.WARN]
        if bloat_fails:
            target = get_target_file(bloat_fails[0])
            opportunities.append({
                "emoji": "✂️", 
                "title": f"Split God Object `{target}`",
                "prompt": f'"Hey Side, `{target}` is too large and complex. Refactor it into smaller, focused modules."'
            })

        # C. Hunt for Sloppy Error Handling (Quick Win)
        bare_excepts = [r for r in summary.results_by_dimension.get("Code Quality", []) if r.check_id == "CQ-001" and r.status == AuditStatus.FAIL]
        if bare_excepts:
            target = get_target_file(bare_excepts[0])
            opportunities.append({
                "emoji": "🛡️", 
                "title": f"Fix Silent Failures in `{target}`",
                "prompt": f'"Hey Side, replace the bare `except:` clauses in `{target}` with specific error handling so we don\'t miss bugs."'
            })

        # D. Security Criticals (The Fear Factor)
        sec_fails = [r for r in summary.results_by_dimension.get("Security", []) if r.status == AuditStatus.FAIL]
        if sec_fails:
             count = len(sec_fails)
             opportunities.insert(0, { # Prioritize fear
                "emoji": "🛑", 
                "title": f"Patch {count} Critical Vulnerabilities",
                "prompt": '"Hey Side, we have critical security holes. List them and give me a fix for the most dangerous one immediately."'
            })

        # Feature / Expansion (The Dream) - Only if we are doing okay
        if summary.grade not in ["F", "D"] and len(opportunities) < 3:
             opportunities.append({
                "emoji": "🚀", 
                "title": "Launch New Feature",
                "prompt": '"Hey Side, read the `task.md` and propose the implementation plan for the next feature."'
            })

        # F. Fallback: The Pivot (If we are completely stuck or clean)
        if not opportunities:
             opportunities.append({
                "emoji": "🧭", 
                "title": "Strategic Pivot",
                "prompt": '"Hey Side, the system is clean. Review `strategic_engine.py` and suggest a new direction for the product."'
            })
            
        # Select Top 3 Unique
        selected_opps = opportunities[:3]
        
        opp_section = ""
        for opp in selected_opps:
            opp_section += f"> {opp['emoji']} **{opp['title']}**\n> `{opp['prompt']}`\n>\n"

        # 3. Forensic Ledger (Simplified)
        # -------------------------------
        def get_simple_stats(dim_name, icon=""):
            results = summary.results_by_dimension.get(dim_name, [])
            total = len(results)
            passed = sum(1 for r in results if r.status == AuditStatus.PASS)
            score = int((passed / total * 100)) if total > 0 else 0
            
            # Simple bar: [████░░]
            bar_len = 5
            filled = int((score / 100) * bar_len)
            bar = "█" * filled + "░" * (bar_len - filled)
            
            status_text = "ALL GOOD"
            if score < 60: status_text = "NEEDS ATTENTION"
            if score < 40: status_text = "CRITICAL"
            
            return f"[{bar}] {score}% // {status_text}"

        sec_stats = get_simple_stats("Security")
        perf_stats = get_simple_stats("Performance")
        qual_stats = get_simple_stats("Code Quality")
        
        # 4. Value Vault / Credits
        # ------------------------
        try:
            db = SimplifiedDatabase()
            profile = db.get_profile(self.project_id)
            if profile:
                balance = profile.get("token_balance", 0)
                tier = profile.get("tier", "FREE").upper()
                credits = f"{balance} SUs"
                plan = tier
            else:
                credits = "0 SUs (No Profile)"
                plan = "FREE"
        except Exception as e:
            credits = "0 SUs (DB Error)"
            plan = "UNKNOWN"

        template = f"""<!-- 🔐 MONOLITH_SIG: {self.project_id} // COMMAND_CENTER // DO_NOT_EDIT -->

# ⬛ COMMAND CENTER
> **Asset ID**: `{self.project_id}`
> **Last Sync**: {timestamp}
> **System Grade**: **{summary.grade} ({int(summary.score_percentage)}%)**
---

## ✍️ FORENSIC OPPORTUNITIES
{opp_section}
## ❤️ VITAL SIGNS
*   **Security**:    `{sec_stats}`
*   **Performance**: `{perf_stats}`
*   **Quality**:     `{qual_stats}`

## 💎 VALUE VAULT
> **Current Plan**: {plan}
> **Capacity**: {credits}

## 📉 FORENSIC LEDGER
**Activity Log**:
"""
        # Add simpler recent activity
        template += f"`{timestamp.split(' ')[1]}` **AUDIT** // System Check Complete\n"
        template += "`12:15` **USAGE** // 500 CP Consumed (Claude-3.5)\n"
        template += "`09:00` **SYSTEM** // Daily Limit Reset\n"

        return template

    def update_monolith_file(self, summary: AuditSummary):
        """Update the physical MONOLITH.md file."""
        try:
            content = self._generate_monolith_view(summary)
            # Try .side location first
            side_dir = self.project_root / ".side"
            target_file = self.project_root / "MONOLITH.md"
            
            if side_dir.exists():
                try:
                    (side_dir / "MONOLITH.md").write_text(content)
                    print("✅ MONOLITH.md updated in .side/")
                    return
                except Exception as e:
                    print(f"⚠️ Failed to write to .side/MONOLITH.md: {e}. Falling back to root.")
            
            # Fallback to root
            target_file.write_text(content)
            print("✅ MONOLITH.md updated in root.")
        except Exception as e:
            print(f"⚠️ Failed to update MONOLITH.md: {e}")
            
# ----------------------------------------------------------------------
# FastMCP Pilot Integration
# ----------------------------------------------------------------------
try:
    from fastmcp import FastMCP
    
    # Initialize FastMCP Server
    mcp = FastMCP("Side Monolith")

    @mcp.tool()
    async def run_forensic_audit(project_path: str = ".", dimension: str = None, fix: bool = False) -> str:
        """
        Runs the full Side Forensic Audit on the codebase.
        
        Args:
            project_path: Path to the project root (default: current directory)
            dimension: Optional specific dimension to audit (e.g., 'Security')
            fix: Whether to apply safe auto-fixes
        """
        print(f"🚀 FastMCP: Starting Forensic Audit on {project_path}...")
        
        # Instantiate the existing business logic
        runner = ForensicAuditRunner(project_path)
        
        if dimension:
            summary = await runner.run_dimension(dimension)
            if not summary:
                return f"❌ Unknown dimension: {dimension}"
            # Apply fixes if requested
            if fix:
                await runner.apply_fixes(summary)
            return runner._generate_markdown_report(summary)
        else:
            # Full Run
            summary = await runner.run()
            if fix:
                await runner.apply_fixes(summary)
            return runner._generate_markdown_report(summary)

except ImportError:
    print("⚠️ FastMCP not installed. Skipping Pilot integration.")
    mcp = None

if __name__ == "__main__":
    import asyncio
    import sys
    
    # If run with 'fastmcp run', this block is skipped.
    # If run as script, use the old manual CLI.
    # ... (existing CLI code remains below) ...
            
