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

    STRATEGY_PROMPT = """You are CSO.ai, an AI Chief Strategy Officer for a software project.

## Your Role
You are a strategic advisor who deeply understands the user's codebase, business, and market. 
You provide actionable, specific advice - not generic platitudes.

## The User's Profile
{profile}

## Recent Changes (Last 7 Days)
{recent_changes}

## Recent Relevant Articles
{articles}

## User's Question
{question}

## Instructions
1. Answer based on the specific context of their project
2. Consider recent changes when giving advice - the project state may have evolved
3. Reference relevant articles when applicable
4. Be direct and actionable - give 3-5 specific recommendations
5. Think like a real CSO - what would you actually recommend?
6. If you don't have enough information, say so
7. Keep your response focused and under 500 words

Provide your strategic advice:"""

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
- 90-100: Directly about current focus area or exact tech stack match
- 70-89: Related to tech stack or business domain
- 50-69: Adjacent technology, generally useful
- 30-49: Tangentially related
- 0-29: Not relevant

IMPORTANT: Prioritize articles matching "Current Focus Areas" - these are what the developer is actively working on.

Respond with ONLY valid JSON:
{{"score": <number>, "reason": "<brief reason>"}}"""

    def __init__(self) -> None:
        """Initialize the Strategist."""
        self._api_key = os.environ.get("GROQ_API_KEY")

    @property
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self._api_key is not None

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

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.GROQ_API_URL,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            # Try fallback model on error
            if model != self.LITE_MODEL:
                return await self._call_groq(prompt, self.LITE_MODEL, max_tokens, temperature)
            print(f"Groq API error: {e}")
            return None
        except Exception as e:
            print(f"Groq API error: {e}")
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

        # Format profile
        profile_text = self._format_profile(profile)

        # Format recent changes
        changes_text = self._format_recent_changes(recent_deltas)

        # Format articles
        articles_text = "No articles available."
        if articles:
            articles_text = "\n".join([
                f"- {a.get('title', 'Untitled')}: {a.get('relevance_reason', '')}"
                for a in articles[:5]
            ])

        prompt = self.STRATEGY_PROMPT.format(
            profile=profile_text,
            recent_changes=changes_text,
            articles=articles_text,
            question=question,
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

    def _fallback_strategy(
        self,
        question: str,
        profile: dict[str, Any],
    ) -> str:
        """Provide fallback strategy without LLM."""
        biz = profile.get("business", {})
        stage = biz.get("stage", "unknown")

        advice_by_stage = {
            "mvp": """Based on your MVP stage:

1. **Focus on validation** - Don't build more until you've validated core assumptions
2. **Talk to users** - 10+ conversations this week
3. **Measure one thing** - Pick your North Star metric
4. **Ship fast** - Speed of learning > perfection

💡 Set GROQ_API_KEY for personalized strategic advice.
   Free at: https://console.groq.com/keys""",

            "early": """Based on your early stage:

1. **Find PMF** - Product-market fit is everything
2. **Retention > Acquisition** - Keep users before getting more
3. **Double down on what works** - Kill what doesn't
4. **Start thinking about revenue** - Even $1 proves value

💡 Set GROQ_API_KEY for personalized strategic advice.
   Free at: https://console.groq.com/keys""",

            "growth": """Based on your growth stage:

1. **Scale systematically** - Document what works
2. **Invest in infrastructure** - Monitoring, observability
3. **Build the team** - You can't do it alone
4. **Watch unit economics** - Growth should be efficient

💡 Set GROQ_API_KEY for personalized strategic advice.
   Free at: https://console.groq.com/keys""",
        }

        return advice_by_stage.get(stage, """I need more context to provide strategic advice.

To enable full strategic intelligence:
1. Run `analyze_codebase` on your project
2. Set GROQ_API_KEY (free at console.groq.com)
3. Run `refresh` to gather market intelligence

Then ask me again!""")

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
            score += 20
            reasons.append(f"mentions {lang}")

        frameworks = tech.get("frameworks", [])
        for fw in frameworks:
            if fw.lower() in text:
                score += 15
                reasons.append(f"about {fw}")
                break

        # Domain match
        biz = profile.get("business", {})
        domain = biz.get("domain", "").lower()
        if domain:
            domain_words = domain.replace("/", " ").replace("-", " ").split()
            for word in domain_words:
                if len(word) > 3 and word in text:
                    score += 15
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
