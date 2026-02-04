import logging
import os
import stat
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

async def generate_hub(db: Any) -> str:
    """
    Evolves the Strategic Hub (HUB.md) based on the latest strategic data.
    """
    from side.utils.paths import get_side_dir
    project_id = db.get_project_id()
    side_dir = get_side_dir()
    hub_path = side_dir / "HUB.md"
    
    logger.info(f"🏛️ [HUB]: Evolving Strategic Hub at {hub_path}")
    
    # 1. Soften the Hub for writing
    if hub_path.exists():
        try:
            os.chmod(hub_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        except Exception as e:
            logger.debug(f"Could not soften HUB: {e}")

    # 2. Collect Data
    plans = db.strategic.list_plans(project_id=project_id)
    activities = db.forensic.get_recent_activities(project_id=project_id, limit=5)
    
    # NEW: Fetch Forensic Audits (Strategic Friction)
    # We look for violations or high-severity issues
    audits = db.forensic.get_recent_audits(project_id=project_id, limit=10)
    friction = [a for a in audits if a.get('severity') in ['CRITICAL', 'HIGH', 'VIOLATION']]
    
    # 3. Generate Markdown
    lines = [
        "# Sidelith Strategic Hub\n",
        f"*Sovereign Strategic Identity for {project_id} (INTENTION FIREWALL ENABLED)*\n",
        "## 🎯 Strategic Objectives\n"
    ]
    
    objectives = [p for p in plans if p.get('type') == 'objective' and p.get('status') != 'done']
    for obj in objectives:
        lines.append(f"- [ ] **{obj['title']}** (ID: `{obj['id']}`)")
    
    if friction:
        lines.append("\n## ⚠️ Strategic Friction & Forensic Remediation\n")
        lines.append("These bottlenecks have been harvested by the **Wisdom Distiller**. Apply these directives to realign.\n")
        for issue in friction:
            severity = issue.get('severity', 'INFO')
            emoji = "🛑" if severity in ['CRITICAL', 'VIOLATION'] else "🟠"
            lines.append(f"### {emoji} {issue.get('message', 'Unknown Friction')}")
            lines.append(f"- **File**: `{issue.get('file_path', 'Global')}`")
            lines.append(f"- **Outcome**: `FORENSIC_PULSE` Detection")
            
            # Generate Remediation Directive (The "Pasteable Prompt" value)
            lines.append("\n> **Strategic Directive**:")
            lines.append(f"> Paste this into your LLM box: `Side, fix the {severity} friction in {issue.get('file_path')}: {issue.get('message')}. Maintain architectural intent.`\n")

    lines.append("\n## 🚀 Active Milestones\n")
    milestones = [p for p in plans if p.get('type') == 'milestone' and p.get('status') != 'done']
    for ms in milestones:
        lines.append(f"- [ ] {ms['title']}")
        
    lines.append("\n## ✅ Success Log\n")
    completed = [p for p in plans if p.get('status') == 'done']
    for c in completed[:10]:
        lines.append(f"- [x] {c['title']}")
        
    lines.append("\n## 📡 Real-time Intelligence\n")
    for act in activities:
        lines.append(f"- *{act.get('created_at', '')}*: {act.get('action', '')}")
        
    # 4. Write File
    try:
        hub_path.write_text("\n".join(lines))
        
        # 5. Harden the Hub (Read-only)
        os.chmod(hub_path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        
        logger.info("✨ [HUB]: Strategic Hub update successful.")
        return "HUB.md"
    except Exception as e:
        logger.error(f"Failed to generate HUB.md: {e}")
        return "ERROR"
