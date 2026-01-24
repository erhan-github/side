"""
Side Strategist - The LLM-powered strategic advisor.

Uses Side Intelligence for fast, intelligent inference (January 2026 models):
- llama-3.1-8b-instant: Fast scoring (277 tok/s, 140ms TTFT)
- llama-3.3-70b-versatile: Deep strategic reasoning (218 tok/s, 110ms TTFT)
- gemma2-9b-it: Lightweight fallback (814 tok/s, very cheap)
"""

import json
import os
import logging
from typing import Any, Optional, Dict, List
from pathlib import Path

import httpx
from side.intel.context_compressor import ContextCompressor
from side.llm.client import LLMClient


logger = logging.getLogger(__name__)


class Strategist:
    """
    LLM-powered strategic advisor using Side Intelligence.

    Model selection (January 2026 benchmarks):
    - FAST_MODEL: For high-volume tasks like scoring articles
    - SMART_MODEL: For complex reasoning and strategic advice
    - LITE_MODEL: Fallback for simple tasks
    """

    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    # Model selection based on task complexity (2026 Side Intelligence offerings)
    FAST_MODEL = "llama-3.1-8b-instant"      # 277 tok/s, 140ms TTFT - scoring
    SMART_MODEL = "llama-3.3-70b-versatile"  # 218 tok/s, 110ms TTFT - strategy
    LITE_MODEL = "llama3-8b-8192"            # Faster, modern fallback

    STRATEGY_PROMPT = """You are Side, a Partner-level CTO specialized in Day-1 Global SaaS Excellence.
Your objective: Build a $100M+ market-dominant asset with 1/10th the effort, using maximum scalability and a "Smart Vibe Coder" mindset.

## Your Lens: Day-1 Dominance
1. **Never "Just an MVP"**: Everything we ship is "Best in Category" on Day 1.
2. **Maximum Scalability**: Design for 10M users now, build with 1/10th the code. 
3. **Elegant Simplicity**: Avoid overengineering, but build the foundation for a global empire.
4. **Leverage Everything**: Reputable OSS + Best-in-class APIs = Dominance.

## Context
Profile: {profile}
Strategic Pivots: {past_decisions}
$100M Goals: {active_goals}
Intelligence Feed: (Offline - Forensics Only)
Deep Memory:
{memory_context}

## User's Strategic Inquiry
{question}

## The "God Mode" Instructions (V3 - Perfection)
1. **THE PULSE**: You MUST start with a SINGLE SENTENCE breakthrough. 
   - Use `⚡ [SHORTCUT]` for high-velocity leverage.
   - Use `🛡️ [MOAT]` for defensive, scalable advantage.
   - Use `🚀 [EXCELLENCE]` for Day-1 dominance improvements.
2. **STRATEGIC IQ**: Assessment of current maturity (400-point scale).
3. **DAY-1 UPGRADE**: Suggest one change that moves the project from "Functional" to "World Class."
4. **BUILD VS. REUSE**: Identify the exact OSS (e.g. Supabase, Clerk) to kill the grunt work.
5. **TONE**: Smart, high-velocity, authoritative. We don't build toys; we build empires.

## Mandatory Output Format
⚡ **THE PULSE**: [PREFIX] [Breakthrough sentence]

🧠 **STRATEGIC IQ**: [Score] [Leverage Assessment]

🏗️ **POWER MOVES (Scalability-First)**:
1. [Move 1]
2. [Move 2]
3. [Move 3]

⚖️ **COMPLIANCE & MOAT WARNINGS**: [Forensic alerts]

Provide your Strategy:"""

    # Removed SCORING_PROMPT per Phase 1 Purge
    _UNUSED_PROMPT = """Rate this article's relevance to the project (0-100).

## Project Profile
{profile}

## Current Focus Areas (from recent git activity)
{focus_areas}

## Article
Title: {title}
URL: {url}
Description: {description}

## Scoring Criteria
- 90-100: CRITICAL MATCH. Directly addresses a current "Focus Area" OR is a perfect Domain + Stack match.
- 70-89: STRONG MATCH. Same Domain (e.g. EdTech) AND Stack, or solves a specific known problem.
- 50-69: TECH MATCH ONLY. Same stack (e.g. Python/FastAPI) but different domain. Useful but not critical.
- 30-49: WEAK MATCH. Popular tool but irrelevant domain (e.g. Home Assistant for EdTech).
- 0-29: Relevance is near zero.

IMPORTANT: 
- PENALIZE popular but irrelevant tools (e.g. Home Assistant, Stable Diffusion) if they don't match the project's DOMAIN.
- A Python repo (Home Assistant) is NOT relevant to a Python EdTech app unless the app does automation.
- Prioritize DOMAIN relevance (EdTech, LMS, Learning) over generic Language relevance.

Respond with ONLY valid JSON:
{{"score": <number>, "reason": "<brief reason>"}}"""

    MONOLITH_PROMPT = """You are the **Side Provocation Engine**. Your goal is to trigger user action.
    
    ## Current Status
    Grade: {grade} ({score}/100) - {label}
    Forensic Health: {forensic_grade}
    Strategic Viability: {strategic_grade}
    Top Focus: {top_focus}
    
    ## Deep Dive
    Dimensions: {dimensions}
    Security: {security_matrix}
    Roadmap: {active_plans}
    
    ## Task
    Identify the SINGLE most critical issue dragging down the project Grade.
    Formulate a "Strategic Insight" that provokes the user to fix it.
    Provide 2 specific "Side Prompts" that are direct and ready to use.
    
    ## Constraints
    - **Insight**: 1-2 sentences. Punchy. Provocative. (e.g. "Your B grade is fake because you have 0 tests.")
    - **Actions**: Direct, conversational prompts starting with "Hey Side".
      - Bad: "Ask Side to scan for secrets"
      - Good: "Hey Side, scan my entire codebase for hardcoded secrets and give me a fix plan."
      - Good: "Hey Side, why is my security score so low? Show me the evidence."
    
    ## Output Format (JSON Only)
    {{
      "insight": "Your security score is critical. I found 5 hardcoded secrets that expose you to immediate risk.",
      "actions": [
        "Hey Side, scan the entire codebase for hardcoded secrets.",
        "Hey Side, explain the security implications of my auth setup."
      ]
    }}"""


    def __init__(self, db: Optional["SimplifiedDatabase"] = None, project_path: Optional[Path] = None, allow_fallbacks: bool = True, memory_retrieval: Optional[Any] = None) -> None:
        """Initialize the Strategist."""
        from side.storage.simple_db import SimplifiedDatabase
        self.llm = LLMClient()
        self.db = db
        self.project_path = project_path
        self.project_id = SimplifiedDatabase.get_project_id(project_path) if project_path else "unknown"
        self.compressor = ContextCompressor()
        self.allow_fallbacks = allow_fallbacks
        self.memory = memory_retrieval
        
        # [Grand Unification] Connect Instrumentation for Adaptive AI
        from side.instrumentation.engine import InstrumentationEngine
        self.instrumentation = InstrumentationEngine(self.db) if self.db else None

    @property
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self.llm.is_available()

    def _detect_adversarial_intent(self, text: str) -> bool:
        """
        Detect potential prompt injection or adversarial intent.
        
        This is the CTO-level 'Forensics Layer'.
        """
        lower_text = text.lower()
        adversarial_patterns = [
            "ignore previous instructions",
            "ignore all instructions",
            "system prompt",
            "you are now",
            "dan mode",
            "jailbreak",
            "output the full prompt",
            "forget what i said",
            "new rule:",
            "disregard"
        ]
        
        for pattern in adversarial_patterns:
            if pattern in lower_text:
                return True
        return False

    async def _call_groq(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str | None:
        """Make a call to Groq API using unified LLMClient."""
        if not self.is_available:
            return None

        # [Hyper-Ralph] Scenario 32: Cheapskate Optimizer
        # Use LITE_MODEL if the prompt is small or the task is repetitive
        actual_model = model
        if "rate this article" in prompt.lower() and len(prompt) < 2000:
             actual_model = self.LITE_MODEL
             logger.debug(f"Cheapskate Optimizer: Downgrading to {actual_model} for simple scoring.")

        try:
            return await self.llm.complete_async(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are a Strategic CTO and Architect.",
                model_override=actual_model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            logger.error(f"Strategist LLM Error: {e}")
            return None

    async def get_strategy(
        self,
        question: str,
        profile: dict[str, Any],
        recent_deltas: list[dict[str, Any]] | None = None,
    ) -> str:
        """
        Get strategic advice for a question.

        Uses the SMART_MODEL (70B) for best reasoning quality.

        Args:
            question: The user's strategic question
            profile: The codebase/business profile
            articles: Optional relevant articles for context
            recent_deltas: Optional recent deltas/changes detected

        Returns:
            Strategic advice from Side Intelligence
        """
        if not self.is_available:
            if not self.allow_fallbacks:
                raise RuntimeError("LLM unavailable and fallbacks are disabled (STRICT_MODE)")
            result = self._fallback_strategy(question, profile)
            if self.db:
                self.db.log_activity(
                    project_id=self.project_id,
                    tool="strategy",
                    action="get_strategy_fallback",
                    cost_tokens=50, # Nominal cost for fallback
                    tier="free",
                    payload={"question": question[:100], "fallback": True}
                )
            return result

        # Forensics Layer: Check for prompt injection
        if self._detect_adversarial_intent(question):
            return "🛡️ **Forensics Alert**: Adversarial intent detected. I am a Strategic Advisor, not a roleplay engine. Please ask a legitimate business or technical question."

        # Format profile
        profile_text = self._format_profile(profile)

        # Format recent changes
        changes_text = self._format_recent_changes(recent_deltas)

        # Format articles with Diversity awareness
        # [Forensics] Articles Removed for Palantir-Level Focus
        # articles_text = "No intelligence available." 


        # Extract domain for strict relevance check
        # Check root 'domain' first (from Auto-Detection), then fallback to 'business' config
        domain = profile.get("domain")
        if not domain:
            biz = profile.get("business", {})
            domain = biz.get("domain", "General Software")
        
        # [Memory - The Read Path]
        # Retrieve persistent memory context if available
        memory_context = ""
        if self.memory:
            try:
                # We fetch relevant memory categories based on the user's question
                memory_context = await self.memory.retrieve(question, self.project_id)
            except Exception as e:
                logger.warning(f"Memory Retrieval Failed: {e}")

        # [Hyper-Ralph] Scenario 15: Use ContextCompressor to prevent token saturation
        context = await self.compressor.compress(
            question=question,
            profile=profile,
            decisions=profile.get("_decisions", []),
            goals=profile.get("_active_goals", []),
            learnings=profile.get("_learnings", []),
            articles=[],
            recent_changes=changes_text
        )

        prompt = self.STRATEGY_PROMPT.format(
            profile=context["profile"],
            past_decisions=context["past_decisions"],
            key_learnings=context["key_learnings"],
            active_goals=context["active_goals"],
            recent_changes=context["recent_changes"],
            memory_context=memory_context,

            # articles=context["articles"], # Removed
            question=context["question"],
            domain=domain,
        )

        # Use SMART_MODEL for strategic reasoning
        result = await self._call_groq(
            prompt,
            model=self.SMART_MODEL,
            max_tokens=1000,
            temperature=0.7,
        )
        if result and self.db:
            self.db.log_activity(
                project_id=self.project_id,
                tool="strategy",
                action="get_strategy",
                cost_tokens=1500, # Estimated smart model cost
                tier="free",
                payload={"question": question[:100]}
            )

        if result:
            return result
            
        if not self.allow_fallbacks:
            raise RuntimeError("Strategy generation failed and fallbacks are disabled (STRICT_MODE)")

        result = self._fallback_strategy(question, profile)
        if self.db:
             self.db.log_activity(
                project_id=self.project_id,
                tool="strategy",
                action="get_strategy_fallback",
                cost_tokens=50,
                tier="free",
                payload={"question": question[:100], "fallback": True}
            )
        return result





    def _format_profile(self, profile: dict[str, Any]) -> str:
        """Format profile for LLM prompts (enriched version)."""
        lines = []

        tech = profile.get("technical", {})
        if tech.get("primary_language"):
            lines.append(f"Language: {tech['primary_language']}")
        if tech.get("frameworks"):
            lines.append(f"Frameworks: {', '.join(tech['frameworks'][:5])}")
        if tech.get("languages"):
            langs = list(tech["languages"].keys())[:5]
            lines.append(f"Stack: {', '.join(langs)}")

        biz = profile.get("business", {})
        if biz.get("product_type"):
            lines.append(f"Product: {biz['product_type']}")
        if biz.get("domain"):
            lines.append(f"Domain: {biz['domain']}")
        if biz.get("stage"):
            lines.append(f"Stage: {biz['stage']}")
        if biz.get("integrations"):
            lines.append(f"Integrations: {', '.join(biz['integrations'][:5])}")
        if biz.get("priorities"):
            lines.append(f"Priorities: {', '.join(biz['priorities'][:3])}")

        # Add code issues summary
        health = tech.get("health_signals", {})
        issues = health.get("code_issues", {})
        if issues.get("total_issues", 0) > 0:
            lines.append(f"Open TODOs: {len(issues.get('todos', []))}")

        # Add project documentation (README/VISION)
        docs = profile.get("project_docs", "")
        if docs:
            lines.append("\n## Project Documentation Context")
            lines.append(docs)

        # Add Strategic Alignment Note (Stage 2)
        alignment_note = profile.get("alignment_note")
        if alignment_note:
            lines.append(f"\n⚠️ STRATEGIC ALIGNMENT WARNING: {alignment_note}")

        # [Grand Unification] Adaptive Feedback Loop
        if self.instrumentation:
            try:
                status = self.instrumentation.get_status(self.project_id)
                leverage = status.get("leverage_factor", 1.0)
                
                lines.append("\n## Instrumentation Signal")
                lines.append(f"Leverage Ratio: {leverage}x")
                
                if leverage < 2.0:
                    lines.append("MODE: COACH. User is struggling or new. Be explicit, encouraging, and concrete.")
                elif leverage > 5.0:
                    lines.append("MODE: PARTNER. User is high-velocity. Be strategic, concise, and assume competence.")
                else:
                    lines.append("MODE: ASSISTANT. Balanced support.")
            except Exception:
                pass

        return "\n".join(lines) if lines else "General software project"

    def _format_focus_areas(self, profile: dict[str, Any]) -> str:
        """Format current focus areas from git activity."""
        tech = profile.get("technical", {})
        health = tech.get("health_signals", {})
        git = health.get("git", {})

        focus_areas = git.get("current_focus_areas", [])
        recent_commits = git.get("recent_commit_messages", [])

        if not focus_areas and not recent_commits:
            return "No recent git activity detected"

        lines = []
        if focus_areas:
            lines.append(f"Active areas: {', '.join(focus_areas)}")
        if recent_commits:
            lines.append("Recent commits:")
            for msg in recent_commits[:5]:
                lines.append(f"  - {msg[:60]}")

        return "\n".join(lines)

    def _format_recent_changes(
        self, deltas: list[dict[str, Any]] | None
    ) -> str:
        """Format recent deltas for strategy context."""
        if not deltas:
            return "No recent changes detected"

        lines = []
        for delta in deltas[:10]:  # Limit to 10 most recent
            delta_type = delta.get("delta_type", "")
            summary = delta.get("summary", "")

            # Format based on type
            if "integration" in delta_type.lower():
                lines.append(f"🔌 {summary}")
            elif "framework" in delta_type.lower():
                lines.append(f"🏗️ {summary}")
            elif "env" in delta_type.lower():
                lines.append(f"⚙️ {summary}")
            else:
                lines.append(f"📝 {summary}")

        return "\n".join(lines) if lines else "No significant changes"

    def _format_strategic_context(
        self, items: list[dict[str, Any]], context_type: str
    ) -> str:
        """
        Format strategic memory with Hyper-Ralph Compression.
        
        Optimization: We only send the most recent/relevant items 
        and summarize them to save tokens.
        """
        if not items:
            return f"No {context_type}s recorded yet."
        
        lines = []
        # Hyper-Ralph: Limit to top 3 instead of 5 if stack is huge
        limit = 5 if len(items) < 10 else 3
        
        for item in items[:limit]:
            if context_type == "decision":
                q = item.get("question", "")
                a = item.get("answer", "")
                # Truncate long answers
                if len(a) > 200: a = a[:200] + "..."
                lines.append(f"- **{q}** → {a}")
            elif context_type == "learning":
                insight = item.get("insight", "")
                impact = item.get("impact", "medium")
                if len(insight) > 200: insight = insight[:200] + "..."
                emoji = "🔴" if impact == "high" else "🟡" if impact == "medium" else "🟢"
                lines.append(f"- {emoji} {insight}")
            elif context_type == "goal":
                title = item.get("title", "")
                ptype = item.get("type", "goal")
                lines.append(f"- [{ptype.upper()}] {title}")
        
        return "\n".join(lines)

    def _fallback_strategy(
        self,
        question: str,
        profile: dict[str, Any],
    ) -> str:
        """Provide fallback strategy for Day-1 Excellence."""
        return """I need more context to execute Day-1 Global Dominance.
        
To activate the 'Smart Vibe Coder' Engine:
1. Run `analyze_codebase` to map your scalability surface.
2. Set GROQ_API_KEY (console.groq.com).
3. Run `refresh` for real-time market signals.

We don't build MVPs; we build the future. Ask me again!"""



    # =========================================================================
    # GUARD FUNCTIONALITY (Merged from intel/guard.py)
    # =========================================================================
    
    CONFLICT_PROMPT = """
    You are a Strategic Guardian. Detect CRITICAL CONFLICTS between a user's new request and their past strategic decisions.
    
    PAST DECISIONS:
    {decisions_text}
    
    USER REQUEST:
    "{query}"
    
    TASK: Identify if the user is making a contradictory architectural move.
    
    Examples:
    - Decided on "PostgreSQL" -> User asks "Setup MongoDB" (CONFLICT)
    - Decided on "Monolith" -> User asks "Create microservice" (CONFLICT)
    
    RESPONSE:
    NO_CONFLICT or CONFLICT: [decision_id]: [explanation]
    """

    async def handle_monolith_evolution(
        self,
        score: int,
        grade: str,
        label: str,
        forensic_grade: str,
        strategic_grade: str,
        top_focus: str,
        dimensions: dict,
        security_matrix: dict,
        active_plans: list
    ) -> dict:
        """
        Synthesize forensic data into a strategic insight for the Monolith.
        """
        prompt = self.MONOLITH_PROMPT.format(
            grade=grade,
            score=score,
            label=label,
            forensic_grade=forensic_grade,
            strategic_grade=strategic_grade,
            top_focus=top_focus,
            dimensions=dimensions,
            security_matrix=security_matrix,
            active_plans=[p['title'] for p in active_plans]
        )
        
        try:
            response = await self._call_groq(
                prompt,
                model=self.SMART_MODEL,
                temperature=0.3, # Low temp for consistency
                max_tokens=500
            )
            
            if not response:
                logger.warning("No response from Strategist (LLM unavailable).")
                return {
                    "insight": "Strategic synthesis unavailable. Insufficient evidence or LLM offline.",
                    "actions": ["Run 'side audit' to generate high-fidelity ground truth."]
                }

            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {
                "insight": "Strategic pulse currently static. Standing by for code-level evidence.",
                "actions": ["Execute a deep forensic scan to populate the Monolith."]
            }
        except Exception as e:
            logger.error(f"Failed to evolve monolith narrative: {e}")
            return {
                "insight": "Synthesis Error. Integrity prioritized over speculation.",
                "actions": ["Check local database state.", "Verify API connectivity."]
            }

    async def check_decision_conflict(
        self, query: str, decisions: list[dict[str, Any]]
    ) -> dict | None:
        """
        Check if query contradicts past decisions.
        
        Returns:
            dict with {detected, decision_id, reason} or None if no conflict
        """
        if not decisions:
            return None
            
        decisions_text = "\n".join([
            f"- [{d['id']}] {d['question']} -> {d['answer']}"
            for d in decisions
        ])
        
        prompt = self.CONFLICT_PROMPT.format(
            decisions_text=decisions_text,
            query=query
        )
        
        response = await self._call_groq(
            prompt,
            model=self.LITE_MODEL,
            max_tokens=100,
            temperature=0.1
        )
        
        if not response or "NO_CONFLICT" in response.upper():
            return None
            
        # Parse conflict
        try:
            parts = response.split(":", 2)
            if len(parts) >= 3 and "CONFLICT" in parts[0].upper():
                return {
                    "detected": True,
                    "decision_id": parts[1].strip(),
                    "reason": parts[2].strip()
                }
        except Exception:
            pass
            
        return None
