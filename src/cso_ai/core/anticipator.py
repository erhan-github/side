"""
CSO.ai Anticipator - The prediction layer.

The Anticipator looks at patterns and predicts:
- What the user might need next
- Risks that are emerging
- Opportunities that are appearing
- Timing for strategic moves

It's the proactive brain of CSO.ai.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from cso_ai.core.understander import IntelligenceProfile


class InsightType(Enum):
    """Types of insights CSO.ai can surface."""

    RISK = "risk"
    OPPORTUNITY = "opportunity"
    RECOMMENDATION = "recommendation"
    WARNING = "warning"
    TREND = "trend"
    ACTION = "action"


class InsightPriority(Enum):
    """Priority levels for insights."""

    CRITICAL = "critical"  # Needs immediate attention
    HIGH = "high"  # Should address soon
    MEDIUM = "medium"  # Worth knowing
    LOW = "low"  # FYI


@dataclass
class Insight:
    """A proactive insight from CSO.ai."""

    type: InsightType
    priority: InsightPriority
    title: str
    description: str
    reasoning: str
    actions: list[str] = field(default_factory=list)
    related_to: list[str] = field(default_factory=list)  # areas: tech, business, etc.
    confidence: float = 0.5  # 0-1 how confident we are
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None  # Some insights are time-sensitive

    def to_dict(self) -> dict[str, Any]:
        """Serialize insight."""
        return {
            "type": self.type.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "reasoning": self.reasoning,
            "actions": self.actions,
            "related_to": self.related_to,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class Anticipator:
    """
    The prediction layer of CSO.ai.

    Responsibilities:
    - Pattern matching across intelligence
    - Risk detection and early warning
    - Opportunity identification
    - Strategic timing recommendations
    - Proactive insight generation

    The Anticipator sees what's coming before you ask.
    """

    def __init__(self) -> None:
        """Initialize the Anticipator."""
        self.insights: list[Insight] = []
        self._patterns: list[dict[str, Any]] = []

    async def analyze_profile(
        self,
        profile: IntelligenceProfile,
    ) -> list[Insight]:
        """
        Analyze a profile and generate proactive insights.

        Args:
            profile: Intelligence profile to analyze

        Returns:
            List of insights
        """
        insights = []

        # Run pattern matchers
        insights.extend(await self._detect_technical_risks(profile))
        insights.extend(await self._detect_business_opportunities(profile))
        insights.extend(await self._detect_timing_signals(profile))
        insights.extend(await self._detect_missing_pieces(profile))
        insights.extend(await self._detect_growth_opportunities(profile))

        # Store and return
        self.insights.extend(insights)
        return insights

    async def analyze_from_dict(self, profile_dict: dict[str, Any]) -> list[Insight]:
        """
        Analyze a profile dictionary and generate insights.

        Args:
            profile_dict: Profile as dictionary (from database)

        Returns:
            List of insights
        """
        insights = []

        tech = profile_dict.get("technical", {})
        biz = profile_dict.get("business", {})
        health = tech.get("health_signals", {})

        # Technical Risks
        insights.extend(self._check_missing_tests(health))
        insights.extend(self._check_missing_ci(health))
        insights.extend(self._check_code_issues(health))
        insights.extend(self._check_missing_license(health))

        # Business Opportunities
        insights.extend(self._check_stage_opportunities(biz))
        insights.extend(self._check_integration_opportunities(biz, tech))

        # Git Activity
        insights.extend(self._check_git_activity(health))

        self.insights.extend(insights)
        return insights

    def _check_missing_tests(self, health: dict[str, Any]) -> list[Insight]:
        """Check for missing tests."""
        if not health.get("has_tests"):
            return [
                Insight(
                    type=InsightType.RISK,
                    priority=InsightPriority.HIGH,
                    title="No tests detected",
                    description="Your codebase doesn't appear to have a test directory.",
                    reasoning="Tests are critical for maintainability and confidence in changes.",
                    actions=[
                        "Add pytest (Python) or Jest (JS/TS)",
                        "Start with critical path tests",
                        "Aim for 70%+ coverage on core logic",
                    ],
                    related_to=["technical", "quality"],
                    confidence=0.8,
                )
            ]
        return []

    def _check_missing_ci(self, health: dict[str, Any]) -> list[Insight]:
        """Check for missing CI/CD."""
        if not health.get("has_ci"):
            return [
                Insight(
                    type=InsightType.RECOMMENDATION,
                    priority=InsightPriority.MEDIUM,
                    title="No CI/CD pipeline detected",
                    description="Consider adding continuous integration for automated testing.",
                    reasoning="CI catches bugs early and ensures code quality on every commit.",
                    actions=[
                        "Add GitHub Actions workflow",
                        "Run tests on every PR",
                        "Add linting and type checking",
                    ],
                    related_to=["technical", "devops"],
                    confidence=0.8,
                )
            ]
        return []

    def _check_code_issues(self, health: dict[str, Any]) -> list[Insight]:
        """Check for code issues (TODOs, FIXMEs)."""
        issues = health.get("code_issues", {})
        total = issues.get("total_issues", 0)

        insights = []

        if total > 20:
            insights.append(
                Insight(
                    type=InsightType.WARNING,
                    priority=InsightPriority.MEDIUM,
                    title=f"High technical debt: {total} code issues",
                    description=f"Found {len(issues.get('todos', []))} TODOs, {len(issues.get('fixmes', []))} FIXMEs, {len(issues.get('hacks', []))} HACKs.",
                    reasoning="Accumulated TODOs and FIXMEs indicate technical debt that slows development.",
                    actions=[
                        "Schedule a tech debt sprint",
                        "Prioritize FIXMEs over TODOs",
                        "Address HACKs before they become permanent",
                    ],
                    related_to=["technical", "quality"],
                    confidence=0.7,
                )
            )

        fixmes = issues.get("fixmes", [])
        if len(fixmes) > 5:
            insights.append(
                Insight(
                    type=InsightType.RISK,
                    priority=InsightPriority.HIGH,
                    title=f"{len(fixmes)} FIXMEs need attention",
                    description="FIXMEs typically indicate bugs or critical issues that need fixing.",
                    reasoning="Unlike TODOs, FIXMEs often indicate broken or problematic code.",
                    actions=[
                        "Review each FIXME this week",
                        "Convert to issues/tickets",
                        "Prioritize based on impact",
                    ],
                    related_to=["technical", "bugs"],
                    confidence=0.8,
                )
            )

        return insights

    def _check_missing_license(self, health: dict[str, Any]) -> list[Insight]:
        """Check for missing license."""
        if not health.get("has_license"):
            return [
                Insight(
                    type=InsightType.RECOMMENDATION,
                    priority=InsightPriority.LOW,
                    title="No LICENSE file detected",
                    description="Consider adding a license if you plan to open source.",
                    reasoning="A license clarifies how others can use your code.",
                    actions=[
                        "MIT for permissive open source",
                        "Apache 2.0 for patent protection",
                        "Keep proprietary if not open sourcing",
                    ],
                    related_to=["legal"],
                    confidence=0.6,
                )
            ]
        return []

    def _check_stage_opportunities(self, biz: dict[str, Any]) -> list[Insight]:
        """Check for stage-specific opportunities."""
        stage = biz.get("stage")
        insights = []

        if stage == "mvp":
            insights.append(
                Insight(
                    type=InsightType.OPPORTUNITY,
                    priority=InsightPriority.HIGH,
                    title="MVP stage: Focus on validation",
                    description="At MVP stage, speed of learning matters more than perfection.",
                    reasoning="Validate your core assumptions before investing in scale.",
                    actions=[
                        "Talk to 10+ potential users this week",
                        "Measure one key metric",
                        "Ship fast, iterate faster",
                    ],
                    related_to=["business", "growth"],
                    confidence=0.7,
                )
            )
        elif stage == "early":
            insights.append(
                Insight(
                    type=InsightType.OPPORTUNITY,
                    priority=InsightPriority.HIGH,
                    title="Early stage: Time to find PMF",
                    description="Focus on product-market fit before scaling.",
                    reasoning="Scaling without PMF wastes resources.",
                    actions=[
                        "Define your ICP (Ideal Customer Profile)",
                        "Track retention, not just acquisition",
                        "Double down on what's working",
                    ],
                    related_to=["business", "growth"],
                    confidence=0.7,
                )
            )
        elif stage == "growth":
            insights.append(
                Insight(
                    type=InsightType.OPPORTUNITY,
                    priority=InsightPriority.MEDIUM,
                    title="Growth stage: Scale systematically",
                    description="You have traction - now scale efficiently.",
                    reasoning="Growth stage requires process and infrastructure.",
                    actions=[
                        "Document your processes",
                        "Invest in monitoring and observability",
                        "Consider team expansion",
                    ],
                    related_to=["business", "growth"],
                    confidence=0.6,
                )
            )

        return insights

    def _check_integration_opportunities(
        self,
        biz: dict[str, Any],
        tech: dict[str, Any],
    ) -> list[Insight]:
        """Check for integration-related opportunities."""
        integrations = set(biz.get("integrations", []))
        insights = []

        # No payments + early stage = opportunity
        if "Stripe" not in integrations and biz.get("stage") in ["early", "growth"]:
            if biz.get("product_type") in ["web_app", "mobile_app"]:
                insights.append(
                    Insight(
                        type=InsightType.OPPORTUNITY,
                        priority=InsightPriority.MEDIUM,
                        title="Consider monetization",
                        description="No payment integration detected.",
                        reasoning="Revenue is the ultimate validation of value.",
                        actions=[
                            "Stripe for payments",
                            "Start with a simple pricing model",
                            "Even $1 proves willingness to pay",
                        ],
                        related_to=["business", "revenue"],
                        confidence=0.5,
                    )
                )

        # No analytics
        if "Segment" not in integrations and "Mixpanel" not in integrations:
            if biz.get("stage") in ["mvp", "early"]:
                insights.append(
                    Insight(
                        type=InsightType.RECOMMENDATION,
                        priority=InsightPriority.MEDIUM,
                        title="Add analytics early",
                        description="No analytics integration detected.",
                        reasoning="Understanding user behavior informs better decisions.",
                        actions=[
                            "PostHog for open-source analytics",
                            "Mixpanel for product analytics",
                            "Track actions, not just pageviews",
                        ],
                        related_to=["business", "growth"],
                        confidence=0.6,
                    )
                )

        # No error tracking
        if "Sentry" not in integrations:
            insights.append(
                Insight(
                    type=InsightType.RECOMMENDATION,
                    priority=InsightPriority.MEDIUM,
                    title="Add error tracking",
                    description="No error tracking (Sentry) detected.",
                    reasoning="You can't fix bugs you don't know about.",
                    actions=[
                        "Add Sentry for error tracking",
                        "Set up alerts for critical errors",
                        "Track error trends over time",
                    ],
                    related_to=["technical", "quality"],
                    confidence=0.7,
                )
            )

        return insights

    def _check_git_activity(self, health: dict[str, Any]) -> list[Insight]:
        """Check git activity patterns."""
        git = health.get("git", {})
        insights = []

        if git.get("is_git_repo"):
            frequency = git.get("commit_frequency")
            recent = git.get("recent_commits", 0)

            if frequency == "sporadic" or recent == 0:
                insights.append(
                    Insight(
                        type=InsightType.WARNING,
                        priority=InsightPriority.LOW,
                        title="Low recent activity",
                        description=f"Only {recent} commits in the last 30 days.",
                        reasoning="Consistent progress builds momentum.",
                        actions=[
                            "Set a weekly commit goal",
                            "Break work into smaller tasks",
                            "Ship something every week",
                        ],
                        related_to=["technical", "velocity"],
                        confidence=0.5,
                    )
                )

        return insights

    # Legacy methods for backwards compatibility
    async def _detect_technical_risks(
        self,
        profile: IntelligenceProfile,
    ) -> list[Insight]:
        """Detect technical risks from profile."""
        return []

    async def _detect_business_opportunities(
        self,
        profile: IntelligenceProfile,
    ) -> list[Insight]:
        """Detect business opportunities from profile."""
        return []

    async def _detect_timing_signals(
        self,
        profile: IntelligenceProfile,
    ) -> list[Insight]:
        """Detect timing-related insights."""
        return []

    async def _detect_missing_pieces(
        self,
        profile: IntelligenceProfile,
    ) -> list[Insight]:
        """Detect what's missing that should be there."""
        return []

    async def _detect_growth_opportunities(
        self,
        profile: IntelligenceProfile,
    ) -> list[Insight]:
        """Detect growth opportunities."""
        return []

    def get_insights(
        self,
        type_filter: InsightType | None = None,
        priority_filter: InsightPriority | None = None,
        limit: int = 10,
    ) -> list[Insight]:
        """
        Get insights with optional filters.

        Args:
            type_filter: Filter by insight type
            priority_filter: Filter by priority
            limit: Maximum insights to return

        Returns:
            Filtered list of insights
        """
        filtered = self.insights

        if type_filter:
            filtered = [i for i in filtered if i.type == type_filter]

        if priority_filter:
            filtered = [i for i in filtered if i.priority == priority_filter]

        # Sort by priority (critical first) then by creation time
        priority_order = {
            InsightPriority.CRITICAL: 0,
            InsightPriority.HIGH: 1,
            InsightPriority.MEDIUM: 2,
            InsightPriority.LOW: 3,
        }
        filtered.sort(key=lambda i: (priority_order[i.priority], -i.created_at.timestamp()))

        return filtered[:limit]

    def clear_insights(self) -> None:
        """Clear all insights."""
        self.insights.clear()
