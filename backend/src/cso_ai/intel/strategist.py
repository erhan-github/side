"""
CSO.ai Strategist - The LLM-powered strategic advisor.

Uses Groq for fast, intelligent inference (January 2026 models):
- llama-3.1-8b-instant: Fast scoring (277 tok/s, 140ms TTFT)
- llama-3.3-70b-versatile: Deep strategic reasoning (218 tok/s, 110ms TTFT)
- gemma2-9b-it: Lightweight fallback (814 tok/s, very cheap)
"""

import json
import os
from typing import Any

import httpx
from cso_ai.intel.context_compressor import ContextCompressor


class Strategist:
    """
    LLM-powered strategic advisor using Groq.

    Model selection (January 2026 benchmarks):
    - FAST_MODEL: For high-volume tasks like scoring articles
    - SMART_MODEL: For complex reasoning and strategic advice
    - LITE_MODEL: Fallback for simple tasks
    """

    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    # Model selection based on task complexity (2026 Groq offerings)
    FAST_MODEL = "llama-3.1-8b-instant"      # 277 tok/s, 140ms TTFT - scoring
    SMART_MODEL = "llama-3.3-70b-versatile"  # 218 tok/s, 110ms TTFT - strategy
    LITE_MODEL = "gemma2-9b-it"              # 814 tok/s, ultra-cheap - fallback

    STRATEGY_PROMPT = """You are CSO.ai, a Partner-level CTO specialized in Day-1 Global SaaS Excellence.
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
Intelligence Feed: {articles}

## User's Strategic Inquiry
{question}

## The "God Mode" Instructions (V3 - Perfection)
1. **THE PULSE**: You MUST start with a SINGLE SENTENCE breakthrough. 
   - Use `⚡ [SHORTCUT]` for high-velocity leverage.
   - Use `🛡️ [MOAT]` for defensive, scalable advantage.
   - Use `🚀 [EXCELLENCE]` for Day-1 dominance improvements.
2. **STRATEGIC IQ**: Assessment of current maturity (0-160 scale).
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

    SCORING_PROMPT = """Rate this article's relevance to the project (0-100).

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



    def __init__(self) -> None:
        """Initialize the Strategist."""
        self._api_key = os.environ.get("GROQ_API_KEY")
        self.compressor = ContextCompressor()

    @property
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self._api_key is not None

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
        """Make a call to Groq API."""
        if not self.is_available:
            return None

        if len(prompt) > 40000:
             logger.warning(f"Extremely large prompt detected ({len(prompt)} chars). Truncating context.")
             prompt = prompt[:40000] + "\n[CONTEXT TRUNCATED FOR ECONOMY]"

        # [Hyper-Ralph] Scenario 32: Cheapskate Optimizer
        # Use LITE_MODEL if the prompt is small or the task is repetitive
        actual_model = model
        if "rate this article" in prompt.lower() and len(prompt) < 2000:
             actual_model = self.LITE_MODEL
             logger.debug(f"Cheapskate Optimizer: Downgrading to {actual_model} for simple scoring.")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": actual_model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    self.GROQ_API_URL,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return None

    async def get_strategy(
        self,
        question: str,
        profile: dict[str, Any],
        articles: list[dict[str, Any]] | None = None,
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
            Strategic advice from Groq
        """
        if not self.is_available:
            return self._fallback_strategy(question, profile)

        # Forensics Layer: Check for prompt injection
        if self._detect_adversarial_intent(question):
            return "🛡️ **Forensics Alert**: Adversarial intent detected. I am a Strategic Advisor, not a roleplay engine. Please ask a legitimate business or technical question."

        # Format profile
        profile_text = self._format_profile(profile)

        # Format recent changes
        changes_text = self._format_recent_changes(recent_deltas)

        # Format articles with Diversity awareness
        articles_text = "No intelligence available."
        if articles:
            lines = []
            for a in articles[:10]: # Process top 10 diverse items
                domain = a.get("domain", "tech").lower()
                emoji = "📝"
                if "legal" in domain: emoji = "⚖️"
                elif "invest" in domain: emoji = "💰"
                
                title = a.get("title", "Untitled")
                desc = a.get("description", "") or ""
                lines.append(f"- {emoji} [{domain.upper()}] {title}: {desc[:150]}...")
            articles_text = "\n".join(lines)

        # Extract domain for strict relevance check
        # Check root 'domain' first (from Auto-Detection), then fallback to 'business' config
        domain = profile.get("domain")
        if not domain:
            biz = profile.get("business", {})
            domain = biz.get("domain", "General Software")
        
        # [Hyper-Ralph] Scenario 15: Use ContextCompressor to prevent token saturation
        context = self.compressor.compress(
            question=question,
            profile=profile,
            decisions=profile.get("_decisions", []),
            goals=profile.get("_active_goals", []),
            learnings=profile.get("_learnings", []),
            articles=articles or [],
            recent_changes=changes_text
        )

        prompt = self.STRATEGY_PROMPT.format(
            profile=context["profile"],
            past_decisions=context["past_decisions"],
            key_learnings=context["key_learnings"],
            active_goals=context["active_goals"],
            recent_changes=context["recent_changes"],
            articles=context["articles"],
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
        if result:
            return result
        return self._fallback_strategy(question, profile)

    async def batch_score_articles(
        self,
        articles_data: list[dict[str, Any]],
        profile: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        [Hyper-Ralph] Scenario 36 Fix: Batch Article Scoring.
        Processes up to 10 articles in a single request to save tokens and time.
        """
        if not articles_data:
            return []

        # We take only a slice to avoid context overflow
        batch = articles_data[:10]
        
        # Prepare content string
        articles_str = ""
        for i, a in enumerate(batch):
            articles_str += f"\nArticle {i+1}:\nTitle: {a.get('title')}\nURL: {a.get('url')}\nDescription: {a.get('description')}\n"

        prompt = f"""Rate these articles' relevance to the project (0-100).
        
        ## Project Profile
        {self._format_profile(profile)}
        
        ## Articles to Score
        {articles_str}
        
        {self.SCORING_PROMPT}"""
        
        result = await self._call_groq(prompt, model=self.FAST_MODEL)
        if not result:
            return [{"url": a["url"], "score": 50, "reason": "No response"} for a in batch]
        
        try:
            # Extract JSON block
            import re
            match = re.search(r"(\[.*\])", result, re.DOTALL)
            if match:
                scores = json.loads(match.group(1))
                return scores
            return [{"url": a["url"], "score": 50, "reason": "Invalid JSON"} for a in batch]
        except Exception as e:
            logger.error(f"Failed to parse batch scores: {e}")
            return [{"url": a["url"], "score": 40, "reason": "Parse error"} for a in batch]

    async def score_article(
        self,
        title: str,
        url: str,
        description: str | None,
        profile: dict[str, Any],
    ) -> tuple[float, str]:
        """
        Score an article's relevance using LLM.

        Uses the FAST_MODEL (8B) for speed on high-volume scoring.
        Includes current focus areas from git activity for better relevance.

        Args:
            title: Article title
            url: Article URL
            description: Article description
            profile: Codebase profile

        Returns:
            Tuple of (score 0-100, reasoning)
        """
        if not self.is_available:
            return self._heuristic_score(title, description, profile)

        profile_text = self._format_profile(profile)
        focus_areas = self._format_focus_areas(profile)

        prompt = self.SCORING_PROMPT.format(
            profile=profile_text,
            focus_areas=focus_areas,
            title=title,
            url=url,
            description=description or "No description",
        )

        # Use FAST_MODEL for high-volume scoring
        result = await self._call_groq(
            prompt,
            model=self.FAST_MODEL,
            max_tokens=100,
            temperature=0.3,
        )
        if result:
            try:
                # Clean up response - sometimes LLM adds extra text
                result = result.strip()
                # Handle markdown code blocks
                if "```" in result:
                    # Extract JSON from code block
                    start = result.find("{")
                    end = result.rfind("}") + 1
                    if start != -1 and end > start:
                        result = result[start:end]
                data = json.loads(result)
                return float(data.get("score", 50)), data.get("reason", "")
            except (json.JSONDecodeError, ValueError):
                pass

        return self._heuristic_score(title, description, profile)

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

    def _heuristic_score(
        self,
        title: str,
        description: str | None,
        profile: dict[str, Any],
    ) -> tuple[float, str]:
        """Score article using heuristics when LLM unavailable."""
        score = 30.0
        reasons = []

        text = f"{title} {description or ''}".lower()

        # Check for current focus areas (highest priority!)
        tech = profile.get("technical", {})
        health = tech.get("health_signals", {})
        git = health.get("git", {})
        focus_areas = git.get("current_focus_areas", [])

        for area in focus_areas:
            if area.lower() in text:
                score += 30  # Big boost for current focus
                reasons.append(f"matches current focus: {area}")
                break

        # Check for stack matches
        lang = tech.get("primary_language", "").lower()
        if lang and lang in text:
            score += 15  # Reduced from 20 - Language alone isn't enough
            reasons.append(f"mentions {lang}")

        frameworks = tech.get("frameworks", [])
        for fw in frameworks:
            if fw.lower() in text:
                score += 15
                reasons.append(f"about {fw}")
                break

        # Domain match - HIGHER PRIORITY
        biz = profile.get("business", {})
        domain = biz.get("domain", "").lower()
        if domain:
            domain_words = domain.replace("/", " ").replace("-", " ").split()
            for word in domain_words:
                if len(word) > 3 and word in text:
                    score += 35  # Increased from 15 - Domain is critical
                    reasons.append(f"relevant to {domain}")
                    break

        # Integration matches
        integrations = biz.get("integrations", [])
        for integration in integrations:
            if integration.lower() in text:
                score += 20
                reasons.append(f"about {integration}")
                break

        score = min(100.0, score)
        reason = ", ".join(reasons) if reasons else "General tech content"
        return score, reason
