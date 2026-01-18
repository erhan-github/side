"""
Strategy tool handlers for CSO.ai.

Handles: architectural_decision, strategic_review
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cso_ai.tools.core import get_auto_intel, get_database
from cso_ai.tools.formatting import (
    get_premium_header, 
    add_source_attribution, 
    format_strategy,
    format_decision,
)
from cso_ai.strategic_engine import StrategicContext, StrategicDecisionEngine
from cso_ai.utils import handle_tool_errors

logger = logging.getLogger(__name__)


@handle_tool_errors
async def handle_decide(arguments: dict[str, Any]) -> str:
    """
    Provide instant strategic decisions for vibe coders.
    
    Returns clear recommendation + reasoning + next steps in < 1 second.
    """
    start_time = datetime.now(timezone.utc)
    
    question = arguments.get("question", "")
    user_context = arguments.get("context", "")
    
    if not question:
        return "❌ Please provide a question (e.g., 'Should I use PostgreSQL or MongoDB?')"
    
    # Get auto-intelligence for context
    auto_intel = get_auto_intel()
    profile = await auto_intel.get_or_create_profile()
    
    # Get database for work context
    db = get_database()
    work_context = db.get_latest_work_context(str(Path.cwd()))
    
    # Build strategic context
    context = StrategicContext(
        tech_stack=list(profile.languages.keys()) if profile.languages else [],
        team_size=1,
        team_skills=list(profile.languages.keys()) if profile.languages else [],
        stage="pmf",
        users=0,
        revenue=0.0,
        runway_months=12,
        focus_area=work_context.get("focus_area") if work_context else None,
        recent_commits=work_context.get("recent_commits", 0) if work_context else 0,
        open_issues=0,
    )
    
    # Initialize decision engine
    engine = StrategicDecisionEngine()
    
    # Analyze the question
    question_lower = question.lower()
    
    # Route to appropriate decision type
    if any(keyword in question_lower for keyword in ["postgres", "mongodb", "database", "mysql", "sqlite"]):
        recommendation = engine.analyze_tech_stack_decision(question, context)
        output = engine.format_recommendation(recommendation)
    elif any(keyword in question_lower for keyword in ["monolith", "microservice", "architecture"]):
        recommendation = engine.analyze_architecture_decision(question, context)
        output = engine.format_recommendation(recommendation)
    elif any(keyword in question_lower for keyword in ["channel", "marketing", "launch", "growth", "users", "customer"]):
        recommendation = engine.analyze_growth_decision(question, context)
        output = engine.format_recommendation(recommendation)
    elif any(keyword in question_lower for keyword in ["fundrais", "raise", "investor", "vc", "seed", "series"]):
        recommendation = engine.analyze_fundraising_decision(question, context)
        output = engine.format_recommendation(recommendation)
    elif any(keyword in question_lower for keyword in ["focus", "priority", "what should i", "next"]):
        output = f"""🎯 STRATEGIC PRIORITIES (Based on YOUR context)

CURRENT FOCUS: {context.focus_area or 'Not detected'}
TECH STACK: {', '.join(context.tech_stack[:3]) if context.tech_stack else 'Detecting...'}

RECOMMENDED PRIORITIES:
1. 🔴 CRITICAL: Ship core features (PMF first)
2. 🟡 IMPORTANT: Set up analytics (measure what matters)
3. 💡 OPPORTUNITY: Build in public (get early feedback)

