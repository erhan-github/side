"""
Tests for the Strategic Decision Engine.

Tests all decision types:
- Tech stack decisions (PostgreSQL vs MongoDB)
- Architecture decisions (monolith vs microservices)
- Growth decisions (channel selection)
- Fundraising decisions (timing analysis)
"""

import pytest

from side.strategic_engine import (
    ConfidenceLevel,
    DecisionType,
    StrategicContext,
    StrategicDecisionEngine,
)


@pytest.fixture
def small_team_context():
    """Context for a small team at PMF stage."""
    return StrategicContext(
        tech_stack=["Python", "FastAPI", "React"],
        team_size=2,
        team_skills=["SQL", "Python", "JavaScript"],
        stage="pmf",
        users=100,
        revenue=0.0,
        runway_months=12,
        focus_area="auth",
        recent_commits=50,
        open_issues=5,
    )


@pytest.fixture
def growing_team_context():
    """Context for a growing team with traction."""
    return StrategicContext(
        tech_stack=["Python", "FastAPI", "PostgreSQL"],
        team_size=8,
        team_skills=["SQL", "Python", "JavaScript", "Go"],
        stage="growth",
        users=5000,
        revenue=8000.0,
        runway_months=8,
        focus_area="api",
        recent_commits=200,
        open_issues=15,
    )


class TestTechStackDecisions:
    """Test tech stack decision analysis."""
    
    def test_postgres_vs_mongodb_recommends_postgres(self, small_team_context):
        """Should recommend PostgreSQL for small team with SQL skills."""
        engine = StrategicDecisionEngine()
        
        rec = engine.analyze_tech_stack_decision(
            "Should I use PostgreSQL or MongoDB?",
            small_team_context,
        )
        
        assert rec.decision_type == DecisionType.TECH_STACK
        assert rec.recommendation == "PostgreSQL"
        assert rec.confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]
        assert len(rec.reasoning) > 0
        assert len(rec.next_steps) > 0
    
    def test_postgres_reasoning_includes_team_skills(self, small_team_context):
        """Reasoning should mention team SQL skills."""
        engine = StrategicDecisionEngine()
        
        rec = engine._analyze_database_choice(small_team_context)
        
        # Check that reasoning mentions SQL knowledge
        reasoning_text = " ".join(rec.reasoning)
        assert "SQL" in reasoning_text or "sql" in reasoning_text.lower()


class TestArchitectureDecisions:
    """Test architecture decision analysis."""
    
    def test_monolith_vs_microservices_small_team(self, small_team_context):
        """Should recommend monolith for small team."""
        engine = StrategicDecisionEngine()
        
        rec = engine.analyze_architecture_decision(
            "Should I use monolith or microservices?",
            small_team_context,
        )
        
        assert rec.decision_type == DecisionType.ARCHITECTURE
        assert rec.recommendation == "Monolith"
        assert rec.confidence == ConfidenceLevel.VERY_HIGH
        assert "small team" in " ".join(rec.reasoning).lower()
    
    def test_monolith_vs_microservices_large_team(self, growing_team_context):
        """Should consider microservices for larger team."""
        engine = StrategicDecisionEngine()
        
        rec = engine._analyze_monolith_vs_microservices(growing_team_context)
        
        # With 8 devs, might still recommend monolith but with lower confidence
        # or recommend microservices
        assert rec.decision_type == DecisionType.ARCHITECTURE
        assert len(rec.next_steps) > 0


class TestGrowthDecisions:
    """Test growth and marketing decision analysis."""
    
    def test_growth_channels_for_dev_tool(self, small_team_context):
        """Should recommend developer communities for dev tools."""
        engine = StrategicDecisionEngine()
        
        rec = engine.analyze_growth_decision(
            "What marketing channels should I use?",
            small_team_context,
        )
        
        assert rec.decision_type == DecisionType.GROWTH
        assert "Developer Communities" in rec.recommendation
        assert rec.confidence == ConfidenceLevel.HIGH
        
        # Should mention HN, Product Hunt, etc.
        next_steps_text = " ".join(rec.next_steps)
        assert any(platform in next_steps_text for platform in ["Product Hunt", "Hacker News", "Dev.to"])


