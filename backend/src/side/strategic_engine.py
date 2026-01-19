"""
Side Strategic Decision Engine

Provides instant, context-aware strategic guidance for vibe coders.
Not a reading platform - THE strategic operating system for product development.

Core capabilities:
- Tech stack decisions (PostgreSQL vs MongoDB, etc.)
- Architecture choices (monolith vs microservices)
- Prioritization frameworks (Impact/Effort matrix)
- Risk assessment (technical debt, security, compliance)
- Growth strategy (channels, marketing, fundraising)
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class DecisionType(Enum):
    """Types of strategic decisions Side can help with."""
    TECH_STACK = "tech_stack"
    ARCHITECTURE = "architecture"
    PRIORITIZATION = "prioritization"
    GROWTH = "growth"
    FUNDRAISING = "fundraising"
    LEGAL = "legal"
    PERFORMANCE = "performance"


class ConfidenceLevel(Enum):
    """Confidence level in recommendations."""
    VERY_HIGH = "very_high"  # 90%+
    HIGH = "high"  # 70-90%
    MEDIUM = "medium"  # 50-70%
    LOW = "low"  # < 50%


@dataclass
class StrategicContext:
    """Context about the user's current situation."""
    
    # Technical context
    tech_stack: list[str]  # ["Python", "FastAPI", "React"]
    team_size: int
    team_skills: list[str]  # ["SQL", "Python", "JavaScript"]
    
    # Business context
    stage: str  # "idea", "pmf", "growth", "scale"
    users: int
    revenue: float  # MRR
    runway_months: int
    
    # Project context
    focus_area: str | None  # "auth", "api", "frontend", etc.
    recent_commits: int
    open_issues: int
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "tech_stack": self.tech_stack,
            "team_size": self.team_size,
            "team_skills": self.team_skills,
            "stage": self.stage,
            "users": self.users,
            "revenue": self.revenue,
            "runway_months": self.runway_months,
            "focus_area": self.focus_area,
            "recent_commits": self.recent_commits,
            "open_issues": self.open_issues,
        }


@dataclass
class StrategicRecommendation:
    """A strategic recommendation with reasoning."""
    
    decision_type: DecisionType
    recommendation: str  # "Use PostgreSQL"
    confidence: ConfidenceLevel
    reasoning: list[str]  # ["Team knows SQL", "Structured data", etc.]
    alternatives: list[dict[str, Any]]  # Other options considered
    next_steps: list[str]  # Actionable steps
    estimated_effort: str  # "30 minutes", "2 hours", "1 day"
    impact: str  # "HIGH", "MEDIUM", "LOW"
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_type": self.decision_type.value,
            "recommendation": self.recommendation,
            "confidence": self.confidence.value,
            "reasoning": self.reasoning,
            "alternatives": self.alternatives,
            "next_steps": self.next_steps,
            "estimated_effort": self.estimated_effort,
            "impact": self.impact,
        }


