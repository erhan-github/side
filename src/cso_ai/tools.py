"""
CSO.ai MCP Tools - The interface to your AI Chief Strategy Officer.

These tools are designed to be invoked through natural conversation.
The descriptions help Cursor understand when to use each tool.
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp.types import Tool

from cso_ai.intel.technical import TechnicalAnalyzer
from cso_ai.intel.business import BusinessAnalyzer
from cso_ai.storage.database import Database

# =============================================================================
# GLOBAL STATE
# =============================================================================

# Singleton instances for persistence across calls
_database: Database | None = None
_last_analyzed_path: str | None = None


def _get_database() -> Database:
    """Get or create the database singleton."""
    global _database
    if _database is None:
        _database = Database()
    return _database


# =============================================================================
# TOOL DEFINITIONS
# =============================================================================

TOOLS: list[Tool] = [
    # -------------------------------------------------------------------------
    # Status & Connection
    # -------------------------------------------------------------------------
    Tool(
        name="ping",
        description="""Check if CSO.ai is online and ready. Triggers on:
- "hey CSO" / "CSO are you there?" / "ping CSO"
- "is my strategy officer online?"
- "check CSO status" / "CSO status"
Returns status and available capabilities.""",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    # -------------------------------------------------------------------------
    # Intelligence Gathering
    # -------------------------------------------------------------------------
    Tool(
        name="analyze_codebase",
        description="""Deep codebase analysis to build CSO's understanding. Triggers on:
- "CSO, understand my codebase" / "analyze this project"
- "what are we building?" / "what's our tech stack?"
- "CSO, look at this codebase" / "understand our code"
- "what does CSO think about our architecture?"
Analyzes: languages, frameworks, dependencies, architecture, health signals.""",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to codebase root. Defaults to current directory.",
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="show_profile",
        description="""Display CSO's current understanding of your project. Triggers on:
- "CSO, what do you know about us?"
- "show our profile" / "what's our tech profile?"
- "CSO, summarize our project" / "describe our codebase"
- "what does CSO understand?"
Shows: technical stack, business context, stage, priorities, risks.""",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    # -------------------------------------------------------------------------
    # Market Intelligence
    # -------------------------------------------------------------------------
    Tool(
        name="whats_new",
        description="""Get relevant tech news and trends curated by CSO. Triggers on:
- "CSO, what's new?" / "what's happening in tech?"
- "what should I be reading?" / "any interesting articles?"
- "what's trending that matters to us?"
- "I'm curious what CSO says about trends"
- "relevant news for our stack"
Returns articles from HN, Lobsters, GitHub scored by relevance.""",
        inputSchema={
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Days to look back. Default: 7",
                    "default": 7,
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="business_insights",
        description="""Get strategic business intelligence from CSO. Triggers on:
- "CSO, what should be our strategy?"
- "what should we focus on?" / "strategic advice?"
- "hey CSO, business trends?" / "industry news?"
- "CSO, any business insights?" / "market intelligence"
Returns: strategy articles, business trends, industry news.""",
        inputSchema={
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Days to look back. Default: 7",
                    "default": 7,
                },
            },
            "required": [],
        },
    ),
    # -------------------------------------------------------------------------
    # Content Evaluation
    # -------------------------------------------------------------------------
    Tool(
        name="analyze_url",
        description="""Have CSO evaluate if content is worth your time. Triggers on:
- "CSO, is this worth reading?" + URL
- "should I read this?" / "is this relevant?"
- "CSO, what do you think about this article?"
- "evaluate this link" / "analyze this URL"
Returns: relevance score, reasoning, key takeaways.""",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to analyze",
                },
            },
            "required": ["url"],
        },
    ),
    Tool(
        name="explore",
        description="""Get a curated deep-dive from CSO on any topic. Triggers on:
- "CSO, tell me about authentication"
- "explore testing strategies" / "deep dive into performance"
- "what should I know about [topic]?"
- "research [topic] for our codebase"
Returns: curated articles, insights, recommendations.""",
        inputSchema={
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Topic to explore (e.g., 'authentication', 'scaling', 'testing')",
                },
            },
            "required": ["topic"],
        },
    ),
    # -------------------------------------------------------------------------
    # Strategic Advice
    # -------------------------------------------------------------------------
    Tool(
        name="ask_strategy",
        description="""Get strategic advice from CSO on any question. Triggers on:
