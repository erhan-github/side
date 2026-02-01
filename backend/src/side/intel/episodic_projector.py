"""
Sovereign Episodic Projector - The 'Hippocampus' of Sidelith.
Responsible for re-constructing the 'RAM' (Recent Context) from the Forensic Ledger.
"""

from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime, timezone
import json

from side.storage.modules.forensic import ForensicStore
from side.storage.modules.strategic import StrategicStore

class EpisodicProjector:
    def __init__(self, forensic: ForensicStore, strategic: StrategicStore):
        self.forensic = forensic
        self.strategic = strategic

    def get_episode_stream(self, project_id: str = "global", limit: int = 15) -> str:
        """
        [PHOENIX PROTOCOL LAYER 2]: Generates the 'Previously On...' summary.
        Fetches raw events and distills them into a coherent narrative vector.
        """
        try:
            # 1. Fetch Recent Activities (The Raw Stream)
            activities = self.forensic.get_recent_activities(project_id, limit=limit)
            
            # 2. Fetch Work Context (The Focus)
            # We assume project_path is current working dir for this context
            # In a real multi-tenant setup, we'd pass the specific path
            work_ctx = self.forensic.get_latest_work_context(str(Path.cwd()))
            
            # 3. Construct the Narrative
            report = ["## 2. EPISODIC STREAM (RAM - Recent History)"]
            
            if work_ctx:
                age = work_ctx['detected_at']
                focus = work_ctx.get('focus_area', 'General')
                report.append(f"**active_focus**: '{focus}' (Updated: {age})")
                
            report.append("**recent_events**:")
            
            if not activities:
                 report.append("- [No recent activities recorded in the Ledger]")
            else:
                for act in activities:
                    tool = act.get('tool', 'SYSTEM')
                    action = act.get('action', 'unknown')
                    # format timestamp relative or short
                    try:
                        ts = act.get('created_at', '')
                        # Simple truncation for cleaner visual
                        time_str = ts.split('T')[-1][:5] if 'T' in ts else ts
                    except:
                        time_str = "now"
                        
                    # Extract payload summary if interesting
                    extra = ""
                    payload = act.get('payload', {})
                    if payload:
                        if "outcome" in payload:
                            extra = f" -> {payload['outcome']}"
                        elif "file" in payload:
                            extra = f" ({payload['file']})"
                        elif "id" in payload:
                            extra = f" [ID:{payload['id'][:6]}]"
                            
                    report.append(f"- [{time_str}] **{tool}**.{action}{extra}")
            
            return "\n".join(report)
            
        except Exception as e:
            return f"## [ERROR] Failed to load Episodic RAM: {e}"