class StrategicDecisionEngine:
    """
    The core strategic intelligence engine.
    
    Provides instant, context-aware recommendations for all types of
    strategic decisions vibe coders face during product development.
    
    Philosophy:
    - Speed: < 1 second responses
    - Clarity: Clear recommendation + reasoning
    - Action: Immediate next steps
    - Context: Based on YOUR situation, not generic advice
    """
    
    def __init__(self):
        """Initialize the decision engine."""
        self.decision_history: list[StrategicRecommendation] = []
    
    def analyze_tech_stack_decision(
        self,
        question: str,
        context: StrategicContext,
    ) -> StrategicRecommendation:
        """
        Analyze tech stack decisions (e.g., PostgreSQL vs MongoDB).
        
        Uses decision frameworks:
        - Team capability assessment
        - Use case fit analysis
        - Cost-benefit analysis
        - Risk assessment
        
        Returns instant recommendation with clear reasoning.
        """
        # Example: PostgreSQL vs MongoDB
        if "postgres" in question.lower() or "mongodb" in question.lower():
            return self._analyze_database_choice(context)
        
        # Add more tech stack decisions here
        return self._generic_tech_decision(question, context)
    
    def _analyze_database_choice(
        self,
        context: StrategicContext,
    ) -> StrategicRecommendation:
        """Analyze PostgreSQL vs MongoDB decision."""
        
        # Scoring factors
        postgres_score = 0
        mongo_score = 0
        reasoning = []
        
        # Factor 1: Team skills
        if "SQL" in context.team_skills or "PostgreSQL" in context.team_skills:
            postgres_score += 30
            reasoning.append("✅ Team knows SQL (0 learning curve)")
        else:
            mongo_score += 10
            reasoning.append("⚠️ Team doesn't know SQL (learning curve)")
        
        # Factor 2: Data structure (heuristic based on focus area)
        if context.focus_area in ["auth", "api", "admin"]:
            postgres_score += 25
            reasoning.append("✅ Structured data (perfect for PostgreSQL)")
        else:
            mongo_score += 15
        
        # Factor 3: Scale requirements
        if context.users < 100000:
            postgres_score += 20
            reasoning.append("✅ Scale target < 100K (PostgreSQL proven)")
        
        # Factor 4: Cost
        postgres_score += 15
        reasoning.append("✅ Lower cost ($50/mo vs $200/mo)")
        
        # Determine recommendation
        if postgres_score > mongo_score:
            recommendation = "PostgreSQL"
            confidence = ConfidenceLevel.VERY_HIGH if postgres_score > 80 else ConfidenceLevel.HIGH
            
            alternatives = [{
                "name": "MongoDB",
                "score": mongo_score,
                "use_case": "Better for unstructured data, rapid prototyping",
            }]
            
            next_steps = [
                "Install PostgreSQL locally",
                "Set up database connection",
                "Create initial schema",
                "Add SQLAlchemy ORM (for FastAPI)",
            ]
        else:
            recommendation = "MongoDB"
            confidence = ConfidenceLevel.HIGH
            
            alternatives = [{
                "name": "PostgreSQL",
                "score": postgres_score,
                "use_case": "Better for structured data, ACID compliance",
            }]
            
            next_steps = [
                "Install MongoDB locally",
                "Set up connection with Motor (async)",
                "Define document schemas",
                "Add indexes for performance",
            ]
        
        return StrategicRecommendation(
            decision_type=DecisionType.TECH_STACK,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=alternatives,
            next_steps=next_steps,
            estimated_effort="2 hours" if recommendation == "PostgreSQL" else "4 hours",
            impact="HIGH",
        )
    
    def _generic_tech_decision(
        self,
        question: str,
        context: StrategicContext,
    ) -> StrategicRecommendation:
        """Handle generic tech decisions."""
        return StrategicRecommendation(
            decision_type=DecisionType.TECH_STACK,
            recommendation="Analyze your specific use case",
            confidence=ConfidenceLevel.MEDIUM,
            reasoning=["Need more context about your requirements"],
            alternatives=[],
            next_steps=["Clarify your use case", "List your constraints"],
            estimated_effort="Unknown",
            impact="MEDIUM",
        )
    
    def analyze_architecture_decision(
        self,
        question: str,
        context: StrategicContext,
    ) -> StrategicRecommendation:
        """
        Analyze architecture decisions (monolith vs microservices, etc.).
        
        Considers:
        - Team size and complexity
        - Scale requirements
        - Development speed needs
        - Operational complexity
        """
        question_lower = question.lower()
        
        # Monolith vs Microservices
        if "monolith" in question_lower or "microservice" in question_lower:
            return self._analyze_monolith_vs_microservices(context)
        
        return self._generic_architecture_decision(question, context)
    
    def _analyze_monolith_vs_microservices(
        self,
        context: StrategicContext,
    ) -> StrategicRecommendation:
        """Analyze monolith vs microservices decision."""
        
        monolith_score = 0
        micro_score = 0
        reasoning = []
        
        # Factor 1: Team size
        if context.team_size <= 5:
            monolith_score += 40
            reasoning.append(f"✅ Small team ({context.team_size} devs) → Monolith is simpler")
        else:
            micro_score += 30
            reasoning.append(f"⚠️ Larger team ({context.team_size} devs) → Consider microservices")
        
        # Factor 2: Stage
        if context.stage in ["idea", "pmf"]:
            monolith_score += 35
            reasoning.append("✅ Early stage → Ship fast with monolith")
        else:
            micro_score += 20
        
        # Factor 3: Scale
        if context.users < 10000:
            monolith_score += 25
            reasoning.append("✅ Low scale → Monolith handles it easily")
        
        # Determine recommendation
        if monolith_score > micro_score:
            recommendation = "Monolith"
            confidence = ConfidenceLevel.VERY_HIGH
            
            alternatives = [{
                "name": "Microservices",
                "score": micro_score,
                "use_case": "Better for large teams, high scale, complex domains",
            }]
            
            next_steps = [
                "Build monolith first (faster to ship)",
                "Design modular code (easy to split later)",
                "Use feature flags (for gradual rollout)",
                "Monitor performance (know when to scale)",
            ]
        else:
            recommendation = "Microservices"
            confidence = ConfidenceLevel.HIGH
            
            alternatives = [{
                "name": "Monolith",
                "score": monolith_score,
                "use_case": "Better for small teams, early stage, simple domains",
            }]
            
            next_steps = [
                "Define service boundaries (by domain)",
                "Set up API gateway",
                "Implement service discovery",
                "Plan deployment strategy (containers)",
            ]
        
        return StrategicRecommendation(
            decision_type=DecisionType.ARCHITECTURE,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=alternatives,
            next_steps=next_steps,
            estimated_effort="1 week" if recommendation == "Monolith" else "2-3 weeks",
            impact="HIGH",
        )
    
    def _generic_architecture_decision(
        self,
        question: str,
        context: StrategicContext,
    ) -> StrategicRecommendation:
        """Handle generic architecture decisions."""
        return StrategicRecommendation(
            decision_type=DecisionType.ARCHITECTURE,
            recommendation="Start simple, scale when needed",
            confidence=ConfidenceLevel.MEDIUM,
            reasoning=["Premature optimization is the root of all evil"],
            alternatives=[],
            next_steps=["Build MVP first", "Measure performance", "Optimize bottlenecks"],
            estimated_effort="Varies",
            impact="MEDIUM",
        )
    
    def analyze_growth_decision(
        self,
        question: str,
        context: StrategicContext,
    ) -> StrategicRecommendation:
        """
        Analyze growth and marketing decisions.
        
        Considers:
        - Product type and target audience
        - Current stage and resources
        - Channel fit and ROI
        """
        question_lower = question.lower()
        
        # Channel selection
        if any(keyword in question_lower for keyword in ["channel", "marketing", "launch", "users"]):
            return self._analyze_growth_channels(context)
        
        return self._generic_growth_decision(question, context)
    
    def _analyze_growth_channels(
        self,
        context: StrategicContext,
    ) -> StrategicRecommendation:
        """Analyze best growth channels."""
        
        # Heuristic: Developer tools → Dev communities
        is_dev_tool = any(tech in ["Python", "JavaScript", "FastAPI", "React"] 
                         for tech in context.tech_stack)
        
        if is_dev_tool:
            recommendation = "Developer Communities"
            reasoning = [
                "✅ Dev tool → Target developer communities",
                "✅ High engagement on HN, Product Hunt, Dev.to",
                "✅ Low cost, high quality users",
            ]
            
            next_steps = [
                "Launch on Product Hunt (prepare materials)",
                "Post on Hacker News ('Show HN')",
                "Write on Dev.to (technical content)",
                "Engage on Reddit (r/programming)",
            ]
            
            alternatives = [
                {
                    "name": "Paid Ads",
                    "use_case": "Faster growth but expensive ($5-10 CAC)",
                },
                {
                    "name": "Content Marketing",
                    "use_case": "Long-term SEO, slower but sustainable",
                },
            ]
        else:
            recommendation = "Content Marketing + Paid Ads"
            reasoning = [
                "✅ B2C product → Broader channels",
                "✅ SEO + paid for faster growth",
            ]
            
            next_steps = [
                "Create landing page (optimize for conversion)",
                "Start content marketing (blog, SEO)",
                "Test paid ads (small budget first)",
                "Build email list (for retention)",
            ]
            
            alternatives = []
        
        return StrategicRecommendation(
            decision_type=DecisionType.GROWTH,
            recommendation=recommendation,
            confidence=ConfidenceLevel.HIGH,
            reasoning=reasoning,
            alternatives=alternatives,
            next_steps=next_steps,
            estimated_effort="2-4 weeks",
            impact="HIGH",
        )
    
    def _generic_growth_decision(
        self,
        question: str,
        context: StrategicContext,
    ) -> StrategicRecommendation:
        """Handle generic growth decisions."""
        return StrategicRecommendation(
            decision_type=DecisionType.GROWTH,
            recommendation="Focus on product-market fit first",
            confidence=ConfidenceLevel.HIGH,
            reasoning=["Growth without PMF = wasted money"],
            alternatives=[],
            next_steps=["Validate with 10 users", "Measure retention", "Then scale"],
            estimated_effort="Varies",
            impact="HIGH",
        )
    
    def analyze_fundraising_decision(
        self,
        question: str,
        context: StrategicContext,
    ) -> StrategicRecommendation:
        """
        Analyze fundraising decisions.
        
        Considers:
        - Current metrics (MRR, growth, runway)
        - Stage and traction
        - Market timing
        """
        # Simple heuristic for now
        should_raise = False
        reasoning = []
        
        # Check runway
        if context.runway_months < 6:
            should_raise = True
            reasoning.append("🔴 Low runway (< 6 months) → Raise now")
        elif context.runway_months < 12:
            reasoning.append("🟡 Medium runway (6-12 months) → Start conversations")
        else:
            reasoning.append("✅ Good runway (12+ months) → Focus on growth")
        
        # Check revenue
        if context.revenue >= 10000:
            reasoning.append("✅ Strong MRR ($10K+) → Good fundraising position")
        elif context.revenue >= 5000:
            reasoning.append("🟡 Decent MRR ($5K+) → Build more traction")
        else:
            reasoning.append("🔴 Low MRR (< $5K) → Too early to raise")
        
        if should_raise:
            recommendation = "Start fundraising now"
            next_steps = [
                "Prepare investor deck",
                "Get warm intros to VCs",
                "Practice pitch",
                "Target: $500K-$2M seed",
            ]
        elif context.revenue >= 5000:
            recommendation = "Build relationships, raise in 3-6 months"
            next_steps = [
                "Focus on growth (hit $10K MRR)",
                "Start investor outreach (warm intros)",
                "Prepare materials (deck, metrics)",
                "Attend networking events",
            ]
        else:
            recommendation = "Too early - focus on product"
            next_steps = [
                "Build product (ship MVP)",
                "Get first customers (validate PMF)",
                "Hit $5K MRR minimum",
                "Then consider fundraising",
            ]
        
        return StrategicRecommendation(
            decision_type=DecisionType.FUNDRAISING,
            recommendation=recommendation,
            confidence=ConfidenceLevel.HIGH,
            reasoning=reasoning,
            alternatives=[],
            next_steps=next_steps,
            estimated_effort="3-6 months",
            impact="HIGH",
        )
    
    def analyze_prioritization(
        self,
        tasks: list[dict[str, Any]],
        context: StrategicContext,
    ) -> list[dict[str, Any]]:
        """
        Prioritize tasks using Impact/Effort matrix.
        
        Framework:
        - High Impact + Low Effort = Do First (Quick Wins)
        - High Impact + High Effort = Plan Carefully (Major Projects)
        - Low Impact + Low Effort = Do Later (Fill-ins)
        - Low Impact + High Effort = Avoid (Time Sinks)
        
        Returns tasks sorted by priority with clear reasoning.
        """
        prioritized = []
        
        for task in tasks:
            impact = task.get("impact", "MEDIUM")
            effort = task.get("effort", "MEDIUM")
            
            # Calculate priority score
            impact_score = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(impact, 2)
            effort_score = {"LOW": 3, "MEDIUM": 2, "HIGH": 1}.get(effort, 2)
            priority_score = impact_score * effort_score
            
            # Determine quadrant
            if impact == "HIGH" and effort == "LOW":
                quadrant = "🔴 CRITICAL (Do First)"
                priority = 1
            elif impact == "HIGH" and effort == "HIGH":
                quadrant = "🟡 IMPORTANT (Plan Carefully)"
                priority = 2
            elif impact == "MEDIUM":
                quadrant = "💡 OPPORTUNITY (If Time)"
                priority = 3
            else:
                quadrant = "❌ SKIP (Not Now)"
                priority = 4
            
            prioritized.append({
                **task,
                "quadrant": quadrant,
                "priority": priority,
                "priority_score": priority_score,
            })
        
        # Sort by priority
        prioritized.sort(key=lambda x: (x["priority"], -x["priority_score"]))
        
        return prioritized
    
    def format_recommendation(
        self,
        rec: StrategicRecommendation,
    ) -> str:
        """Format recommendation for display."""
        
        confidence_emoji = {
            ConfidenceLevel.VERY_HIGH: "🎯",
            ConfidenceLevel.HIGH: "✅",
            ConfidenceLevel.MEDIUM: "💡",
            ConfidenceLevel.LOW: "⚠️",
        }
        
        output = []
        output.append(f"{confidence_emoji[rec.confidence]} RECOMMENDATION: {rec.recommendation}")
        output.append(f"Confidence: {rec.confidence.value.replace('_', ' ').title()} ({rec.confidence.value})")
        output.append("")
        
        output.append("WHY:")
        for reason in rec.reasoning:
            output.append(f"  {reason}")
        output.append("")
        
        if rec.alternatives:
            output.append("ALTERNATIVES CONSIDERED:")
            for alt in rec.alternatives:
                output.append(f"  • {alt['name']} (score: {alt.get('score', 'N/A')})")
                if "use_case" in alt:
                    output.append(f"    {alt['use_case']}")
            output.append("")
        
        output.append("NEXT STEPS:")
        for i, step in enumerate(rec.next_steps, 1):
            output.append(f"  {i}. {step}")
        output.append("")
        
        output.append(f"⏱️ Estimated Effort: {rec.estimated_effort}")
        output.append(f"📊 Impact: {rec.impact}")
        
        return "\n".join(output)