- "CSO, what's our strategy?" / "what should we focus on?"
- "CSO, give me strategic advice about [topic]"
- "what are the risks?" / "what opportunities do we have?"
- "CSO, help me think through [problem]"
- "strategic recommendation for [situation]"
Uses LLM to provide personalized strategic guidance.""",
        inputSchema={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Your strategic question for the CSO",
                },
            },
            "required": ["question"],
        },
    ),
    # -------------------------------------------------------------------------
    # System Operations
    # -------------------------------------------------------------------------
    Tool(
        name="refresh",
        description="""Have CSO refresh its knowledge base. Triggers on:
- "CSO, update your info" / "refresh intelligence"
- "get latest news" / "sync CSO"
- "update market data" / "refresh articles"
Re-fetches all sources and re-scores against profile.""",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="stats",
        description="""Show CSO.ai statistics and storage info. Triggers on:
- "CSO stats" / "show statistics"
- "how many articles?" / "storage info"
Returns: articles count, profile info, LLM status.""",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
]


# =============================================================================
# TOOL HANDLERS
# =============================================================================


async def handle_tool_call(name: str, arguments: dict[str, Any]) -> str:
    """Route tool calls to appropriate handlers."""
    handlers = {
        "ping": _handle_ping,
        "analyze_codebase": _handle_analyze_codebase,
        "show_profile": _handle_show_profile,
        "whats_new": _handle_whats_new,
        "business_insights": _handle_business_insights,
        "analyze_url": _handle_analyze_url,
        "explore": _handle_explore,
        "ask_strategy": _handle_ask_strategy,
        "refresh": _handle_refresh,
        "stats": _handle_stats,
    }

    handler = handlers.get(name)
    if handler is None:
        return f"Unknown tool: {name}"

    return await handler(arguments)


# -----------------------------------------------------------------------------
# Handler Implementations
# -----------------------------------------------------------------------------


async def _handle_ping(arguments: dict[str, Any]) -> str:
    """CSO.ai status check."""
    timestamp = datetime.now(timezone.utc).isoformat()

    # Check if we have a profile
    db = _get_database()
    profile = db.get_latest_profile()
    profile_status = "✅ Profile loaded" if profile else "⚠️ No profile yet"

    return f"""🧠 CSO.ai is online and ready.

┌─────────────────────────────────────────┐
│         Chief Strategy Officer          │
│         Version 0.1.0                   │
│         {timestamp[:19]}          │
│         {profile_status}                │
└─────────────────────────────────────────┘

I can help you with:

📊 INTELLIGENCE
  • analyze_codebase - Deep technical analysis
  • show_profile - What I understand about you

📰 MARKET
  • whats_new - Relevant tech trends
  • business_insights - Strategic intelligence
  • explore [topic] - Deep-dive research

🔍 EVALUATION
  • analyze_url - Is this worth reading?

💡 Just ask naturally:
  "CSO, what should be our strategy?"
  "What's happening in our space?"
  "Is this article worth reading?"
"""


async def _handle_analyze_codebase(arguments: dict[str, Any]) -> str:
    """Analyze codebase to build intelligence profile."""
    global _last_analyzed_path

    path = arguments.get("path", ".")

    # Resolve path
    if path == ".":
        # Try to find a reasonable default
        cwd = os.getcwd()
        path = cwd
    
    root = Path(path).resolve()
    
    if not root.exists():
        return f"❌ Path not found: {root}"

    if not root.is_dir():
        return f"❌ Path is not a directory: {root}"

    # Run technical analysis
    tech_analyzer = TechnicalAnalyzer()
    tech_intel = await tech_analyzer.analyze(root)

    # Read README for business context
    readme_content = None
    for readme_name in ["README.md", "README.rst", "README.txt", "README"]:
        readme_path = root / readme_name
        if readme_path.exists():
            try:
                readme_content = readme_path.read_text(encoding="utf-8")[:5000]
                break
            except (OSError, UnicodeDecodeError):
                continue

    # Run business analysis
    biz_analyzer = BusinessAnalyzer()
    biz_intel = await biz_analyzer.analyze(tech_intel, readme_content)

    # Store in database
    db = _get_database()
    db.save_profile(
        path=str(root),
        technical=tech_intel.to_dict(),
        business=biz_intel.to_dict(),
        confidence=0.7,
    )

    _last_analyzed_path = str(root)

    # Format output
    output = f"""🧠 CSO.ai Intelligence Report

