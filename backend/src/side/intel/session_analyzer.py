"""
Timeline Projector - Session Context History.
Provides an audit-safe summary of recent activity for LLM context.
"""

from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime, timezone
import json

from side.storage.modules.audit import AuditService
from side.storage.modules.strategy import StrategicStore

class SessionAnalyzer:
    def __init__(self, audit: AuditService, strategic: StrategicStore):
        self.audit = audit
        self.strategic = strategic

    def get_session_context(self, session_id: str, limit: int = 5) -> str:
        """
        [SESSION CONTEXT]: Traverses the causal history to inject the most relevant chain.
        Prioritizes: Root Cause (Edit) -> Intermediary Friction -> Terminal Error.
        """
        try:
            # 1. Fetch activities for this session
            activities = self.audit.get_causal_timeline(session_id)
            if not activities:
                return "## [SESSION_HISTORY]: No history for this session."

            # 2. Extract the Thread (Backwards traversal from latest)
            # Find terminal signal (usually the latest)
            signals = [a for a in activities if a["type"] == "SIGNAL"]
            if not signals:
                return "## [SESSION_HISTORY]: No signals captured in this session."

            thread = []
            current = signals[-1]["data"] # Start from latest signal
            
            while current and len(thread) < limit:
                thread.append(current)
                parent_id = current.get("parent_id")
                if not parent_id:
                    break
                # Find parent in signals
                parent = next((s["data"] for s in signals if s["data"].get("id") == parent_id), None)
                current = parent

            thread.reverse() # Chronological order

            # 3. Format the Session Context
            report = ["## 2. SESSION CONTEXT (Recent History)"]
            for node in thread:
                tool = node.get('tool', 'SYSTEM')
                action = node.get('action', 'unknown')
                payload = node.get('payload', {})
                
                # Check for Code Rules (formerly Causal Frames)
                frame = ""
                if "code_rule" in payload or "causal_frame" in payload:
                    rule_content = payload.get("code_rule", payload.get("causal_frame", ""))
                    frame = f"\n   [RULE]:\n   ```\n   {rule_content}\n   ```"
                
                snippet = payload.get('snippet', payload.get('file', ''))
                report.append(f"- **{tool}**.{action} ({snippet}){frame}")

            return "\n".join(report)

        except Exception as e:
            return f"## [PROTOCOL ERROR]: Session analysis failed: {e}"

    def get_summary_history(self, project_id: str = "global", limit: int = 15) -> str:
        """
        [CONTEXT RECOVERY]: Narrative summary history.
        """
        try:
            # 1. Fetch Recent Activities (The Raw Stream)
            activities = self.audit.get_recent_activities(project_id, limit=limit)
            
            # 2. Fetch Work Context (The Focus)
            work_ctx = self.audit.get_latest_work_context(str(Path.cwd()))
            
            # 3. Construct the Narrative
            report = ["## 2. SESSION TIMELINE (Recent History)"]
            
            if work_ctx:
                age = work_ctx['detected_at']
                focus = work_ctx.get('focus_area', 'General')
                report.append(f"**active_focus**: '{focus}' (Updated: {age})")
                
            report.append("**recent_events**:")
            
            if not activities:
                 report.append("- [No recent activities recorded]")
            else:
                for act in activities:
                    tool = act.get('tool', 'SYSTEM')
                    action = act.get('action', 'unknown')
                    # format timestamp
                    try:
                        ts = act.get('created_at', '')
                        time_str = ts.split('T')[-1][:5] if 'T' in ts else ts
                    except:
                        time_str = "now"
                        
                    # Extract payload summary
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
            return f"## [ERROR] Failed to load Session History: {e}"
