"""
CSO.ai Advisor - The recommendation layer.

The Advisor synthesizes everything and provides:
- Actionable recommendations
- Prioritized next steps
- Strategic guidance
- Relevant external content

It's the voice of CSO.ai that users interact with.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from cso_ai.core.anticipator import Insight, InsightPriority, InsightType
from cso_ai.core.understander import IntelligenceProfile


@dataclass
class Recommendation:
    """A strategic recommendation from CSO.ai."""

    title: str
    summary: str
    details: str
    priority: InsightPriority
    category: str  # tech, business, market, financial, legal
    actions: list[str] = field(default_factory=list)
    resources: list[dict[str, str]] = field(default_factory=list)  # {title, url}
    confidence: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        """Serialize recommendation."""
        return {
            "title": self.title,
            "summary": self.summary,
            "details": self.details,
            "priority": self.priority.value,
            "category": self.category,
            "actions": self.actions,
            "resources": self.resources,
            "confidence": self.confidence,
        }


@dataclass
class StrategicBrief:
    """A comprehensive strategic brief from CSO.ai."""

    profile_summary: str
    key_insights: list[Insight]
    recommendations: list[Recommendation]
    risks: list[str]
    opportunities: list[str]
    next_steps: list[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Serialize brief."""
        return {
            "profile_summary": self.profile_summary,
            "key_insights": [i.to_dict() for i in self.key_insights],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "risks": self.risks,
            "opportunities": self.opportunities,
            "next_steps": self.next_steps,
            "generated_at": self.generated_at.isoformat(),
        }


class Advisor:
    """
    The recommendation layer of CSO.ai.

    Responsibilities:
    - Synthesize intelligence into recommendations
    - Prioritize what matters most right now
    - Surface relevant external content
    - Provide strategic guidance

    The Advisor is how CSO.ai communicates with users.
    """

    def __init__(self) -> None:
        """Initialize the Advisor."""
        self._recommendations: list[Recommendation] = []

    async def generate_brief(
        self,
        profile: IntelligenceProfile,
        insights: list[Insight],
    ) -> StrategicBrief:
        """
        Generate a comprehensive strategic brief.

        Args:
            profile: Current intelligence profile
            insights: List of insights from Anticipator

        Returns:
            Complete StrategicBrief
        """
        # Generate profile summary
        summary = await self._summarize_profile(profile)

        # Convert insights to recommendations
        recommendations = await self._insights_to_recommendations(insights)

        # Extract risks and opportunities
        risks = [i.title for i in insights if i.type == InsightType.RISK]
        opportunities = [i.title for i in insights if i.type == InsightType.OPPORTUNITY]

        # Generate next steps
        next_steps = await self._prioritize_actions(recommendations)

        return StrategicBrief(
            profile_summary=summary,
            key_insights=insights[:5],  # Top 5
            recommendations=recommendations,
            risks=risks,
            opportunities=opportunities,
            next_steps=next_steps,
        )

    async def _summarize_profile(self, profile: IntelligenceProfile) -> str:
        """Generate a human-readable profile summary."""
        tech = profile.technical
        biz = profile.business

        parts = []

        # Technical summary
        if tech.primary_language:
            parts.append(f"Primary language: {tech.primary_language}")
        if tech.frameworks:
            parts.append(f"Frameworks: {', '.join(tech.frameworks)}")

        # Business summary
        if biz.product_type:
            parts.append(f"Product type: {biz.product_type}")
        if biz.stage:
            parts.append(f"Stage: {biz.stage}")
        if biz.domain:
            parts.append(f"Domain: {biz.domain}")

        if not parts:
            return "Profile is still being built. Run analyze_codebase for deeper understanding."

        return " | ".join(parts)

    async def _insights_to_recommendations(
        self,
        insights: list[Insight],
    ) -> list[Recommendation]:
        """Convert insights into actionable recommendations."""
        recommendations = []

        for insight in insights:
            rec = Recommendation(
                title=insight.title,
                summary=insight.description,
                details=insight.reasoning,
                priority=insight.priority,
                category=insight.related_to[0] if insight.related_to else "general",
                actions=insight.actions,
                confidence=insight.confidence,
            )
            recommendations.append(rec)

        # Sort by priority
        priority_order = {
            InsightPriority.CRITICAL: 0,
            InsightPriority.HIGH: 1,
            InsightPriority.MEDIUM: 2,
            InsightPriority.LOW: 3,
        }
        recommendations.sort(key=lambda r: priority_order[r.priority])

        return recommendations

    async def _prioritize_actions(
        self,
        recommendations: list[Recommendation],
    ) -> list[str]:
        """Extract and prioritize top actions across all recommendations."""
        all_actions = []

        for rec in recommendations:
            for action in rec.actions:
                all_actions.append((action, rec.priority))

        # Sort by priority
        priority_order = {
            InsightPriority.CRITICAL: 0,
            InsightPriority.HIGH: 1,
            InsightPriority.MEDIUM: 2,
            InsightPriority.LOW: 3,
        }
        all_actions.sort(key=lambda x: priority_order[x[1]])

        # Return top actions
        return [action for action, _ in all_actions[:5]]

    async def get_relevant_content(
        self,
        profile: IntelligenceProfile,
        topic: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get relevant external content for the profile.

        Args:
            profile: Intelligence profile
            topic: Optional specific topic

        Returns:
            List of relevant content items
        """
        # TODO: Implement in Phase 5
        # - Fetch from sources
        # - Score relevance
        # - Filter and rank
        return []

    async def evaluate_content(
        self,
        url: str,
        profile: IntelligenceProfile,
    ) -> dict[str, Any]:
        """
        Evaluate if a piece of content is worth consuming.

        Args:
            url: URL to evaluate
            profile: Intelligence profile for context

        Returns:
            Evaluation with score and reasoning
        """
        # TODO: Implement in Phase 5
        return {
            "url": url,
            "score": 0,
            "reasoning": "Content evaluation coming in Phase 5",
            "worth_reading": False,
        }