class TestFundraisingDecisions:
    """Test fundraising decision analysis."""
    
    def test_fundraising_too_early(self, small_team_context):
        """Should recommend waiting when revenue is too low."""
        engine = StrategicDecisionEngine()
        
        rec = engine.analyze_fundraising_decision(
            "Should I raise money now?",
            small_team_context,
        )
        
        assert rec.decision_type == DecisionType.FUNDRAISING
        assert "Too early" in rec.recommendation or "focus on product" in rec.recommendation.lower()
        assert "MRR" in " ".join(rec.reasoning)
    
    def test_fundraising_with_traction(self, growing_team_context):
        """Should recommend building relationships when close to ready."""
        engine = StrategicDecisionEngine()
        
        rec = engine.analyze_fundraising_decision(
            "Should I raise money?",
            growing_team_context,
        )
        
        assert rec.decision_type == DecisionType.FUNDRAISING
        # With $8K MRR and 8 months runway, should recommend building relationships
        assert "relationships" in rec.recommendation.lower() or "raise" in rec.recommendation.lower()


class TestPrioritization:
    """Test task prioritization framework."""
    
    def test_prioritize_by_impact_effort(self, small_team_context):
        """Should prioritize high impact, low effort tasks first."""
        engine = StrategicDecisionEngine()
        
        tasks = [
            {"name": "Fix critical bug", "impact": "HIGH", "effort": "LOW"},
            {"name": "Redesign UI", "impact": "LOW", "effort": "HIGH"},
            {"name": "Add analytics", "impact": "HIGH", "effort": "HIGH"},
            {"name": "Update docs", "impact": "LOW", "effort": "LOW"},
        ]
        
        prioritized = engine.analyze_prioritization(tasks, small_team_context)
        
        # First task should be high impact, low effort
        assert prioritized[0]["name"] == "Fix critical bug"
        assert "CRITICAL" in prioritized[0]["quadrant"]
        
        # Last should be low impact, high effort
        assert prioritized[-1]["name"] == "Redesign UI"
        assert "SKIP" in prioritized[-1]["quadrant"]


class TestRecommendationFormatting:
    """Test recommendation output formatting."""
    
    def test_format_recommendation_includes_all_sections(self, small_team_context):
        """Formatted output should include all key sections."""
        engine = StrategicDecisionEngine()
        
        rec = engine.analyze_tech_stack_decision(
            "PostgreSQL or MongoDB?",
            small_team_context,
        )
        
        output = engine.format_recommendation(rec)
        
        # Should include key sections
        assert "RECOMMENDATION" in output
        assert "WHY" in output
        assert "NEXT STEPS" in output
        assert "Estimated Effort" in output
        assert "Impact" in output
    
    def test_format_includes_confidence_emoji(self, small_team_context):
        """Should include emoji based on confidence level."""
        engine = StrategicDecisionEngine()
        
        rec = engine.analyze_tech_stack_decision(
            "PostgreSQL or MongoDB?",
            small_team_context,
        )
        
        output = engine.format_recommendation(rec)
        
        # Should have emoji (🎯, ✅, 💡, or ⚠️)
        assert any(emoji in output for emoji in ["🎯", "✅", "💡", "⚠️"])


class TestContextToDict:
    """Test context serialization."""
    
    def test_context_to_dict(self, small_team_context):
        """Context should serialize to dict correctly."""
        context_dict = small_team_context.to_dict()
        
        assert context_dict["tech_stack"] == ["Python", "FastAPI", "React"]
        assert context_dict["team_size"] == 2
        assert context_dict["stage"] == "pmf"
        assert context_dict["focus_area"] == "auth"


class TestRecommendationToDict:
    """Test recommendation serialization."""
    
    def test_recommendation_to_dict(self, small_team_context):
        """Recommendation should serialize to dict correctly."""
        engine = StrategicDecisionEngine()
        
        rec = engine.analyze_tech_stack_decision(
            "PostgreSQL or MongoDB?",
            small_team_context,
        )
        
        rec_dict = rec.to_dict()
        
        assert rec_dict["decision_type"] == "tech_stack"
        assert rec_dict["recommendation"] == "PostgreSQL"
        assert "confidence" in rec_dict
        assert "reasoning" in rec_dict
        assert "next_steps" in rec_dict
