"""
CSO.ai Business Intelligence.

Infers business context from codebase:
- Product type (SaaS, mobile, API, etc.)
- Development stage
- Business domain
- Integration landscape
- Priorities
"""

from typing import Any

from cso_ai.core.understander import BusinessIntel, TechnicalIntel


class BusinessAnalyzer:
    """
    Infers business context from technical signals.

    Understands:
    - What type of product is being built
    - What stage the company is at
    - What domain/industry they're in
    - What third-party services they use
    - What their priorities appear to be
    """

    # Product type signals
    PRODUCT_SIGNALS: dict[str, list[str]] = {
        "mobile_app": [
            "SwiftUI", "UIKit", "React Native", "Flutter",
            "Swift", "Kotlin", "Dart",
        ],
        "web_app": [
            "React", "Vue", "Angular", "Svelte",
            "Next.js", "Nuxt", "Remix",
        ],
        "api": [
            "FastAPI", "Express", "Flask", "Django",
            "NestJS", "Gin", "Fiber",
        ],
        "cli": [
            "argparse", "click", "typer", "commander",
        ],
    }

    # Integration detection
    INTEGRATION_PATTERNS: dict[str, list[str]] = {
        # LLM Providers
        "Groq": ["groq", "api.groq.com"],
        "OpenAI": ["openai", "api.openai.com"],
        "Anthropic": ["anthropic", "api.anthropic.com"],
        "Mistral": ["mistral", "api.mistral.ai"],
        "Cohere": ["cohere", "api.cohere.ai"],
        "Replicate": ["replicate"],
        "Together": ["together", "api.together.xyz"],
        "Ollama": ["ollama"],
        "LiteLLM": ["litellm"],
        # Payment & Finance
        "Stripe": ["stripe"],
        "Plaid": ["plaid"],
        # Databases
        "Supabase": ["supabase", "@supabase/supabase-js", "supabase.co"],
        "PlanetScale": ["planetscale", "@planetscale"],
        "Neon": ["neon", "neon.tech"],
        "Turso": ["turso", "@libsql"],
        "Firebase": ["firebase", "firebase-admin"],
        "PostgreSQL": ["pg", "psycopg2", "asyncpg"],
        "MongoDB": ["mongodb", "mongoose", "pymongo"],
        "Prisma": ["@prisma/client"],
        "Redis": ["redis", "ioredis"],
        # Infrastructure
        "AWS": ["boto3", "aws-sdk", "@aws-sdk"],
        "Vercel": ["vercel", "@vercel"],
        "Railway": ["railway"],
        "Fly.io": ["fly.io", "flyctl"],
        "Render": ["render.com"],
        # Auth
        "Auth0": ["auth0"],
        "Clerk": ["@clerk"],
        # Monitoring & Analytics
        "Sentry": ["sentry", "@sentry"],
        "Segment": ["analytics-node", "@segment"],
        # Communication
        "Twilio": ["twilio"],
        "SendGrid": ["sendgrid", "@sendgrid"],
    }

    # Domain keywords
    DOMAIN_KEYWORDS: dict[str, list[str]] = {
        "EdTech": ["learn", "course", "lesson", "quiz", "student", "education"],
        "FinTech": ["payment", "bank", "finance", "transaction", "wallet", "invoice"],
        "HealthTech": ["health", "medical", "patient", "doctor", "clinic"],
        "E-commerce": ["shop", "store", "cart", "checkout", "product", "order"],
        "DevTools": ["developer", "api", "sdk", "cli", "debug", "deploy"],
        "AI/ML": ["model", "train", "embedding", "vector", "llm", "inference"],
        "SaaS": ["subscription", "tenant", "team", "workspace", "plan"],
        "Social": ["user", "profile", "post", "feed", "follow", "message"],
        "Productivity": ["task", "project", "calendar", "note", "workflow"],
    }

    def __init__(self) -> None:
        """Initialize the analyzer."""
        pass

    async def analyze(
        self,
        tech_intel: TechnicalIntel,
        readme_content: str | None = None,
        root_path: str | None = None,
    ) -> BusinessIntel:
        """
        Infer business context from technical intelligence.

        Args:
            tech_intel: Technical intelligence from codebase
            readme_content: Optional README content for context
            root_path: Optional root path for code scanning

        Returns:
            BusinessIntel with inferred context
        """
        intel = BusinessIntel()

        # Infer product type
        intel.product_type = self._infer_product_type(tech_intel)

        # Detect integrations from dependencies
        deps_integrations = self._detect_integrations(tech_intel)

        # Also scan code for integrations (catches Groq, API URLs, etc.)
        code_integrations = []
        if root_path:
            code_integrations = await self._detect_integrations_from_code(root_path)

        # Merge both sources
        intel.integrations = sorted(
            list(set(deps_integrations + code_integrations))
        )

        # Infer domain
        intel.domain = self._infer_domain(tech_intel, readme_content)

        # Infer stage
        intel.stage = self._infer_stage(tech_intel, intel)

        # Infer priorities
        intel.priorities = self._infer_priorities(tech_intel, intel)

        # Infer business model
        intel.business_model = self._infer_business_model(intel)

        return intel

    def _infer_product_type(self, tech: TechnicalIntel) -> str | None:
        """Infer product type from frameworks and languages."""
        frameworks = set(tech.frameworks)
        languages = set(tech.languages.keys())

        scores: dict[str, int] = {k: 0 for k in self.PRODUCT_SIGNALS}

        for product_type, signals in self.PRODUCT_SIGNALS.items():
            for signal in signals:
                if signal in frameworks or signal in languages:
                    scores[product_type] += 1

        # Boost mobile if we see mobile-specific languages
        if "Swift" in languages or "Kotlin" in languages:
            scores["mobile_app"] += 2
        if "Dart" in languages:
            scores["mobile_app"] += 2

        if scores:
            best = max(scores.items(), key=lambda x: x[1])
            if best[1] > 0:
                return best[0]

        return None

    def _detect_integrations(self, tech: TechnicalIntel) -> list[str]:
        """Detect third-party integrations from dependency files."""
        all_deps = set()
        for deps in tech.dependencies.values():
            all_deps.update(dep.lower() for dep in deps)

        detected = []
        for integration, patterns in self.INTEGRATION_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in all_deps:
                    detected.append(integration)
                    break

        return detected

    async def _detect_integrations_from_code(self, root_path: str) -> list[str]:
        """
        Detect integrations by scanning actual code files.

        This catches integrations that aren't in dependency files,
        like direct API calls to Groq, OpenAI, etc.
        """
        from pathlib import Path

        from cso_ai.intel.delta_detector import CodeScanner

        scanner = CodeScanner()
        root = Path(root_path)

        if not root.exists():
            return []

        try:
            result = await scanner.scan_integrations(root)
            return result.get("integrations", [])
        except Exception:
            # If scanning fails, return empty list
            return []

    def _infer_domain(
        self,
        tech: TechnicalIntel,
        readme: str | None,
    ) -> str | None:
        """Infer business domain from signals."""
        # Combine text sources
        text_sources = []
        if readme:
            text_sources.append(readme.lower())

        combined = " ".join(text_sources)

        # Score domains by keyword matches
        scores: dict[str, int] = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in combined)
            if score > 0:
                scores[domain] = score

        # Boost from integrations
        all_deps = " ".join(
            dep.lower()
            for deps in tech.dependencies.values()
            for dep in deps
        )

        if "stripe" in all_deps or "plaid" in all_deps:
            scores["FinTech"] = scores.get("FinTech", 0) + 2
        if "openai" in all_deps or "anthropic" in all_deps:
            scores["AI/ML"] = scores.get("AI/ML", 0) + 2

        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]

        return None

    def _infer_stage(
        self,
        tech: TechnicalIntel,
        biz: BusinessIntel,
    ) -> str | None:
        """Infer development stage."""
        signals = tech.health_signals

        # Maturity indicators
        maturity_score = 0

        if signals.get("has_tests"):
            maturity_score += 1
        if signals.get("has_ci"):
            maturity_score += 2

        # Integration indicators
        if "Sentry" in biz.integrations:
            maturity_score += 1
        if "Segment" in biz.integrations:
            maturity_score += 1
        if "Stripe" in biz.integrations:
            maturity_score += 2  # Revenue = growth stage

        # Determine stage
        if maturity_score >= 5:
            return "growth"
        elif maturity_score >= 2:
            return "early"
        else:
            return "mvp"

    def _infer_priorities(
        self,
        tech: TechnicalIntel,
        biz: BusinessIntel,
    ) -> list[str]:
        """Infer current priorities."""
        priorities = []

        signals = tech.health_signals

        # Missing essentials
        if not signals.get("has_tests"):
            priorities.append("Testing")
        if not signals.get("has_ci"):
            priorities.append("CI/CD")

        # Stage-based priorities
        if biz.stage == "mvp":
            priorities.append("Core Features")
        elif biz.stage == "early":
            priorities.append("User Acquisition")
            priorities.append("Product-Market Fit")
        elif biz.stage == "growth":
            priorities.append("Scaling")
            priorities.append("Team Growth")

        return priorities

    def _infer_business_model(self, biz: BusinessIntel) -> str | None:
        """Infer business model from signals."""
        integrations = set(biz.integrations)

        # B2B signals
        if biz.product_type == "api" or "Segment" in integrations:
            return "B2B"

        # B2C signals
        if biz.product_type == "mobile_app":
            return "B2C"

        # E-commerce signals
        if "Stripe" in integrations and biz.domain == "E-commerce":
            return "E-commerce"

        return None
