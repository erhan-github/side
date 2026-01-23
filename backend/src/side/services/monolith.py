"""
Monolith Service - The Orchestrator of the Strategic Dashboard.

This service is responsible for aggregating intelligence from all subsystems
(Memory, Forensics, Instrumentation, Billing) and rendering the 
Unified Strategic Monolith (.side/MONOLITH.md).

It is the "View Controller" of the Side Operating System.
"""

import logging
import os
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from side.utils.paths import get_side_dir, get_repo_root
from side.intel.evaluator import StrategicEvaluator
from side.intel.intelligence_store import IntelligenceStore
from side.intel.strategist import Strategist
from side.instrumentation.engine import InstrumentationEngine

logger = logging.getLogger(__name__)

MONOLITH_NAME = "MONOLITH.md"

def _soften_monolith(path: Path):
    """Temporarily unlock the Monolith for evolution."""
    try:
        if path.exists():
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    except Exception as e:
        logger.debug(f"Monolith softening skipped: {e}")

def _harden_monolith(path: Path):
    """Seal the Monolith after evolution (Read-only for all)."""
    try:
        if path.exists():
            os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    except Exception as e:
        logger.debug(f"Monolith hardening skipped: {e}")

async def generate_monolith(db: Any) -> str | None:
    """
    Generate and seal the .side/MONOLITH.md as the definitive strategic anchor.
    
    Args:
        db: The SimplifiedDatabase instance.
        
    Returns:
        Path string to the generated monolith or None if failed.
    """
    try:
        side_dir = get_side_dir()
        monolith_path = side_dir / MONOLITH_NAME
        repo_root = get_repo_root()
        
        # 1. Unlock for Evolution
        _soften_monolith(monolith_path)
        
        # 2. Gather Intelligence
        project_id = db.get_project_id(repo_root)
        profile = db.get_profile(project_id)
        
        # SELF-HEALING: If profile is missing (Day 1 or Migration), auto-detect immediately
        if not profile:
            try:
                # Import here to avoid circular dependencies if core uses this service
                from side.tools.core import get_auto_intel
                auto_intel = get_auto_intel()
                await auto_intel.get_or_create_profile(repo_root)
                profile = db.get_profile(project_id) or {}
            except Exception as e:
                logger.warning(f"Failed to auto-heal profile: {e}")
                profile = {}

        all_plans = db.list_plans()
        
        # Merge audit summaries
        audit_summary = db.get_audit_summary(project_id)
        
        # Integrate IntelligenceStore findings
        try:
            store = IntelligenceStore(db)
            intel_stats = store.get_finding_stats(project_id)
            
            # Map new stats to summary
            audit_summary['CRITICAL'] = audit_summary.get('CRITICAL', 0) + intel_stats.get('critical', 0)
            audit_summary['HIGH'] = audit_summary.get('HIGH', 0) + intel_stats.get('high', 0)
            audit_summary['MEDIUM'] = audit_summary.get('MEDIUM', 0) + intel_stats.get('medium', 0)
            audit_summary['LOW'] = audit_summary.get('LOW', 0) + intel_stats.get('low', 0)
        except Exception as e:
            logger.error(f"Failed to fetch intel stats: {e}")
            
        activities = db.get_recent_activities(project_id, limit=100)
        
        # Calculate Two-Pillar Grade
        eval_result = StrategicEvaluator.calculate_iq(
            profile, all_plans, audit_summary, 
            project_root=repo_root, 
            activities=activities
        )
        
        # Provocation Engine (Strategic Insight)
        strategist = Strategist(db, repo_root)
        insight = await strategist.handle_monolith_evolution(
            score=eval_result['score'],
            grade=eval_result['grade'],
            label=eval_result['label'],
            forensic_grade=eval_result['forensic_grade'],
            strategic_grade=eval_result['strategic_grade'],
            top_focus=eval_result['top_focus'],
            dimensions=eval_result['dimensions'],
            security_matrix=audit_summary,
            active_plans=all_plans
        )
        
        # 3. Render Monolith 2.0 Dashboard
        lines = [
            f"<!-- 🔐 MONOLITH_SIG: {project_id[:8]} // PROVOCATION_ENGINE // DO_NOT_EDIT -->",
            "",
            "# ⬛ PROJECT STATUS",
            f"> **Asset ID**: `{project_id[:8]}`",
            f"> **Last Sync**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            f"> **Grade**: **{eval_result['grade']} ({eval_result['raw_score']}/400)**",
            f"> **Pillar Overview**: `Forensic: {eval_result['forensic_grade']} ({eval_result['forensic_score']}/100)` // `Strategic: {eval_result['strategic_grade']} ({eval_result['strategic_score']}/100)`",
            "---",
            "",
        ]

        # 🛑 SMART ALERTS
        # Condition 1: Critical Vulnerabilities
        crit_count = audit_summary.get('CRITICAL', 0)
        if crit_count > 0:
            lines.extend([
                f"> 🛑 **Action Required**: {crit_count} Critical Vulnerabilities detected.",
                "> Run `/fix-security-critical` immediately to secure the asset.",
                ""
            ])

        # Condition 2: Low Capacity
        bal = profile.get("token_balance", 0)
        if bal < 100:
             lines.extend([
                f"> ⚠️ **Low Capacity**: {bal} SUs remaining.",
                "> Allocation will be adjusted based on outcome leverage.",
                ""
             ])

        # 00_INSTRUMENTATION (Factual Observability)
        try:
             ie_check = InstrumentationEngine(db)
             status = ie_check.get_status(project_id)
             lines.extend([
                 "## 00_INSTRUMENTATION",
                 f"> **Operating Mode**: {status['operating_mode']}",
                 f"> **Leverage Factor**: {status['leverage_factor']} (Outcome/Action)",
                 f"> **Recent Outcomes**: {', '.join(status['recent_outcomes'][:3])}",
                 ""
             ])
        except Exception as e:
            logger.error(f"Failed to render instrumentation: {e}")

        lines.append("## 01_VITAL_SIGNS")
        
        # VITAL SIGNS: Top 3 Critical Dimensions only
        sorted_dims = sorted(eval_result['dimensions'].items(), key=lambda x: x[1])
        top_3 = sorted_dims[:3]
        
        for k, v in top_3:
            # Normalized to 10 blocks (v is out of 40) -> v/4
            # If v < 28 (70%), it's critical
            status = "! ISSUE" if v < 28 else "✓ GOOD"
            bars = "█" * (v // 4) + "░" * (10 - (v // 4))
            lines.append(f"[{k:12}] {bars} {status}")

        lines.append("")

        # STRATEGIC INSIGHT (Provocation)
        lines.extend([
            "## 02_BRIEFING",
            f"**Focus**: {eval_result['top_focus']}",
            f"**Alert**: {eval_result['grade']} Grade ({eval_result['label']})",
            "",
            "> 💡 **STRATEGIC INSIGHT**:",
            f"> \"{insight.get('insight', 'System stable. No immediate threats detected.')}\"",
            ">",
            "> **YOU CAN ASK YOUR LLM**:",
        ])
        
        actions = insight.get('actions', [])
        if actions:
            for action in actions:
                lines.append(f"> - \"{action}\"")
        else:
             lines.append("> - \"Check system health.\"")
        lines.append("")

        # DEEP DIVE (Matrices)
        lines.append("## 03_DEEP_DIVE")
        
        # Forensic Pillar
        lines.append(f"### 🛡️ FORENSIC HEALTH ({eval_result['forensic_grade']} - {eval_result['forensic_score']}/100)")
        
        # 1. Security
        crit = audit_summary.get('CRITICAL', 0)
        high = audit_summary.get('HIGH', 0)
        sec_alert = f"! {crit} CRITICAL" if crit > 0 else (f"! {high} HIGH" if high > 0 else "✓ SECURE")
        lines.append(f"[Security    ] {sec_alert}")
        if crit > 0 or high > 0:
            lines.append(f"> 🔴 **Action Available**: Run `/fix-security-critical` to resolve {crit+high} issues.")
            lines.append(f"> \"Hey Side, list all critical/high security issues and give me a fix plan.\"")
        
        # 2. Velocity
        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", "--oneline", "-n", "100", "--since=7 days ago"],
                capture_output=True, text=True, cwd=str(repo_root), timeout=5
            )
            commit_count = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            vel_status = "✓ STRONG" if commit_count > 10 else "! STALLED"
        except:
            vel_status = "? UNKNOWN"
        lines.append(f"[Velocity    ] {vel_status} ({commit_count if 'commit_count' in locals() else 0} commits/7d)")
        
        # 3. Architecture
        has_src = (repo_root / "src").exists()
        has_tests = (repo_root / "tests").exists()
        arch_status = "✓ STRUCTURED" if has_src and has_tests else "! UNSTRUCTURED"
        lines.append(f"[Architecture] {arch_status}")
        lines.append("")

        # Strategic Pillar
        lines.append(f"### 🧠 STRATEGIC VIABILITY ({eval_result['strategic_grade']} - {eval_result['strategic_score']}/100)")
        
        # 1. MarketFit (Simulations)
        sims = [a for a in activities if a.get("tool") == "simulate"]
        sim_status = "✓ VALIDATED" if len(sims) > 5 else "! UNTESTED"
        lines.append(f"[MarketFit   ] {sim_status} ({len(sims)} simulations)")
        
        # 2. Investor
        has_vis = (repo_root / "VISION.md").exists()
        has_rdm = (repo_root / "ROADMAP.md").exists()
        inv_status = "✓ READY" if has_vis and has_rdm else "! INCOMPLETE"
        lines.append(f"[Investor    ] {inv_status}")
        if inv_status == "! INCOMPLETE":
            lines.append("> 🔴 \"Hey Side, help me draft a Vision and Roadmap to make this investor-ready.\"")
        lines.append("")
        
        # DIRECTIVES
        lines.append("## 04_ACTIVE_DIRECTIVES")
        active_count = len([p for p in all_plans if p.get("status") != "done"])
        if active_count == 0:
            lines.append("No active directives. Ask me to 'Add a task' to get started.")
        else:
             for p in all_plans:
                 if p.get("status") != "done":
                     lines.append(f"- [{p.get('type','task')[0].upper()}] {p['title']}")
        lines.append("")

        # 05_CREDITS (Real Ledger)
        try:
            tokens_monthly = profile.get("tokens_monthly", 50)
            tokens_used = profile.get("tokens_used", 0)
            balance = profile.get("token_balance", tokens_monthly - tokens_used)
            tier = profile.get("tier", "hobby").upper()
            
            lines.extend([
                "## 05_CREDITS",
                f"**Balance**: 💰 {balance} SUs",
                f"**Usage**: `{tokens_used}` / `{tokens_monthly}` SUs this period",
                f"**Layer**: {tier}",
                ""
            ])
        except Exception:
            pass

        # 06_DEPLOYMENT_HEALTH (New Section)
        try:
            # Fetch active deployment findings from IntelStore/DB
            # We filter for 'DEPLOYMENT_GOTCHA' type which we just added
            if hasattr(db, 'get_findings_by_type'):
                deploy_issues = db.get_findings_by_type('DEPLOYMENT_GOTCHA')
                if deploy_issues:
                    lines.extend([
                        "## 06_DEPLOYMENT_HEALTH",
                        "> ⚠️ **Pre-Flight Checks Failed**",
                        ""
                    ])
                    for issue in deploy_issues:
                        lines.append(f"### 🔴 {issue.get('message', 'Deployment Issue')}")
                        lines.append(f"- **File**: `{issue.get('file')}`")
                        lines.append(f"- **Fix**: {issue.get('action')}")
                        if issue.get('metadata') and issue['metadata'].get('reference'):
                             lines.append(f"- **Docs**: {issue['metadata']['reference']}")
                        lines.append("")
                    lines.append("> *Run `side audit` to re-scan.*")
                    lines.append("")
        except Exception as e:
            logger.warning(f"Failed to render deployment health: {e}")

        # ACTIVITY LOG
        lines.extend([
            "---",
            "## 07_ACTIVITY_LOG",
        ])
        activities = db.get_recent_activities(project_id, limit=15)
        for a in activities:
            # Simple time: HH:MM
            dt = datetime.fromisoformat(a['created_at'].replace('Z', '+00:00'))
            ts = dt.strftime('%H:%M')
            lines.append(f"`{ts}` **{a['tool'].upper()}** // {a['action']}")
        
        monolith_path.write_text("\n".join(lines))
        
        # 4. Seal the Monolith
        _harden_monolith(monolith_path)
        
        return str(monolith_path)
        
    except Exception as e:
        logger.warning(f"Monolith Evolution Failed: {e}")
        return None