📍 Analyzed: {root.name}
📁 Path: {root}

{'═' * 50}
📊 TECHNICAL INTELLIGENCE
{'═' * 50}

"""

    # Languages
    if tech_intel.languages:
        output += "🗂️ LANGUAGES\n"
        total_files = sum(tech_intel.languages.values())
        for lang, count in list(tech_intel.languages.items())[:5]:
            pct = (count / total_files * 100) if total_files > 0 else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            output += f"   {lang:15} {bar} {count:4} files ({pct:.0f}%)\n"
        output += "\n"

    # Primary language
    if tech_intel.primary_language:
        output += f"🎯 Primary Language: {tech_intel.primary_language}\n\n"

    # Frameworks
    if tech_intel.frameworks:
        output += "⚙️ FRAMEWORKS & LIBRARIES\n"
        for fw in tech_intel.frameworks:
            output += f"   • {fw}\n"
        output += "\n"

    # Dependencies
    if tech_intel.dependencies:
        output += "📦 DEPENDENCIES\n"
        for dep_type, deps in tech_intel.dependencies.items():
            output += f"   {dep_type}: {len(deps)} packages\n"
            # Show top 5
            for dep in deps[:5]:
                output += f"      • {dep}\n"
            if len(deps) > 5:
                output += f"      ... and {len(deps) - 5} more\n"
        output += "\n"

    # Architecture
    if tech_intel.architecture_patterns:
        output += "🏗️ ARCHITECTURE\n"
        for pattern in tech_intel.architecture_patterns:
            output += f"   • {pattern}\n"
        output += "\n"

    # Health signals
    output += "💚 CODE HEALTH\n"
    signals = tech_intel.health_signals
    output += f"   README:     {'✅' if signals.get('has_readme') else '❌'}\n"
    output += f"   .gitignore: {'✅' if signals.get('has_gitignore') else '❌'}\n"
    output += f"   Tests:      {'✅' if signals.get('has_tests') else '❌'}\n"
    output += f"   CI/CD:      {'✅' if signals.get('has_ci') else '❌'}\n"
    output += f"   Docker:     {'✅' if signals.get('has_docker') else '❌'}\n"
    output += f"   License:    {'✅' if signals.get('has_license') else '❌'}\n"
    output += "\n"

    # Git signals (Phase 3)
    git = signals.get("git", {})
    if git.get("is_git_repo"):
        output += "📊 GIT ACTIVITY\n"
        output += f"   Total Commits: {git.get('total_commits', 0)}\n"
        output += f"   Last 30 Days:  {git.get('recent_commits', 0)} commits\n"
        output += f"   Frequency:     {git.get('commit_frequency', 'unknown')}\n"
        if git.get("contributors"):
            output += f"   Contributors:  {', '.join(git['contributors'][:3])}\n"
        if git.get("last_commit_date"):
            output += f"   Last Commit:   {git['last_commit_date']}\n"
        output += "\n"

    # Code issues (Phase 3)
    issues = signals.get("code_issues", {})
    if issues.get("total_issues", 0) > 0:
        output += "📝 CODE ISSUES\n"
        output += f"   TODOs:  {len(issues.get('todos', []))}\n"
        output += f"   FIXMEs: {len(issues.get('fixmes', []))}\n"
        output += f"   HACKs:  {len(issues.get('hacks', []))}\n"
        # Show top 3 TODOs
        for todo in issues.get("todos", [])[:3]:
            output += f"   → {todo.get('file', '?')}: {todo.get('text', '')[:50]}\n"
        output += "\n"

    # Cursor rules (Phase 3)
    cursor_rules = signals.get("cursor_rules")
    if cursor_rules:
        output += "📋 CURSOR RULES DETECTED\n"
        themes = cursor_rules.get("themes", [])
        if themes:
            output += f"   Themes: {', '.join(themes)}\n"
        output += "\n"

    # Business Intelligence
    output += f"""{'═' * 50}
