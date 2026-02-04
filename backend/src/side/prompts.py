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
from side.storage.modules.forensic import ForensicStore
from side.storage.modules.strategic import StrategicStore
from side.storage.modules.transient import OperationalStore
from side.storage.modules.identity import IdentityStore

logger = logging.getLogger("side-mcp")

class DynamicPromptManager:
    def __init__(self):
        # SFO Sprint: No Fat Architecture
        self.engine = ContextEngine()
        self.forensic = ForensicStore(self.engine)
        self.strategic = StrategicStore(self.engine)
        self.operational = OperationalStore(self.engine)
        self.identity = IdentityStore(self.engine)
        self.project_path = Path.cwd()
        self.project_id = ContextEngine.get_project_id(self.project_path)

    def get_prompts(self) -> list[Prompt]:
        prompts = [
            Prompt(
                name="strategy",
                description="Get strategic advice - 'What should I focus on?'",
                arguments=[
                    PromptArgument(
                        name="context",
                        description="Optional context about what you're working on",
                        required=False,
                    ),
                ],
            ),
        ]
        
        if not self.store:
            return prompts

        try:
            # SFO Sprint: No Fat - Direct ForensicStore access
            findings = self.forensic.get_recent_activities(self.project_id, limit=100)
            
            # Filter for meaningful architectural or security findings
            security_issues = [f for f in findings if f.get('outcome') == 'VIOLATION' or 'security' in str(f.get('payload', '')).lower()]
            perf_issues = [f for f in findings if 'performance' in str(f.get('payload', '')).lower()]
            
            if security_issues:
                prompts.append(Prompt(
                    name="fix-security-critical",
                    description=f"🚨 Fix {len(security_issues)} Critical Security Issues (Auth, Secrets, etc.)",
                    arguments=[]
                ))
            
            # [Level 3 Interaction: fix_flow]
            if findings:
                prompts.append(Prompt(
                    name="fix_flow",
                    description="✨ Smart Fix: Auto-resolves the most pressing issue found.",
                    arguments=[]
                ))
            
            # [Experience V2: The CSO Briefing]
            prompts.append(Prompt(
                name="brief",
                description="☀️ Mission Briefing: Strategic status, recent work, and today's focus.",
                arguments=[]
            ))
            
            # [Experience V2: The CSO Consult]
            prompts.append(Prompt(
                name="consult",
                description="🧠 Strategic Consultation: Get a CTO-level decision on a technical or business choice.",
                arguments=[
                     PromptArgument(
                        name="question",
                        description="The strategic question (e.g., 'Should we switch to Next.js?')",
                        required=True,
                    ),
                ]
            ))
            
            # [Experience V2: The CSO Gatekeeper]
            prompts.append(Prompt(
                name="verify",
                description="🛡️ Pre-Flight Check: Verify system health before shipping/deploying.",
                arguments=[]
            ))
            
            # [Experience V3: The Frontend Guard]
            prompts.append(Prompt(
                name="check_design",
                description="🎨 Design System Guard: Enforce UI consistency and prevent ad-hoc styling.",
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
                name="check_truth",
                description="🔍 Truth Engine: Verify that documentation (README, Vision) matches reality.",
                arguments=[]
            ))

            # [Experience V4: Deep Forensics]
            prompts.append(Prompt(
                name="audit_deep",
                description="🕵️ Deep Recursive Audit: Scan codebase for complex patterns (e.g. 'hardcoded secrets').",
                arguments=[
                    PromptArgument(
                        name="query",
                        description="What to look for (e.g. 'security vulnerabilities' or 'unused code')",
                        required=True,
                    )
                ]
            ))
            
            if perf_issues:
                prompts.append(Prompt(
                    name="fix-performance-critical",
                    description=f"⚡ Fix {len(perf_issues)} Performance bottlenecks (N+1 queries, loops)",
                    arguments=[]
                ))
                
        except Exception as e:
            logger.error(f"Failed to load dynamic prompts: {e}")
            
        return prompts

    def get_prompt_result(self, name: str, args: dict[str, str]) -> GetPromptResult:
        if name == "fix_flow":
            # Smart Logic: Find the worst issue
            findings = self.forensic.get_recent_activities(self.project_id, limit=50)
            # Filter for violations
            violations = [f for f in findings if f.get('outcome') == 'VIOLATION']
            if not violations:
                 return GetPromptResult(
                    description="No issues found",
                    messages=[PromptMessage(role="user", content=TextContent(type="text", text="Side, run a deep audit to find new things to fix."))]
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
                            text=f"Side, fix this {top_issue.get('severity')} issue:\n\n"
                                 f"**Issue**: {top_issue.get('message')}\n"
                                 f"**File**: {top_issue.get('file_path')}\n"
                                 f"**Fix**: Analyze the code and apply a robust patch.\n"
                                 f"**Verify**: Ensure tests pass after fixing."
                        ),
                    ),
                ],
            )
            
        if name == "brief":
            # 1. Get Profile
            profile = self.identity.get_profile(self.project_id) or {}
            
            # 2. Get Active Plans
            all_plans = self.strategic.list_plans(self.project_id, status="active")
            top_focus = all_plans[0]['title'] if all_plans else "No active directives."
            
            # 3. Get Recent Activity (Context)
            activities = self.forensic.get_recent_activities(self.project_id, limit=5)
            recent_context = "\n".join([f"- {a['action']} ({a['tool']})" for a in activities]) if activities else "None."
            
            return GetPromptResult(
                description="Mission Briefing",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Side, give me a Strategic Mission Briefing.\n\n"
                                 f"**Pilot**: {profile.get('name', 'Founder')} ({profile.get('tier', 'free').upper()})\n"
                                 f"**Current Focus**: {top_focus}\n"
                                 f"**Recent Context**:\n{recent_context}\n\n"
                                 f"**Goal**: Analyze my recent context and tell me exactly what I should do next to advance the Focus. Be concise and strategic."
                        ),
                    ),
                ],
            )

        if name == "consult":
            question = args.get("question", "What should we do?")
            
            # 1. Get Strategic Context
            profile = self.identity.get_profile(self.project_id) or {}
            stack = profile.get("tech_stack", "Unknown Stack")
            stage = profile.get("stage", "Unknown Stage")
            
            # 2. Get Past Decisions (Consistency)
            decisions = self.strategic.list_rejections(self.project_id, limit=3)
            past_decisions = "\n".join([f"- Q: {r['question']} -> A: {r['answer']}" for r in decisions]) if decisions else "None."

            return GetPromptResult(
                description="Strategic Consultation",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Side, I need a CTO-level decision.\n\n"
                                 f"**Question**: \"{question}\"\n\n"
                                 f"**Context**:\n"
                                 f"- **Stage**: {stage}\n"
                                 f"- **Stack**: {stack}\n"
                                 f"- **Precedent** (Last 3 Decisions):\n{past_decisions}\n\n"
                                 f"**Directives**:\n"
                                 f"1. Analyze the trade-offs (Cost, Speed, Debt).\n"
                                 f"2. Check alignment with our Stage (e.g. don't over-engineer for MVP).\n"
                                 f"3. Give a Verdict: **YES/NO/DEFER**.\n"
                                 f"4. Provide a 1-sentence Strategic Rationale."
                        ),
                    ),
                ],
            )

        if name == "verify":
            # 1. Get Security Posture
            # SFO Sprint: Simplified audit summary from forensic store
            findings = self.forensic.get_recent_activities(self.project_id, limit=100)
            crit = len([f for f in findings if f.get('outcome') == 'VIOLATION'])
            high = 0 # Placeholder for severity mapping in ForensicStore
            
            # 2. Get Recent Work
            # Determine what to verify (e.g. files changed recently, though we can't easily get diffs here without git tool)
            # We'll ask the Agent to check Logic and Security.
            
            status = "🔴 BLOCKED" if crit > 0 else ("🟠 RISKY" if high > 0 else "🟢 CLEAR")
            
            return GetPromptResult(
                description="Pre-Flight Verification",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Side, Perform a Pre-Flight Verification.\n\n"
                                 f"**Current Status**: {status}\n"
                                 f"- Critical Issues: {crit}\n"
                                 f"- High Issues: {high}\n\n"
                                 f"**Protocol**:\n"
                                 f"1. Run `audit` on any modified files.\n"
                                 f"2. Verify no 'print' debugging or secrets are left.\n"
                                 f"3. Confirm compliance with the Active Plan.\n"
                                 f"4. Verdict: **SHIP IT** or **BLOCK**."
                        ),
                    ),
                ],
            )

        if name == "check_design":
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
                description="Design System Review",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Side, review this frontend code for Design System compliance.\n\n"
                                 f"**Approved Components**: [{component_list}]\n\n"
                                 f"**Code to Review**:\n```tsx\n{code_snippet}\n```\n\n"
                                 f"**Directives**:\n"
                                 f"1. Identify unauthorized HTML elements (e.g. `button`, `input`) that should be Reusable Components.\n"
                                 f"2. Identify hardcoded CSS/Tailwind that duplicates Design System tokens.\n"
                                 f"3. Rewrite the code to use the Approved Components."
                        ),
                    ),
                ],
            )

        if name == "check_truth":
            # 1. Discover Strategy Docs
            docs_context = ""
            for doc_name in ["README.md", "backend/VISION.md", "docs/MASTER_ROADMAP.md"]:
                doc_path = self.project_path / doc_name
                if doc_path.exists():
                     content = doc_path.read_text()
                     # Extract first 1000 chars to avoid prompt overflow but give enough context
                     docs_context += f"\n--- {doc_name} ---\n{content[:1000]}...\n"
            
            if not docs_context:
                docs_context = "No strategic documentation found (README.md, VISION.md, etc.)."

            return GetPromptResult(
                description="Strategic Reality Check",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Side, Perform a Strategic Reality Check (Truth Engine).\n\n"
                                 f"**Documentation Context**:\n{docs_context}\n\n"
                                 f"**Directives**:\n"
                                 f"1. Identify every 'Feature Claim' or 'Strategic Goal' mentioned in the docs.\n"
                                 f"2. Verify if the code for these features actually exists in the monorepo.\n"
                                 f"3. Identify Omissions (Built but not Doc'd) or Hallucinations (Doc'd but not Built).\n"
                                 f"4. Report 'Documentation Debt' as a list of actionable tasks."
                        ),
                    ),
                ],
            )
            
        if name == "fix-security-critical":
            return GetPromptResult(
                description="Fix Critical Security Issues",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text="Hey Side, list all critical/high security issues. For each one:\n1. Explain the risk.\n2. Propose a code fix.\n3. Apply the fix.\n4. Call `verify_fix` to confirm resolution.\n\nCRITICAL: If `verify_fix` fails, you MUST attempt a different fix and verify again. Do NOT report back until the fix is verified as PASS.",
                        ),
                    ),
                ],
            )
        
        if name == "fix-performance-critical":
            return GetPromptResult(
                description="Fix Critical Performance Issues",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text="Hey Side, identify the top performance bottlenecks. Focus on N+1 queries and expensive loops. optimize them and verify the speedup.",
                        ),
                    ),
                ],
            )
            
        if name == "strategy":
            context = args.get('context', '')
            return GetPromptResult(
                description=f"Strategic advice{f' for {context}' if context else ''}",
                messages=[PromptMessage(role="user", content=TextContent(type="text", text=f"Side, what should I focus on?{f' Context: {context}' if context else ''}"))],
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
