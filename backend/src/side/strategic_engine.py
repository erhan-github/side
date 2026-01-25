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
    project_path: str | None = None  # Path to the project root
    
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
    tool_proposal: dict[str, Any] | None = None  # The proactive tool call
    
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
            "tool_proposal": self.tool_proposal,
        }


from side.llm.client import LLMClient
from side.services.billing import SystemAction

class StrategicDecisionEngine:
    """
    The core strategic intelligence engine.
    
    Provides instant, context-aware recommendations for all types of
    strategic decisions vibe coders face during product development.
    
    Philosophy:
    - Speed: < 1 second responses (Heuristic) -> "Twitchy"
    - Intelligence: Deep reasoning for complex qs (V2 Hybrid) -> "Deliberate"
    - Clarity: Clear recommendation + reasoning
    - Action: Immediate next steps
    - Context: Based on YOUR situation, not generic advice
    """
    
    def __init__(self):
        """Initialize the decision engine."""
        self.decision_history: list[StrategicRecommendation] = []
        self.llm = LLMClient()
    
    def _ask_expert(
        self,
        question: str,
        context: StrategicContext,
        decision_type: DecisionType
    ) -> StrategicRecommendation:
        """
        V2 HYBRID ROUTER: The "Thinking" Path.
        Uses Model Chaining for Speed & Economy:
        1. FAST_MODEL (8B): Quick Triage & Simple Logic.
        2. SMART_MODEL (70B): Deep Strategic Nuance.
        """
        import json
        
        # 🟢 Tier 1: Is this a simple or complex question? (Rapid Triage)
        # We can use a small prompt to let the 8B model decide if it needs help.
        # For V1-V2 transition, we'll use the LLMClient's auto-tiered completion.
        
        # 1. Construct Prompt
        prompt = f"""You are a Strategic CTO.
        
        User Question: "{question}"
        
        Project Context:
        - Stack: {context.tech_stack}
        - Team: {context.team_size} people
        - Stage: {context.stage}
        
        Task: Provide a decisive recommendation. 
        If this is a tech choice, be opinionated.
        
        Output JSON ONLY:
        {{
            "recommendation": "Title",
            "confidence": "high",
            "reasoning": ["..."],
            "next_steps": ["..."],
            "estimated_effort": "...",
            "impact": "HIGH"
        }}
        """
        
        try:
            # 🟢 Tier 2: Smart Selection
            # We use Llama 3.1 8B for most things, and Llama 3.3 70B for the "Strategy" decision type.
            target_model = "llama-3.1-8b-instant" # Default fast
            if decision_type in [DecisionType.ARCHITECTURE, DecisionType.FUNDRAISING]:
                target_model = "llama-3.3-70b-versatile" # Deep thinking
                
            response = self.llm.complete(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are a CTO.",
                model_override=target_model,
                temperature=0.2
            )
            
            # 3. Parse JSON
            clean_response = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_response)
            
            rec = StrategicRecommendation(
                decision_type=decision_type,
                recommendation=data.get("recommendation", "Analysis"),
                confidence=ConfidenceLevel.HIGH,
                reasoning=data.get("reasoning", []),
                alternatives=[],
                next_steps=data.get("next_steps", []),
                estimated_effort=data.get("estimated_effort", "Unknown"),
                impact=data.get("impact", "HIGH"),
                tool_proposal={
                    "name": "plan", 
                    "arguments": {"goal": f"Execute strategy: {data.get('recommendation')}", "due": "this week"}
                }
            )
            
            # [PERSISTENCE] Save decision to Brain
            self._persist_decision(rec, question, context)
            
            return rec
            
        except Exception:
            return self._generic_tech_decision(question, context)

    def _persist_decision(self, rec: StrategicRecommendation, question: str, context: StrategicContext) -> None:
        """
        [Brain Logic] Write the decision to the Sovereign Ledger (SQLite).
        """
        try:
            from side.storage.simple_db import SimplifiedDatabase
            import uuid
            import json
            
            db = SimplifiedDatabase()
            
            # 1. Get Project ID
            # Use context.project_path if available to ensure alignment with caller
            import os
            target_path = context.project_path if context.project_path else os.getcwd()
            project_id = db.get_project_id(target_path)
            
            with db._connection() as conn:
                conn.execute(
                    """
                    INSERT INTO decisions (
                        id, project_id, question, answer, reasoning, category, 
                        confidence, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (
                        f"dec_{uuid.uuid4().hex[:8]}",
                        project_id,
                        question,
                        rec.recommendation,
                        json.dumps(rec.reasoning),
                        rec.decision_type.value,
                        {"very_high": 9, "high": 7, "medium": 5, "low": 3}.get(rec.confidence.value, 5)
                    )
                )
                conn.commit()
                # self.decision_history is RAM cache, keep using it?
                # Yes, but strictly speaking we should rely on DB.
                self.decision_history.append(rec)
                
        except Exception as e:
            # Fallback: Don't crash the user response if DB fails
            print(f"Warning: Failed to persist decision: {e}")

    def analyze_tech_stack_decision(
        self,
        question: str,
        context: StrategicContext,
    ) -> StrategicRecommendation:
        """
        Analyze tech stack decisions (e.g., PostgreSQL vs MongoDB).
        Hybrid Router: Heuristic (Fast) vs Expert (Smart).
        """
        q_lower = question.lower()
        
        # Path A: Heuristic (Fast, Free, Deterministic)
        # Matches known patterns that we have calibrated logic for.
        if "postgres" in q_lower or "mongodb" in q_lower:
            return self._analyze_database_choice(context)
            
        # Path B: Hybrid V2 (Slow, Paid, Smart)
        # Handles everything else (e.g. "Geospatial", "Vector DB", "Redis vs Memcached")
        return self._ask_expert(question, context, DecisionType.TECH_STACK)
    
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
        
        rec = StrategicRecommendation(
            decision_type=DecisionType.TECH_STACK,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=alternatives,
            next_steps=next_steps,
            estimated_effort="2 hours" if recommendation == "PostgreSQL" else "4 hours",
            impact="HIGH",
            tool_proposal={
                "name": "plan",
                "arguments": {
                    "goal": f"Set up {recommendation} database infrastructure",
                    "due": "today"
                }
            }
        )
        self._persist_decision(rec, "PostgreSQL vs MongoDB", context)
        return rec
    
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
        Hybrid Router: Heuristic (Fast) vs Expert (Smart).
        """
        q_lower = question.lower()
        
        # Path A: Heuristic (Fast)
        # "Monolith or Microservices" is the classic question we optimize for.
        if "monolith" in q_lower or "microservice" in q_lower:
            return self._analyze_monolith_vs_microservices(context)
            
        # Path B: Hybrid V2 (Smart)
        # Handles "Event Driven", "Serverless", "Clean Architecture", etc.
        return self._ask_expert(question, context, DecisionType.ARCHITECTURE)

    
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
        
        rec = StrategicRecommendation(
            decision_type=DecisionType.ARCHITECTURE,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=alternatives,
            next_steps=next_steps,
            estimated_effort="1 week" if recommendation == "Monolith" else "2-3 weeks",
            impact="HIGH",
            tool_proposal={
                "name": "plan",
                "arguments": {
                    "goal": f"Design {recommendation.lower()} architecture boundaries",
                    "due": "this week"
                }
            }
        )
        self._persist_decision(rec, "Monolith vs Microservices", context)
        return rec
    
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
        Hybrid Router: Heuristic (Fast) vs Expert (Smart).
        """
        q_lower = question.lower()
        
        # Path A: Heuristic (Fast)
        # Checks for basic channel selection based on stack.
        if any(k in q_lower for k in ["channel", "marketing", "launch", "users", "seo", "ads"]):
             # Our heuristic is good for "Dev Tools" vs "B2C", but limited.
             # We might want to pass more nuanced growth questions to expert.
             # For now, we prefer heuristic speed unless it's clearly outside scope.
             return self._analyze_growth_channels(context)
        
        # Path B: Hybrid V2 (Smart)
        return self._ask_expert(question, context, DecisionType.GROWTH)

    
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
        
        rec = StrategicRecommendation(
            decision_type=DecisionType.GROWTH,
            recommendation=recommendation,
            confidence=ConfidenceLevel.HIGH,
            reasoning=reasoning,
            alternatives=alternatives,
            next_steps=next_steps,
            estimated_effort="2-4 weeks",
            impact="HIGH",
            tool_proposal={
                "name": "plan",
                "arguments": {
                    "goal": f"Execute growth strategy: {recommendation}",
                    "due": "next month"
                }
            }
        )
        self._persist_decision(rec, "Best Growth Channels", context)
        return rec
    
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
        Hybrid Router: Heuristic (Fast) vs Expert (Smart).
        """
        q_lower = question.lower()
        
        # Path A: Heuristic (Fast)
        # Good for "Should I raise?" based on metrics.
        if "raise" in q_lower or "fund" in q_lower or "money" in q_lower or "vc" in q_lower:
             # Basic runway check is best handled by rigid math.
             return self._analyze_fundraising_metrics(context) 
             
        # Path B: Expert (e.g. "How to pitch?", "Valuation?")
        return self._ask_expert(question, context, DecisionType.FUNDRAISING)
        
    def _analyze_fundraising_metrics(self, context: StrategicContext) -> StrategicRecommendation:
        """Renamed from original analyze logic to separate Heuristic."""

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
        
        rec = StrategicRecommendation(
            decision_type=DecisionType.FUNDRAISING,
            recommendation=recommendation,
            confidence=ConfidenceLevel.HIGH,
            reasoning=reasoning,
            alternatives=[],
            next_steps=next_steps,
            estimated_effort="3-6 months",
            impact="HIGH",
            tool_proposal={
                "name": "plan",
                "arguments": {
                    "goal": "Prepare fundraising deck and metrics" if should_raise else "Focus on product deliverables",
                    "due": "next week"
                }
            }
        )
        self._persist_decision(rec, "Should I raise?", context)
        return rec
    
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
        """
        Format recommendation using the 'Frame Design System' (Hook -> Evidence -> Proposal).
        This drives the 'Proactive Button' UX.
        """
        
        confidence_emoji = {
            ConfidenceLevel.VERY_HIGH: "🎯",
            ConfidenceLevel.HIGH: "⚡",
            ConfidenceLevel.MEDIUM: "💡",
            ConfidenceLevel.LOW: "⚠️",
        }
        
        output = []
        
        # 1. THE HOOK (Insight)
        # "🎯 Strategy: Use PostgreSQL"
        output.append(f"{confidence_emoji[rec.confidence]} **Strategy: {rec.recommendation}**")
        output.append("")
        
        # 2. THE EVIDENCE (Context)
        # Bullet points of why
        output.append("**Why this works:**")
        for reason in rec.reasoning[:3]: # Keep it tight
            output.append(f"*   {reason}")
        output.append("")
        
        # 3. THE PROPOSAL (The Button)
        if rec.tool_proposal:
            tool_name = rec.tool_proposal.get("name")
            args = rec.tool_proposal.get("arguments", {})
            
            # Formatted specifically so the Agent recognizes it as a directive to call the tool
            output.append(f"> **Side Proposes Action:** `{tool_name}`")
            output.append(f"> *Run this to execute the strategy immediately.*")
            
            # This is the signal for the 'Run' button in the client
            output.append(f"tool_code: call_tool('{tool_name}', {args})") 
        else:
            # Fallback for pure advice
            output.append("**Next Steps:**")
            for i, step in enumerate(rec.next_steps[:3], 1):
                output.append(f"{i}. {step}")
        
        return "\n".join(output)