💼 BUSINESS INTELLIGENCE
{'═' * 50}

"""

    if biz_intel.product_type:
        output += f"📱 Product Type: {biz_intel.product_type}\n"
    if biz_intel.domain:
        output += f"🏢 Domain: {biz_intel.domain}\n"
    if biz_intel.stage:
        output += f"📈 Stage: {biz_intel.stage}\n"
    if biz_intel.business_model:
        output += f"💰 Business Model: {biz_intel.business_model}\n"
    output += "\n"

    if biz_intel.integrations:
        output += "🔌 INTEGRATIONS DETECTED\n"
        for integration in biz_intel.integrations:
            output += f"   • {integration}\n"
        output += "\n"

    if biz_intel.priorities:
        output += "🎯 INFERRED PRIORITIES\n"
        for priority in biz_intel.priorities:
            output += f"   • {priority}\n"
        output += "\n"

    # Generate proactive insights (Phase 6)
    from cso_ai.core.anticipator import Anticipator
    anticipator = Anticipator()
    insights = await anticipator.analyze_from_dict({
        "technical": tech_intel.to_dict(),
        "business": biz_intel.to_dict(),
    })

    if insights:
        output += f"""{'═' * 50}
🔮 PROACTIVE INSIGHTS
{'═' * 50}

"""
        for insight in insights[:5]:  # Show top 5
            icon = {
                "risk": "⚠️",
                "opportunity": "💡",
                "recommendation": "📋",
                "warning": "🚨",
                "trend": "📈",
                "action": "✅",
            }.get(insight.type.value, "•")

            priority_color = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
            }.get(insight.priority.value, "")

            output += f"{icon} {priority_color} {insight.title}\n"
            output += f"   {insight.description}\n"
            if insight.actions:
                output += f"   → {insight.actions[0]}\n"
            output += "\n"

    output += f"""{'═' * 50}
✅ Profile saved! Use 'show_profile' to see it anytime.
{'═' * 50}
"""

    return output


async def _handle_show_profile(arguments: dict[str, Any]) -> str:
    """Display current understanding of the project."""
    db = _get_database()
    profile = db.get_latest_profile()

    if profile is None:
        return """📋 CSO Intelligence Profile

⚠️ No intelligence gathered yet.

To build your profile:
  1. Run `analyze_codebase` on your project
  2. CSO.ai will build technical + business understanding
  3. All future insights will be tailored to you

Example: "CSO, analyze my codebase"
"""

    tech = profile.get("technical", {})
    biz = profile.get("business", {})

    output = f"""🧠 CSO.ai Intelligence Profile

📍 Project: {Path(profile['path']).name}
📁 Path: {profile['path']}
🕐 Last Updated: {profile.get('updated_at', 'Unknown')[:19]}
📊 Confidence: {profile.get('confidence', 0) * 100:.0f}%

{'═' * 50}
📊 TECHNICAL PROFILE
{'═' * 50}

"""

    # Languages
    languages = tech.get("languages", {})
    if languages:
        output += "🗂️ Languages: "
        lang_list = [f"{lang} ({count})" for lang, count in list(languages.items())[:4]]
        output += ", ".join(lang_list) + "\n"

    if tech.get("primary_language"):
        output += f"🎯 Primary: {tech['primary_language']}\n"

    frameworks = tech.get("frameworks", [])
    if frameworks:
        output += f"⚙️ Frameworks: {', '.join(frameworks)}\n"

    patterns = tech.get("architecture_patterns", [])
    if patterns:
        output += f"🏗️ Architecture: {', '.join(patterns)}\n"

    output += "\n"

    # Health
    signals = tech.get("health_signals", {})
    health_items = []
    if signals.get("has_tests"):
        health_items.append("Tests ✅")
    else:
        health_items.append("Tests ❌")
    if signals.get("has_ci"):
        health_items.append("CI/CD ✅")
    else:
        health_items.append("CI/CD ❌")
    output += f"💚 Health: {' | '.join(health_items)}\n\n"

    output += f"""{'═' * 50}
💼 BUSINESS PROFILE
{'═' * 50}

