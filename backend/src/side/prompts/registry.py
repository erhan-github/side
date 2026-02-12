"""
MCP Prompt Registry - Dynamic User-Facing Scenarios.
Optimized for 'Thin the Fat' architecture and standard FastMCP SDK usage.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from mcp.types import (
    GetPromptResult,
    PromptArgument,
    PromptMessage,
    TextContent,
)

from side.storage.modules import (
    ContextEngine,
    SessionCache,
    IdentityService,
    DecisionStore
)

logger = logging.getLogger("side")

class DynamicPromptManager:
    """
    Manages dynamic MCP prompts with optimized context retrieval.
    Each method provides the logic for a specific prompt scenario.
    """
    def __init__(self):
        from side.storage.modules.audit import AuditService
        self.engine = ContextEngine()
        self.audits = AuditService(self.engine)
        self.plans = DecisionStore(self.engine)
        self.cache = SessionCache(self.engine)
        self.profile = IdentityService(self.engine)
        self.project_path = Path.cwd()
        self.project_id = ContextEngine.get_project_id(self.project_path)

    def handle_technical_question(self, question: str) -> GetPromptResult:
        profile = self.profile.get_user_profile(self.project_id) or {}
        decisions = self.plans.list_rejections(self.project_id, limit=3)
        past_decisions = "\n".join([f"- Q: {r['question']} -> A: {r['answer']}" for r in decisions]) if decisions else "None."

        text = (
            f"I need a technical decision.\n\n"
            f"**Question**: \"{question}\"\n\n"
            f"**Context**:\n"
            f"- **Stack**: {profile.get('tech_stack', 'Standard')}\n"
            f"- **Precedent**:\n{past_decisions}\n\n"
            f"Analyze trade-offs and give a verdict (YES/NO/DEFER) with rationale."
        )
        return GetPromptResult(description="Technical Consultation", messages=[self._msg(text)])

    def handle_status(self) -> GetPromptResult:
        all_plans = self.plans.list_plans(self.project_id, status="active")
        top_focus = all_plans[0]['title'] if all_plans else "No active directives."
        activities = self.audits.get_recent_activities(self.project_id, limit=5)
        recent_context = "\n".join([f"- {a['action']} ({a.get('tool', 'manual')})" for a in activities]) if activities else "None."
        
        text = (
            f"Give me a Status Update.\n\n"
            f"**Current Focus**: {top_focus}\n"
            f"**Recent Context**:\n{recent_context}\n\n"
            f"Tell me what I should do next to advance the Focus. Be concise."
        )
        return GetPromptResult(description="Status Update", messages=[self._msg(text)])

    def handle_fix_issues(self) -> GetPromptResult:
        findings = self.audits.get_recent_activities(self.project_id, limit=20)
        violations = [f for f in findings if f.get('outcome') == 'VIOLATION']
        top_issue = violations[0] if violations else (findings[0] if findings else None)
        
        if not top_issue:
             return GetPromptResult(description="No issues", messages=[self._msg("No issues found to fix.")])
        
        text = (
            f"Fix this {top_issue.get('severity', 'HIGH')} issue:\n\n"
            f"**Issue**: {top_issue.get('message')}\n"
            f"**File**: {top_issue.get('file_path')}\n"
            f"**Instructions**: Analyze the code and apply a robust patch."
        )
        return GetPromptResult(description=f"Fix: {top_issue.get('message', 'Issue')}", messages=[self._msg(text)])

    def handle_readiness(self) -> GetPromptResult:
        findings = self.audits.get_recent_activities(self.project_id, limit=50)
        crit = len([f for f in findings if f.get('outcome') == 'VIOLATION'])
        status = "🔴 BLOCKED" if crit > 0 else "🟢 CLEAR"
        
        text = (
            f"Perform a Readiness Check. Current Status: {status}\n\n"
            f"- Critical Issues: {crit}\n"
            f"1. Run audit on modified files.\n"
            f"2. Check for leftover debug code.\n"
            f"3. Verdict: **SHIP IT** or **BLOCK**."
        )
        return GetPromptResult(description="Readiness Check", messages=[self._msg(text)])

    def handle_design_review(self, code: str) -> GetPromptResult:
        # Optimized component discovery
        components = []
        ui_dir = self.project_path / "web/components"
        if ui_dir.exists():
            components = [f.stem for f in ui_dir.glob("*.tsx") if not f.name.startswith("index")]
        
        c_list = ", ".join(sorted(components)) or "Standard Elements"
        text = (
            f"Review this frontend code. Available Components: [{c_list}]\n\n"
            f"**Code**:\n```tsx\n{code}\n```\n\n"
            f"Advise on component reuse and consistency."
        )
        return GetPromptResult(description="Design Review", messages=[self._msg(text)])

    def handle_security_fix(self) -> GetPromptResult:
        text = "List all detected security violations and provide safe remediation for each."
        return GetPromptResult(description="Security Fix", messages=[self._msg(text)])

    def handle_audit_deep(self, query: str) -> GetPromptResult:
        text = f"Perform a deep audit for: {query}\nAnalyze cross-file dependencies and report any architectural gaps."
        return GetPromptResult(description="Deep Audit", messages=[self._msg(text)])

    def _msg(self, text: str) -> PromptMessage:
        return PromptMessage(role="user", content=TextContent(type="text", text=text))

def register_prompt_handlers(server, prompt_manager: DynamicPromptManager):
    """
    Registers the prompts using the server.prompt() decorator-style call.
    Note: We use the function name 'prompt' as a closure to register individual handlers.
    """
    
    @server.prompt(name="ask_technical_question")
    def ask_technical_question(question: str) -> GetPromptResult:
        return prompt_manager.handle_technical_question(question)

    @server.prompt(name="get_status")
    def get_status() -> GetPromptResult:
        return prompt_manager.handle_status()

    @server.prompt(name="fix_general_issues")
    def fix_general_issues() -> GetPromptResult:
        return prompt_manager.handle_fix_issues()

    @server.prompt(name="verify_readiness")
    def verify_readiness() -> GetPromptResult:
        return prompt_manager.handle_readiness()

    @server.prompt(name="review_design")
    def review_design(code: str) -> GetPromptResult:
        return prompt_manager.handle_design_review(code)

    @server.prompt(name="fix_security_issues")
    def fix_security_issues() -> GetPromptResult:
        return prompt_manager.handle_security_fix()

    @server.prompt(name="audit_deep")
    def audit_deep(query: str) -> GetPromptResult:
        return prompt_manager.handle_audit_deep(query)
