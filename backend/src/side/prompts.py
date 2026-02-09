"""
Prompt management for Side MCP.
"""

import logging
from pathlib import Path
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
)

from side.storage.modules.base import ContextEngine
from side.storage.modules.audit import AuditStore
from side.storage.modules.strategy import StrategyStore
from side.storage.modules.transient import OperationalStore
from side.storage.modules.identity import IdentityStore

logger = logging.getLogger("side-mcp")

class DynamicPromptManager:
    def __init__(self):
        # Lean Architecture
        self.engine = ContextEngine()
        self.audit = AuditStore(self.engine)
        self.strategic = StrategyStore(self.engine)
        self.operational = OperationalStore(self.engine)
        self.identity = IdentityStore(self.engine)
        self.project_path = Path.cwd()
        self.project_id = ContextEngine.get_project_id(self.project_path)

    def get_prompts(self) -> list[Prompt]:
        prompts = [
            Prompt(
                name="ask_technical_question",
                description="Get technical advice on a specific question.",
                arguments=[
                    PromptArgument(
                        name="question",
                        description="Your technical question (e.g., 'Components vs Hooks?')",
                        required=True,
                    ),
                ],
            ),
        ]
        
        try:
            # Lean Architecture - Direct AuditStore access
            findings = self.audit.get_recent_activities(self.project_id, limit=100)
            
            # Filter for meaningful architectural or security findings
            security_issues = [f for f in findings if f.get('outcome') == 'VIOLATION' or 'security' in str(f.get('payload', '')).lower()]
            perf_issues = [f for f in findings if 'performance' in str(f.get('payload', '')).lower()]
            
            if security_issues:
                prompts.append(Prompt(
                    name="fix_security_issues",
                    description=f"Fix {len(security_issues)} Security Issues identified in logs.",
                    arguments=[]
                ))
            
            # [Level 3 Interaction: fix_flow]
            if findings:
                prompts.append(Prompt(
                    name="fix_general_issues",
                    description="Auto-resolve the most pressing issue found in logs.",
                    arguments=[]
                ))
            
            # [Experience V2: The Executive Briefing]
            prompts.append(Prompt(
                name="get_status",
                description="Get a status update based on recent activity and plans.",
                arguments=[]
            ))
            
            # [Experience V2: The Gatekeeper]
            prompts.append(Prompt(
                name="verify_readiness",
                description="Check if the system is ready for deployment/shipping.",
                arguments=[]
            ))
            
            # [Experience V3: The Frontend Guard]
            prompts.append(Prompt(
                name="review_design",
                description="Review code for UI consistency and component usage.",
                arguments=[
                    PromptArgument(
                        name="code",
                        description="The code snippet or file content to review.",
                        required=True,
                    )
                ]
            ))
            
            # [Experience V3: The Truth Engine]
            prompts.append(Prompt(
                name="verify_documentation",
                description="Check if documentation matches the actual codebase.",
                arguments=[]
            ))

            # [Experience V4: Deep Audit]
            prompts.append(Prompt(
                name="audit_deep",
                description="Scan codebase for specific patterns or issues.",
                arguments=[
                    PromptArgument(
                        name="query",
                        description="What to look for (e.g. 'unused code')",
                        required=True,
                    )
                ]
            ))
            
            if perf_issues:
                prompts.append(Prompt(
                    name="fix_performance_issues",
                    description=f"Fix {len(perf_issues)} Performance bottlenecks.",
                    arguments=[]
                ))
                
        except Exception as e:
            logger.error(f"Failed to load dynamic prompts: {e}")
            
        return prompts

    def get_prompt_result(self, name: str, args: dict[str, str]) -> GetPromptResult:
        if name == "fix_general_issues":
            # Smart Logic: Find the worst issue
            findings = self.audit.get_recent_activities(self.project_id, limit=50)
            # Filter for violations
            violations = [f for f in findings if f.get('outcome') == 'VIOLATION']
            if not violations:
                 return GetPromptResult(
                    description="No issues found",
                    messages=[PromptMessage(role="user", content=TextContent(type="text", text="Run a deep audit to find new things to fix."))]
                )
            
            # Sort by severity (CRITICAL > HIGH > MEDIUM > LOW)
            severity_map = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
            findings.sort(key=lambda x: severity_map.get(x.get('severity', 'INFO'), 5))
            top_issue = findings[0]
            
            return GetPromptResult(
                description=f"Fix: {top_issue.get('message', 'Issue')}",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Fix this {top_issue.get('severity')} issue:\n\n"
                                 f"**Issue**: {top_issue.get('message')}\n"
                                 f"**File**: {top_issue.get('file_path')}\n"
                                 f"**Instructions**: Analyze the code and apply a robust patch. Ensure tests pass."
                        ),
                    ),
                ],
            )
            
        if name == "get_status":
            # 1. Get Profile
            profile = self.identity.get_profile(self.project_id) or {}
            
            # 2. Get Active Plans
            all_plans = self.strategic.list_plans(self.project_id, status="active")
            top_focus = all_plans[0]['title'] if all_plans else "No active directives."
            
            # 3. Get Recent Activity (Context)
            activities = self.audit.get_recent_activities(self.project_id, limit=5)
            recent_context = "\n".join([f"- {a['action']} ({a['tool']})" for a in activities]) if activities else "None."
            
            return GetPromptResult(
                description="Status Update",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Give me a Status Update.\n\n"
                                 f"**User**: {profile.get('name', 'Founder')}\n"
                                 f"**Current Focus**: {top_focus}\n"
                                 f"**Recent Context**:\n{recent_context}\n\n"
                                 f"Analyze recent context and tell me what I should do next to advance the Focus. Be concise."
                        ),
                    ),
                ],
            )

        if name == "ask_technical_question":
            question = args.get("question", "What should we do?")
            
            # 1. Get Strategic Context
            profile = self.identity.get_profile(self.project_id) or {}
            stack = profile.get("tech_stack", "Unknown Stack")
            stage = profile.get("stage", "Unknown Stage")
            
            # 2. Get Past Decisions (Consistency)
            decisions = self.strategic.list_rejections(self.project_id, limit=3)
            past_decisions = "\n".join([f"- Q: {r['question']} -> A: {r['answer']}" for r in decisions]) if decisions else "None."

            return GetPromptResult(
                description="Technical Consultation",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"I need a technical decision.\n\n"
                                 f"**Question**: \"{question}\"\n\n"
                                 f"**Context**:\n"
                                 f"- **Stage**: {stage}\n"
                                 f"- **Stack**: {stack}\n"
                                 f"- **Precedent** (Last 3 Decisions):\n{past_decisions}\n\n"
                                 f"Analyze the trade-offs (Cost, Speed, Debt) and give a verdict (YES/NO/DEFER) with a one-sentence rationale."
                        ),
                    ),
                ],
            )

        if name == "verify_readiness":
            # 1. Get Security Posture
            # SFO Sprint: Simplified audit summary from audit store
            findings = self.audit.get_recent_activities(self.project_id, limit=100)
            crit = len([f for f in findings if f.get('outcome') == 'VIOLATION'])
            high = 0 # Placeholder for severity mapping in AuditStore
            
            # 2. Get Recent Work
            # Determine what to verify (e.g. files changed recently, though we can't easily get diffs here without git tool)
            # We'll ask the Agent to check Logic and Security.
            
            status = "🔴 BLOCKED" if crit > 0 else ("🟠 RISKY" if high > 0 else "🟢 CLEAR")
            
            return GetPromptResult(
                description="Readiness Check",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Perform a Readiness Check.\n\n"
                                 f"**Current Status**: {status}\n"
                                 f"- Critical Issues: {crit}\n"
                                 f"- High Issues: {high}\n\n"
                                 f"1. Run `audit` on any modified files.\n"
                                 f"2. Verify no debugging code or secrets are left.\n"
                                 f"3. Confirm compliance with the Active Plan.\n"
                                 f"4. Verdict: **SHIP IT** or **BLOCK**."
                        ),
                    ),
                ],
            )

        if name == "review_design":
            code_snippet = args.get("code", "")
            
            # 1. Discover Design System
            web_root = self.project_path / "web"
            components = []
            if web_root.exists():
                # Naive scan for components/ui or components
                ui_dir = web_root / "components"
                if ui_dir.exists():
                     # Recursively find .tsx files
                     for f in ui_dir.rglob("*.tsx"):
                         if not f.name.startswith("index"):
                             components.append(f.stem)
            
            component_list = ", ".join(sorted(components)) or "None detected."

            return GetPromptResult(
                description="Design Review",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Review this frontend code for consistency.\n\n"
                                 f"**Available Components**: [{component_list}]\n\n"
                                 f"**Code**:\n```tsx\n{code_snippet}\n```\n\n"
                                 f"Identify authorized components that should be used instead of raw HTML elements. Rewrite the code using them."
                        ),
                    ),
                ],
            )

        if name == "verify_documentation":
            # 1. Discover Strategy Docs
            docs_context = ""
            for doc_name in ["README.md", "backend/VISION.md", "docs/MASTER_ROADMAP.md"]:
                doc_path = self.project_path / doc_name
                if doc_path.exists():
                     content = doc_path.read_text()
                     # Extract first 1000 chars to avoid prompt overflow but give enough context
                     docs_context += f"\n--- {doc_name} ---\n{content[:1000]}...\n"
            
            if not docs_context:
                docs_context = "No strategic documentation found."

            return GetPromptResult(
                description="Documentation Verification",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Verify that documentation matches reality.\n\n"
                                 f"**Docs Context**:\n{docs_context}\n\n"
                                 f"Identify feature claims in logs vs docs. Report any missing documentation or unimplemented claims."
                        ),
                    ),
                ],
            )
            
        if name == "fix_security_issues":
            return GetPromptResult(
                description="Fix Security Issues",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text="List all critical security issues. For each one:\n1. Explain the risk.\n2. Propose a code fix.\n3. Apply the fix.\n4. Verify the fix.",
                        ),
                    ),
                ],
            )
        
        if name == "fix_performance_issues":
            return GetPromptResult(
                description="Fix Performance Issues",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text="Identify top performance bottlenecks (N+1 queries, loops). Optimize them and verify the speedup.",
                        ),
                    ),
                ],
            )

            
        raise ValueError(f"Unknown prompt: {name}")

def register_prompt_handlers(server, prompt_manager: DynamicPromptManager):
    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """Return the list of available prompts."""
        return prompt_manager.get_prompts()

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
        """Handle prompt requests."""
        return prompt_manager.get_prompt_result(name, arguments or {})