"""

    if biz.get("product_type"):
        output += f"📱 Type: {biz['product_type']}\n"
    if biz.get("domain"):
        output += f"🏢 Domain: {biz['domain']}\n"
    if biz.get("stage"):
        output += f"📈 Stage: {biz['stage']}\n"
    if biz.get("business_model"):
        output += f"💰 Model: {biz['business_model']}\n"

    integrations = biz.get("integrations", [])
    if integrations:
        output += f"\n🔌 Integrations: {', '.join(integrations)}\n"

    priorities = biz.get("priorities", [])
    if priorities:
        output += f"\n🎯 Priorities:\n"
        for p in priorities:
            output += f"   • {p}\n"

    output += f"""
{'═' * 50}
💡 Re-run 'analyze_codebase' to update this profile.
{'═' * 50}
"""

    return output


async def _handle_whats_new(arguments: dict[str, Any]) -> str:
    """Get relevant tech news and trends."""
    days = arguments.get("days", 7)

    # Check for profile
    db = _get_database()
    profile = db.get_latest_profile()

    if profile is None:
        return f"""📰 What's New (Last {days} days)

⚠️ No profile found - I can't personalize results.

Run `analyze_codebase` first so I can:
• Score articles against your tech stack
• Filter by your business domain
• Prioritize what matters to you

Run: "CSO, analyze my codebase" first!
"""

    tech = profile.get("technical", {})
    biz = profile.get("business", {})

    output = f"""📰 What's New (Last {days} days)

Profile: {Path(profile['path']).name}
Stack: {tech.get('primary_language', 'Unknown')} | {', '.join(tech.get('frameworks', [])[:3]) or 'No frameworks'}
Domain: {biz.get('domain', 'Unknown')}

{'─' * 50}
Fetching from HN, Lobsters, GitHub...
{'─' * 50}

"""

    # Fetch and score articles
    from cso_ai.intel.market import MarketAnalyzer
    market = MarketAnalyzer()

    try:
        articles = await market.get_tech_articles(profile, days=days, limit=10)

        if not articles:
            output += "No articles found. Try again later or check your network.\n"
        else:
            for i, article in enumerate(articles, 1):
                score = article.relevance_score or 0
                score_bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))

                output += f"{i}. [{score:.0f}] {score_bar}\n"
                output += f"   📰 {article.title[:60]}{'...' if len(article.title) > 60 else ''}\n"
                output += f"   🔗 {article.url}\n"
                output += f"   💡 {article.relevance_reason or 'General tech content'}\n"
                output += f"   📍 {article.source}"
                if article.score:
                    output += f" ({article.score} pts)"
                output += "\n\n"

        output += f"{'─' * 50}\n"
        output += f"Scored {len(articles)} articles against your profile.\n"

    except Exception as e:
        output += f"Error fetching articles: {str(e)}\n"
        output += "Check your network connection and try again.\n"

    return output


async def _handle_business_insights(arguments: dict[str, Any]) -> str:
    """Get strategic business intelligence."""
    days = arguments.get("days", 7)

    db = _get_database()
    profile = db.get_latest_profile()

    if profile is None:
        return f"""💼 Business Insights (Last {days} days)

⚠️ No profile found.

Run `analyze_codebase` first so I can:
• Understand your business domain
• Track relevant industry news
• Surface strategic opportunities

Run: "CSO, analyze my codebase" first!
"""

    biz = profile.get("business", {})

    output = f"""💼 Business Insights (Last {days} days)

Domain: {biz.get('domain', 'Unknown')}
Stage: {biz.get('stage', 'Unknown')}
Model: {biz.get('business_model', 'Unknown')}

{'─' * 50}
Fetching business-relevant content...
{'─' * 50}