NEXT STEPS:
1. Define your MVP scope (what's the minimum?)
2. Set up basic metrics (signups, retention)
3. Launch to first 10 users (get feedback)

⏱️ Estimated: 1-2 weeks for MVP
📊 Impact: HIGH (validates your idea)"""
    else:
        output = f"""💡 STRATEGIC INSIGHT

QUESTION: {question}

CONTEXT DETECTED:
• Tech Stack: {', '.join(context.tech_stack[:3]) if context.tech_stack else 'Analyzing...'}
• Focus Area: {context.focus_area or 'Not detected'}
• Stage: {context.stage.upper()}

RECOMMENDATION:
For more specific advice, try asking:
• "Should I use PostgreSQL or MongoDB?"
• "Monolith or microservices?"
• "What marketing channels should I use?"
• "Should I raise money now?"
• "What should I focus on this week?"

Or provide more context about your situation."""
    
    # Prepend premium header
    header = get_premium_header("Architectural Decision", "128 Tokens")
    output = header + output

    # Add performance footer
    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    output += f"\n\n⚡ Response time: {elapsed*1000:.0f}ms"
    
    # Add source attribution
    output = add_source_attribution(
        output,
        tool_name="decide",
        data_sources=["Strategic Decision Engine", "Profile Analysis", "Context Detection"]
    )
    
    return output


@handle_tool_errors
async def handle_strategy(arguments: dict[str, Any]) -> str:
    """
    Get strategic advice based on current work.
    
    Target: < 2 seconds
    """
    start_time = datetime.now(timezone.utc)
    context = arguments.get("context", "")

    # Auto-detect stack + recent work
    auto_intel = get_auto_intel()
    profile = await auto_intel.get_or_create_profile()

    # Fetch domain signals
    from cso_ai.intel.signals import SignalAggregator
    from cso_ai.intel.market import Article
    
    aggregator = SignalAggregator()
    domain = profile.domain or profile.to_dict().get("business", {}).get("domain", "General Software")
    articles = []
    article_dicts = []
    
    try:
        signals = await aggregator.fetch_signals(domain)
        for s in signals[:7]:
            article_dicts.append({
                "title": s["title"],
                "url": s["url"],
                "description": s["description"],
                "domain": s["domain"],
                "source": s["source"]
            })
            articles.append(Article(
                title=s["title"],
                url=s["url"],
                description=s["description"],
                source=s["source"],
                domain=s["domain"],
                published_at=datetime.now(timezone.utc)
            ))
    except Exception as e:
        logger.warning(f"Strategy signal fetch failed: {e}")

    # Get active goals for context
    db = get_database()
    active_plans = db.list_plans(status="active", plan_type="goal")
    
    goal_context = ""
    if active_plans:
        goal_context += "📌 CURRENT GOALS:\n"
        for p in active_plans[:5]:
            goal_context += f"  - {p['title']}"
            if p.get('due_date'):
                goal_context += f" (due {p['due_date']})"
            goal_context += "\n"

    # Generate strategy
    from cso_ai.intel.strategist import Strategist
    
    strategist = Strategist()
    profile_dict = profile.to_dict()
    
    # Inject strategic context
    profile_dict["_decisions"] = db.list_decisions()[:5]
    profile_dict["_learnings"] = db.list_learnings()[:5]
    profile_dict["_active_goals"] = db.list_plans(status="active")[:5]
    
    # Check for conflicts
    from cso_ai.intel.guard import Guard
    guard = Guard()
    decisions = db.list_decisions()
    conflict = await guard.check_conflict(context, decisions)
    
    guard_warning = ""
    if conflict:
        logger.info(f"Guard detected conflict: {conflict.reason}")
        guard_warning = f"⚠️ **STRATEGIC CONFLICT DETECTED**\n"
        guard_warning += f"Your request conflicts with Decision #{conflict.decision_id}: {conflict.reason}\n"
        guard_warning += f"Are you pivoting strategy?\n\n"
    
    # Build question
    question = f"What should I focus on? {context}".strip()
    
    if guard_warning:
        question = f"{guard_warning}\n{question}"
        
    if goal_context:
        question += f"\n\nMY CURRENT COMMITMENTS:\n{goal_context}"
    
    if strategist.is_available:
        strategy = await strategist.get_strategy(
            question=question,
            profile=profile_dict,
            articles=article_dicts,
        )
    else:
        strategy = strategist._fallback_strategy(question, profile_dict)

    # Calculate elapsed time
    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    # Calculate Strategic IQ and dimensions
    # Base score: 100, adjust based on profile completeness and context
    strategic_iq = 100
    dimensions = {
        "Architecture": 25,
        "Velocity": 25,
        "Security": 25,
        "Docs": 25,
    }
    
    # Adjust based on detected profile
    if profile.languages and len(profile.languages) >= 2:
        dimensions["Architecture"] = 28
        strategic_iq += 5
    if profile.domain:
        dimensions["Velocity"] = 30
        strategic_iq += 8
    if active_plans and len(active_plans) >= 2:
        dimensions["Velocity"] = 32
        strategic_iq += 5
    
    # Determine top focus
    min_dim = min(dimensions, key=dimensions.get)
    top_focus = f"{min_dim} needs attention" if dimensions[min_dim] < 22 else "All dimensions healthy!"
    
    # If we have LLM-generated strategy, append it as additional context
    llm_context = ""
    if strategy:
        # Extract first 2 lines as the "headline"
        strategy_lines = strategy.strip().split("\n")
        llm_context = "\n".join(strategy_lines[:3])
    
    # Format with new killer features style
    output = format_strategy(
        strategic_iq=strategic_iq,
        dimensions=dimensions,
        top_focus=top_focus if not llm_context else llm_context,
        articles=articles[:2] if articles else None,
        elapsed=elapsed,
        follow_up="Run full forensic audit?"
    )
    
    return output
