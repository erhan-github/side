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
from side.utils.labels import ForensicLabel

# Strategic Weighting Dossier [Palantir-Level]
DIMENSION_WEIGHTS = {
    "security": 100,
    "law": 95,
    "logic": 80,
    "resilience": 70,
    "marketfit": 60,
    "performance": 50,
    "velocity": 40,
    "docs": 30,
    "architecture": 20,
    "system": 10,
}

SEVERITY_MULTIPLIERS = {
    "CRITICAL": 5,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
    "INFO": 0,
}

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
        
        # 3. Render Monolith Dashboard (Pure Evidence)
        seen_finding_ids = set()
        
        # Gather Strategic Findings from Store (Restored)
        findings_data = []
        try:
            findings_data = store.get_active_findings(project_id)
        except Exception as e:
            logger.debug(f"Failed to fetch strategic findings: {e}")

        # Strategic Prioritization Logic
        def strategic_sort_key(f):
            dim = f.get('metadata', {}).get('dimension', 'system').lower()
            sev = f.get('severity', 'LOW').upper()
            weight = DIMENSION_WEIGHTS.get(dim, 10)
            multiplier = SEVERITY_MULTIPLIERS.get(sev, 1)
            return -(weight * multiplier) # Negative for descending order

        findings_data.sort(key=strategic_sort_key)

        lines = [
            f"<!-- 🔐 MONOLITH_SIG: {project_id[:8]} // PROVOCATION_ENGINE // DO_NOT_EDIT -->",
            "",
            f"Grade: {eval_result['grade']} ({eval_result['raw_score']}/400)",
            f"Last Sync: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            "",
            "   ┌── ⚡ SIGNAL READY ──┐",
            "   │  → EXECUTE IN IDE  │",
            "   └────────────────────┘",
            "",
            "---",
            "",
        ]

        # DEEP INTELLIGENCE (Priority: TOP)
        lines.extend([
            "DEEP INTELLIGENCE SUGGESTIONS",
            "",
        ])
        
        # 1. Semantic Security Scan (Strategic Overwatch)
        crit_finds = []
        try:
            crit_finds = store.get_active_findings(project_id, severity='CRITICAL')
        except Exception as e:
            logger.debug(f"Failed to fetch critical findings: {e}")

        crit = audit_summary.get('CRITICAL', 0)
        high = audit_summary.get('HIGH', 0)
        
        from side.utils.soul import StrategicSoul
        
        if crit > 0 or high > 0:
            target_criticals = crit_finds[:3]
            
        if crit > 0 or high > 0:
            target_criticals = crit_finds[:3]
            
            # 1. Render Specific Critical Findings directly
            if target_criticals:
                for cf in target_criticals:
                    lines.extend([
                        f"{ForensicLabel.format_title('security', cf['type']).upper()}",
                        f"{StrategicSoul.inject_fusion(cf)}",
                        "",
                        "---",
                        ""
                    ])
                    seen_finding_ids.add(cf['id'])
            
            # 2. Render Backlog Summary if exists
            total_backlog = len(crit_finds) + high - len(target_criticals)
            
            if total_backlog > 0:
                 overwatch_body = f"Detected {total_backlog} additional technical anomalies awaiting resolution."
                 overwatch_action = "List remaining security vulnerabilities and prepare a technical patch plan for immediate resolution."
                 lines.extend([
                    f"{ForensicLabel.format_title('security', 'SECURITY BACKLOG').upper()}",
                    f"{StrategicSoul.fusion_literal('🛡️', 'Security', overwatch_body, overwatch_action)}",
                    "",
                    "---",
                    ""
                 ])

        # 2. Logic Consistency (Brain)
        logic_matches = []
        try:
            # Broaden matching for 'Logic' findings
            logic_matches = [f for f in findings_data if 
                             f.get('metadata', {}).get('dimension', '').lower() in ['logic', 'code quality'] or 
                             "Bare Except" in f['type']]
        except Exception:
            pass

        if logic_matches:
            for lf in logic_matches[:2]:
                lines.extend([
                    f"{ForensicLabel.format_title('logic', lf['type']).upper()}",
                    f"{StrategicSoul.inject_fusion(lf)}",
                    "",
                    "---",
                    ""
                ])
                # Add to seen so they don't appear in general list
                seen_finding_ids.add(lf['id'])
        else:
            logic_nom_prompt = '"Hey Side, run a deep logic audit to maintain this state."'
            lines.extend([
                f"{ForensicLabel.format_title('logic', 'LOGIC CONSISTENCY: NOMINAL').upper()}",
                f"{StrategicSoul.fusion_literal('🧩', 'Logic', 'Logic gates verified. (0 Logical anomalies detected).', logic_nom_prompt)}",
                "",
                "---",
                ""
            ])

        # FORENSIC FINDINGS (General List)
        lines.extend([
            "FORENSIC PROMPTING SUGGESTIONS",
            "",
        ])

        # Render Top Findings (Conversational IDE-Optimized)
        count = 0
        for f in findings_data:
            if count >= 10: break
            if f['id'] in seen_finding_ids: continue
            
            seen_finding_ids.add(f['id'])
            dim = f.get('metadata', {}).get('dimension', 'system')
            
            lines.extend([
                f"{ForensicLabel.format_title(dim, f['type']).upper()}",
                f"{StrategicSoul.inject_fusion(f)}",
                "",
                "---",
                ""
            ])
            count += 1
            
        if count == 0:
            sys_nom_prompt = '"Check system health."'
            lines.extend([
                f"{ForensicLabel.format_title('system', 'FORENSIC PROMPTING: NOMINAL').upper()}",
                f"{StrategicSoul.fusion_literal('⬛', 'System', 'Strategic signals are nominal. (0 detections).', sys_nom_prompt)}",
                "",
                "---",
                ""
            ])

        # 4. Global Action Prompt (If total is 0)
        total_findings = len(findings_data) + len(crit_finds)
        if total_findings == 0:
            lines.append("HEY SIDE! NO ACTIVE FINDINGS DETECTED. RUN 'SIDE SCAN' TO POPULATE THE COMMAND CENTER.")
            lines.append("")



        monolith_path.write_text("\n".join(lines))
        
        # 4. Seal the Monolith
        _harden_monolith(monolith_path)
        
        return str(monolith_path)
        
    except Exception as e:
        logger.warning(f"Monolith Evolution Failed: {e}")
        raise e