"""

    # Fetch and score articles with business focus
    from cso_ai.intel.market import MarketAnalyzer
    market = MarketAnalyzer()

    try:
        articles = await market.get_business_articles(profile, days=days, limit=10)

        if not articles:
            output += "No business articles found. Try again later.\n"
        else:
            for i, article in enumerate(articles, 1):
                score = article.relevance_score or 0

                output += f"{i}. [{score:.0f}/100]\n"
                output += f"   📰 {article.title[:60]}{'...' if len(article.title) > 60 else ''}\n"
                output += f"   🔗 {article.url}\n"
                output += f"   💡 {article.relevance_reason or 'Business content'}\n\n"

        output += f"{'─' * 50}\n"
        output += f"Found {len(articles)} business-relevant articles.\n"

    except Exception as e:
        output += f"Error fetching articles: {str(e)}\n"

    return output


async def _handle_analyze_url(arguments: dict[str, Any]) -> str:
    """Evaluate if a URL is worth reading."""
    url = arguments.get("url", "")
    if not url:
        return "Please provide a URL to analyze."

    db = _get_database()
    profile = db.get_latest_profile()

    if profile is None:
        return f"""🔍 URL Analysis

URL: {url}

⚠️ No profile found - I can't evaluate relevance.

Run `analyze_codebase` first, then I can tell you:
• How relevant this is to YOUR stack
• Whether it's worth your time
• Key takeaways if any
"""

    output = f"""🔍 URL Analysis

Analyzing: {url}

{'─' * 50}

"""

    from cso_ai.intel.market import MarketAnalyzer
    market = MarketAnalyzer()

    try:
        result = await market.analyze_url(url, profile)

        score = result.get("relevance_score", 0)
        score_bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))

        output += f"📊 RELEVANCE SCORE: {score:.0f}/100\n"
        output += f"   {score_bar}\n\n"

        if result.get("title"):
            output += f"📰 Title: {result['title'][:80]}\n\n"

        if result.get("description"):
            output += f"📝 Description:\n   {result['description'][:200]}...\n\n"

        output += f"💡 Why: {result.get('relevance_reason', 'No specific reason')}\n\n"

        output += f"{'─' * 50}\n"
        output += f"🎯 {result.get('recommendation', 'Unable to determine')}\n"

    except Exception as e:
        output += f"Error analyzing URL: {str(e)}\n"
        output += "Make sure the URL is valid and accessible.\n"

    return output


async def _handle_explore(arguments: dict[str, Any]) -> str:
    """Deep-dive research on a topic."""
    topic = arguments.get("topic", "")
    if not topic:
        return "Please specify a topic to explore."

    db = _get_database()
    profile = db.get_latest_profile()

    if profile is None:
        profile = {"technical": {}, "business": {}}

    tech = profile.get("technical", {})

    output = f"""🔬 Deep Dive: {topic}

Stack: {tech.get('primary_language', 'Unknown')} | {', '.join(tech.get('frameworks', [])[:3]) or 'No frameworks'}

{'─' * 50}
Searching for "{topic}" across sources...
{'─' * 50}

"""

    from cso_ai.intel.market import MarketAnalyzer
    market = MarketAnalyzer()

    try:
        articles = await market.explore_topic(topic, profile, limit=10)

        if not articles:
            output += f"No articles found for '{topic}'.\n"
            output += "Try a different topic or broader search term.\n"
        else:
            output += f"Found {len(articles)} articles about {topic}:\n\n"

            for i, article in enumerate(articles, 1):
                score = article.relevance_score or 0

                output += f"{i}. [{score:.0f}/100] {article.title[:55]}{'...' if len(article.title) > 55 else ''}\n"
                output += f"   🔗 {article.url}\n"
                output += f"   📍 {article.source}\n\n"

        output += f"{'─' * 50}\n"
        output += f"Tip: Use 'analyze_url' on any link for deeper analysis.\n"

    except Exception as e:
        output += f"Error exploring topic: {str(e)}\n"

    return output


async def _handle_ask_strategy(arguments: dict[str, Any]) -> str:
    """Get strategic advice from CSO."""
    question = arguments.get("question", "")
    if not question:
        return "Please ask a strategic question."

    db = _get_database()
    profile = db.get_latest_profile()

    if profile is None:
        return f"""🎯 Strategic Advice

Question: {question}

⚠️ No profile found - I need context to give good advice.

Run `analyze_codebase` first so I can:
• Understand your technical stack
• Know your business stage
• Consider your domain
• Give personalized strategy

Run: "CSO, analyze my codebase" first!
"""

    output = f"""🎯 Strategic Advice

Question: {question}

{'─' * 50}
Thinking as your Chief Strategy Officer...
{'─' * 50}

