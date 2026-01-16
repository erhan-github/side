"""
CSO.ai Understander - The comprehension layer.

The Understander processes observations and builds understanding:
- Technical profile (languages, frameworks, architecture)
- Business profile (stage, domain, model)
- Market position (competitors, trends)
- Financial signals (runway, economics)

It transforms raw observations into actionable intelligence.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from cso_ai.core.listener import Observation


@dataclass
class TechnicalIntel:
    """Technical intelligence about a codebase."""

    languages: dict[str, int] = field(default_factory=dict)
    primary_language: str | None = None
    frameworks: list[str] = field(default_factory=list)
    dependencies: dict[str, list[str]] = field(default_factory=dict)
    architecture_patterns: list[str] = field(default_factory=list)
    health_signals: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize technical intel."""
        return {
            "languages": self.languages,
            "primary_language": self.primary_language,
            "frameworks": self.frameworks,
            "dependencies": self.dependencies,
            "architecture_patterns": self.architecture_patterns,
            "health_signals": self.health_signals,
        }


@dataclass
class BusinessIntel:
    """Business intelligence inferred from codebase."""

    product_type: str | None = None  # SaaS, mobile, API, CLI, library
    stage: str | None = None  # idea, mvp, early, growth, mature
    domain: str | None = None  # EdTech, FinTech, DevTools, etc.
    business_model: str | None = None  # B2B, B2C, marketplace, etc.
    integrations: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize business intel."""
        return {
            "product_type": self.product_type,
            "stage": self.stage,
            "domain": self.domain,
            "business_model": self.business_model,
            "integrations": self.integrations,
            "priorities": self.priorities,
        }


@dataclass
class MarketIntel:
    """Market intelligence about the space."""

    competitors: list[str] = field(default_factory=list)
    trends: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)
    threats: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize market intel."""
        return {
            "competitors": self.competitors,
            "trends": self.trends,
            "opportunities": self.opportunities,
            "threats": self.threats,
        }


@dataclass
class FinancialIntel:
    """Financial intelligence signals."""

    has_payments: bool = False
    payment_provider: str | None = None
    pricing_signals: list[str] = field(default_factory=list)
    runway_indicators: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize financial intel."""
        return {
            "has_payments": self.has_payments,
            "payment_provider": self.payment_provider,
            "pricing_signals": self.pricing_signals,
            "runway_indicators": self.runway_indicators,
        }


@dataclass
class IntelligenceProfile:
    """Complete intelligence profile for a project."""

    path: str
    technical: TechnicalIntel = field(default_factory=TechnicalIntel)
    business: BusinessIntel = field(default_factory=BusinessIntel)
    market: MarketIntel = field(default_factory=MarketIntel)
    financial: FinancialIntel = field(default_factory=FinancialIntel)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 0.0  # 0-1 how confident we are in this profile

    def to_dict(self) -> dict[str, Any]:
        """Serialize complete profile."""
        return {
            "path": self.path,
            "technical": self.technical.to_dict(),
            "business": self.business.to_dict(),
            "market": self.market.to_dict(),
            "financial": self.financial.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "confidence": self.confidence,
        }


class Understander:
    """
    The comprehension layer of CSO.ai.

    Responsibilities:
    - Process observations from Listener
    - Build technical intelligence
    - Infer business context
    - Track market position
    - Detect financial signals

    The Understander transforms observations into structured intelligence.
    """

    def __init__(self) -> None:
        """Initialize the Understander."""
        self.profiles: dict[str, IntelligenceProfile] = {}

    async def process_observations(
        self,
        observations: list[Observation],
        path: str,
    ) -> IntelligenceProfile:
        """
        Process observations and build/update intelligence profile.

        Args:
            observations: List of observations from Listener
            path: Path identifier for the profile

        Returns:
            Updated IntelligenceProfile
        """
        # Get or create profile
        if path not in self.profiles:
            self.profiles[path] = IntelligenceProfile(path=path)

        profile = self.profiles[path]

        # Process each observation
        for obs in observations:
            await self._process_observation(obs, profile)

        profile.updated_at = datetime.utcnow()
        return profile

    async def _process_observation(
        self,
        observation: Observation,
        profile: IntelligenceProfile,
    ) -> None:
        """Process a single observation and update profile."""
        # Route to appropriate processor based on source/type
        processors = {
            ("codebase", "structure_scan"): self._process_structure,
            ("document", "document_read"): self._process_document,
            ("git", "repo_detected"): self._process_git,
        }

        processor = processors.get((observation.source, observation.type))
        if processor:
            await processor(observation, profile)

    async def _process_structure(
        self,
        obs: Observation,
        profile: IntelligenceProfile,
    ) -> None:
        """Process codebase structure observation."""
        # TODO: Implement in Phase 2
        profile.confidence = max(profile.confidence, 0.1)

    async def _process_document(
        self,
        obs: Observation,
        profile: IntelligenceProfile,
    ) -> None:
        """Process document observation."""
        # TODO: Implement in Phase 4
        profile.confidence = max(profile.confidence, 0.1)

    async def _process_git(
        self,
        obs: Observation,
        profile: IntelligenceProfile,
    ) -> None:
        """Process git observation."""
        # TODO: Implement in Phase 2
        profile.confidence = max(profile.confidence, 0.1)

    def get_profile(self, path: str) -> IntelligenceProfile | None:
        """Get profile for a path."""
        return self.profiles.get(path)

    def get_latest_profile(self) -> IntelligenceProfile | None:
        """Get most recently updated profile."""
        if not self.profiles:
            return None

        return max(self.profiles.values(), key=lambda p: p.updated_at)