"""

    from cso_ai.intel.strategist import Strategist
    strategist = Strategist()

    # Get relevant articles if available
    articles = db.get_articles(limit=5)
    articles_data = [
        {"title": a.title, "relevance_reason": a.relevance_reason}
        for a in articles
        if (a.relevance_score or 0) >= 50
    ]

    try:
        advice = await strategist.get_strategy(
            question=question,
            profile=profile,
            articles=articles_data,
        )
        output += advice + "\n"
    except Exception as e:
        output += f"Error getting strategic advice: {str(e)}\n"

    output += f"\n{'─' * 50}\n"

    if not strategist.is_available:
        output += "💡 Set GROQ_API_KEY for smarter strategic advice.\n"
    else:
        output += "💡 Powered by Groq (Llama 3.3 70B) - your AI Chief Strategy Officer.\n"

    return output


async def _handle_refresh(arguments: dict[str, Any]) -> str:
    """Refresh CSO.ai's knowledge base."""
    db = _get_database()
    profile = db.get_latest_profile()

    if profile is None:
        return """🔄 Refresh

⚠️ Nothing to refresh - no profile found.

Run `analyze_codebase` first to build your profile.
"""

    output = f"""🔄 Intelligence Refresh

Profile: {Path(profile['path']).name}
Last Updated: {profile.get('updated_at', 'Unknown')[:19]}

{'─' * 50}
Refreshing market intelligence...
{'─' * 50}

"""

    from cso_ai.intel.market import MarketAnalyzer
    market = MarketAnalyzer()

    try:
        # Fetch fresh articles
        articles = await market.fetch_all_sources(days=7)
        output += f"✅ Fetched {len(articles)} articles from sources\n"

        # Score them
        scored = await market.score_articles(articles, profile)
        high_relevance = [a for a in scored if (a.relevance_score or 0) >= 60]
        output += f"✅ Scored articles against your profile\n"
        output += f"✅ Found {len(high_relevance)} highly relevant articles\n\n"

        # Save to database
        db.save_articles(scored)
        output += f"✅ Saved to local database\n\n"

        output += f"{'─' * 50}\n"
        output += "Use 'whats_new' to see the latest relevant content.\n"

    except Exception as e:
        output += f"Error during refresh: {str(e)}\n"
        output += "Check your network connection and try again.\n"

    return output


async def _handle_stats(arguments: dict[str, Any]) -> str:
    """Show CSO.ai statistics."""
    db = _get_database()
    profile = db.get_latest_profile()

    # Check LLM availability
    from cso_ai.intel.strategist import Strategist
    strategist = Strategist()
    llm_status = "✅ Available" if strategist.is_available else "❌ Not configured"

    output = """📊 CSO.ai Statistics

┌─────────────────────────────────────────┐
│              SYSTEM STATUS              │
└─────────────────────────────────────────┘

"""

    # Profile info
    if profile:
        output += f"📋 Profile: {Path(profile['path']).name}\n"
        output += f"   Path: {profile['path']}\n"
        output += f"   Updated: {profile.get('updated_at', 'Unknown')[:19]}\n"
        output += f"   Confidence: {profile.get('confidence', 0) * 100:.0f}%\n\n"
    else:
        output += "📋 Profile: Not created yet\n\n"

    # Article stats
    articles = db.get_articles(limit=1000)
    output += f"📰 Articles Stored: {len(articles)}\n"

    if articles:
        high_relevance = len([a for a in articles if (a.relevance_score or 0) >= 60])
        output += f"   High Relevance (60+): {high_relevance}\n"

        sources: dict[str, int] = {}
        for a in articles:
            src = a.source or "unknown"
            sources[src] = sources.get(src, 0) + 1
        for src, count in sources.items():
            output += f"   {src}: {count}\n"

    output += f"\n🧠 LLM Status: {llm_status}\n"

    if not strategist.is_available:
        output += "   Set GROQ_API_KEY for smart scoring & strategy\n"
        output += "   Get free key: https://console.groq.com/keys\n"

    # Data location
    output += f"\n📁 Data: ~/.cso-ai/data.db\n"

    output += f"""
{'─' * 50}
💡 Use 'refresh' to fetch more articles.
💡 Use 'analyze_codebase' to update your profile.
"""

    return output
