"""
CSO.ai MCP Tools - The interface to your AI Chief Strategy Officer.

These tools are designed to be invoked through natural conversation.
The descriptions help Cursor understand when to use each tool.

DELTA-BASED TRACKING:
1. SKELETON (one-time): Basic project understanding (2-3 lines)
   - Languages, domain, what the project is about
   - Created on first analysis, rarely updated

2. DELTA (frequent): What changed since last sync
   - New commits, files changed, TODOs added/removed
   - Quick sync each time you use CSO

3. STRATEGY: Based on skeleton + recent deltas
   - No need to re-analyze entire codebase each time

SIMPLIFIED CORE TOOLS (Fast):
- read: Top 5 relevant articles (instant from cache)
- strategy: Advice based on skeleton + deltas
- sync: Quick delta check (what changed?)
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
    # =========================================================================
    # SIMPLIFIED CORE TOOLS (Fast, Primary Use)
    # =========================================================================
    Tool(
        name="read",
        description="""Show the most relevant articles to read right now. FAST.

Triggers on:
- "what should I read?"
- "relevant articles"
- "CSO, anything interesting?"
- "tech news for me"
- "what's worth reading?"

Returns top 5 cached articles scored for YOUR stack. Instant response.""",
        inputSchema={
            "type": "object",
            "properties": {
                "refresh": {
                    "type": "boolean",
                    "description": "Force refresh from sources (slower). Default: false",
                    "default": False,
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="strategy",
        description="""Strategic advice based on your project's current state. FAST.

Triggers on:
- "CSO, what should I focus on?"
- "what's our strategy?"
- "strategic advice"
- "what are the priorities?"
- "CSO, help me think"

Uses: project skeleton + recent deltas + LLM reasoning.""",
        inputSchema={
            "type": "object",
            "properties": {
                "context": {
                    "type": "string",
                    "description": "Optional: what you're working on right now",
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="sync",
        description="""Quick sync: detect what changed since last check. FAST.

Triggers on:
- "CSO, sync"
- "what changed?"
- "update CSO"
- "quick sync"

Checks git commits, file changes, TODOs. Updates delta tracker.""",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to project. Defaults to current directory.",
                },
            },
            "required": [],
        },
    ),
    # =========================================================================
    # FULL TOOLS (Detailed operations, may be slower)
    # =========================================================================
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
        # Simplified core tools (fast)
        "read": _handle_read,
        "strategy": _handle_strategy,
        "sync": _handle_sync,
        # Full tools
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

    # Check what we have
    db = _get_database()
    skeleton = db.get_latest_skeleton()
    profile = db.get_latest_profile()
    
    if skeleton:
        project_status = f"✅ {skeleton['name']} ({skeleton['primary_language']})"
    elif profile:
        project_status = f"✅ Profile loaded"
    else:
        project_status = "⚠️ No project yet - run 'sync'"

    return f"""🧠 CSO.ai Ready

┌─────────────────────────────────────────┐
│         Chief Strategy Officer          │
│         {project_status:^31} │
└─────────────────────────────────────────┘

🚀 QUICK START (Fast):
  • "CSO, sync" - First time? Sync your project
  • "what should I read?" - Top articles for you
  • "what's our strategy?" - Strategic advice

📊 DETAILED (Slower):
  • "analyze codebase" - Full deep analysis
  • "refresh articles" - Fetch fresh content

💡 Delta Tracking:
  CSO learns your project skeleton once,
  then tracks changes (deltas) to give
  fast, relevant advice each time.
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

    # Run business analysis (with code scanning for integrations)
    biz_analyzer = BusinessAnalyzer()
    biz_intel = await biz_analyzer.analyze(tech_intel, readme_content, root_path=str(root))

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

    # Get recent deltas for context
    project_path = profile.get("path", "")
    recent_deltas = []
    if project_path:
        recent_deltas = db.get_recent_deltas(project_path, limit=10, days=7)

    try:
        advice = await strategist.get_strategy(
            question=question,
            profile=profile,
            articles=articles_data,
            recent_deltas=recent_deltas,
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


# =============================================================================
# SIMPLIFIED CORE HANDLERS (Fast)
# =============================================================================


async def _handle_read(arguments: dict[str, Any]) -> str:
    """Return top 5 relevant articles from cache. FAST."""
    force_refresh = arguments.get("refresh", False)
    
    db = _get_database()
    profile = db.get_latest_profile()
    skeleton = db.get_latest_skeleton()
    
    if profile is None and skeleton is None:
        return """📚 Reading List

❌ No project data yet. Run sync first:
   "CSO, sync"
"""

    # Get cached articles first (instant)
    cached_articles = db.get_articles(limit=100)
    
    # If refresh requested or no articles, fetch new ones
    if force_refresh or len(cached_articles) == 0:
        try:
            from cso_ai.intel.market import MarketAnalyzer
            market = MarketAnalyzer()
            articles = await market.get_tech_articles(profile, days=7, limit=20)
            cached_articles = articles
        except Exception as e:
            if len(cached_articles) == 0:
                return f"📚 Reading List\n\n❌ No articles. Error: {str(e)[:50]}"

    # Get top 5 by relevance score
    sorted_articles = sorted(
        cached_articles,
        key=lambda a: a.relevance_score or 0,
        reverse=True
    )[:5]

    if not sorted_articles:
        return "📚 Reading List\n\nNo articles found. Try: refresh=true"

    # Get stack info from profile or skeleton
    if profile:
        tech = profile.get("technical", {})
        primary_lang = tech.get('primary_language', '?')
        frameworks = tech.get('frameworks', [])
    elif skeleton:
        primary_lang = skeleton.get('primary_language', '?')
        frameworks = []
    else:
        primary_lang = '?'
        frameworks = []
    
    output = f"""📚 Top Articles for You

Stack: {primary_lang} | {', '.join(frameworks[:2]) or 'No frameworks'}

"""

    for i, article in enumerate(sorted_articles, 1):
        score = article.relevance_score or 0
        # Visual score indicator
        if score >= 70:
            indicator = "🔥"
        elif score >= 50:
            indicator = "👍"
        else:
            indicator = "📄"
        
        title = article.title[:55] + "..." if len(article.title) > 55 else article.title
        output += f"{i}. {indicator} [{score:.0f}] {title}\n"
        output += f"   {article.url}\n"
        if article.relevance_reason:
            reason = article.relevance_reason[:70]
            if len(article.relevance_reason) > 70:
                reason += "..."
            output += f"   → {reason}\n"
        output += "\n"

    output += "─" * 40 + "\n"
    output += "💡 Add refresh=true to get fresh articles"

    return output


async def _handle_strategy(arguments: dict[str, Any]) -> str:
    """Strategic advice based on skeleton + deltas. Uses LLM if available."""
    context = arguments.get("context", "")
    
    db = _get_database()
    
    # Try skeleton first (fast, lightweight)
    skeleton = db.get_latest_skeleton()
    profile = db.get_latest_profile()
    
    # Use skeleton if available, fall back to profile
    if skeleton is None and profile is None:
        return """🎯 Strategic Advice

❌ No project data yet. Run sync first:
   "CSO, sync" or "CSO, analyze my codebase"
"""

    # Use profile if available (has most complete data), otherwise skeleton
    if profile:
        tech = profile.get("technical", {})
        biz = profile.get("business", {})
        project_name = Path(profile.get("path", "")).name
        domain = biz.get("domain", "Unknown")
        stage = biz.get("stage", "Unknown")
        primary_lang = tech.get("primary_language", "Unknown")
        description = skeleton.get("description", "") if skeleton else ""
        project_path = profile.get("path", "")
        health = tech.get("health_signals", {})
        git = health.get("git", {})
        issues = health.get("code_issues", {})
    elif skeleton:
        project_name = skeleton.get("name", "Unknown")
        domain = skeleton.get("domain", "Unknown")
        stage = skeleton.get("stage", "Unknown")
        primary_lang = skeleton.get("primary_language", "Unknown")
        description = skeleton.get("description", "")
        project_path = skeleton.get("path", "")
        health = {}
        git = {}
        issues = {}
    else:
        # This shouldn't happen due to check above, but handle it
        return """🎯 Strategic Advice

❌ No project data yet. Run sync first:
   "CSO, sync" or "CSO, analyze my codebase"
"""
    
    # Get recent deltas for context
    deltas = db.get_recent_deltas(project_path, limit=10, days=7)
    delta_summary = db.get_delta_summary(project_path, days=7)

    output = f"""🎯 Strategic Advice

Project: {project_name}
{primary_lang} | {domain} | {stage}
"""
    
    if description:
        output += f"\"{description[:60]}...\"\n"
    
    # Show recent activity
    if deltas:
        output += f"\n📊 Recent: {len(deltas)} changes tracked\n"
    
    output += "\n"

    # Try LLM first (if available)
    from cso_ai.intel.strategist import Strategist
    strategist = Strategist()
    
    if strategist.is_available:
        # Build context with skeleton + deltas
        llm_context = f"Project: {project_name} ({primary_lang}, {domain}, {stage})"
        if description:
            llm_context += f"\nAbout: {description}"
        if delta_summary.get("total_deltas", 0) > 0:
            llm_context += f"\nRecent changes: {delta_summary['total_deltas']} events"
            for dtype, summaries in delta_summary.get("by_type", {}).items():
                llm_context += f"\n- {dtype}: {len(summaries)} events"
        
        question = context if context else "What should I focus on? Give 3-5 specific, actionable recommendations."
        
        # Use existing profile if available, otherwise build minimal one
        strategy_profile = profile if profile else {
            "path": project_path,
            "technical": {"primary_language": primary_lang},
            "business": {"domain": domain, "stage": stage},
        }
        
        try:
            advice = await strategist.get_strategy(
                question=f"{question}\n\nContext: {llm_context}",
                profile=strategy_profile,
                articles=[],  # Skip articles for speed
                recent_deltas=deltas,
            )
            output += advice
            output += "\n\n" + "─" * 40 + "\n"
            output += "💡 Powered by Groq LLM"
            return output
        except Exception as e:
            output += f"⚠️ LLM error: {str(e)[:30]}\n\n"

    # Fallback: Rule-based advice
    output += "📋 Based on your project analysis:\n\n"

    recommendations = []
    
    biz = profile.get("business", {}) if profile else {}
    if stage == 'mvp':
        recommendations.append("🚀 MVP Stage: Focus on core features, not perfection")
        recommendations.append("👥 Talk to 5+ users this week for validation")
    elif stage == 'early':
        recommendations.append("📈 Early Stage: Start measuring key metrics")
        recommendations.append("🔄 Establish feedback loops with users")
    elif stage == 'growth':
        recommendations.append("⚡ Growth Stage: Focus on performance and scale")
        recommendations.append("🏗️ Technical debt becomes critical now")

    # Health-based advice
    if not health.get('has_ci'):
        recommendations.append("⚙️ Add CI/CD - critical for team velocity")
    if not health.get('has_tests'):
        recommendations.append("🧪 Add tests for critical paths")
    
    # Git activity advice
    recent = git.get('recent_commits', 0)
    if recent == 0:
        recommendations.append("⚠️ No recent commits - momentum is key")
    elif recent > 50:
        recommendations.append("🔥 High velocity! Make sure quality keeps up")
    
    # TODO advice
    todo_count = len(issues.get('todos', []))
    if todo_count > 10:
        recommendations.append(f"📝 {todo_count} TODOs - schedule a cleanup sprint")
    
    # Focus areas from git
    focus = git.get('focus_areas', [])
    if focus:
        recommendations.append(f"🎯 Recent focus: {', '.join(focus[:3])}")

    for rec in recommendations[:5]:
        output += f"{rec}\n"

    output += "\n" + "─" * 40 + "\n"
    output += "💡 Set GROQ_API_KEY for smarter LLM-powered advice"

    return output


async def _handle_sync(arguments: dict[str, Any]) -> str:
    """Quick sync: detect what changed since last check."""
    from cso_ai.intel.delta_detector import (
        CodeScanner,
        GitDiffAnalyzer,
        Snapshot,
        SnapshotComparer,
    )
    
    path = arguments.get("path", ".")
    if path == ".":
        path = os.getcwd()
    
    root = Path(path).resolve()
    
    if not root.exists() or not root.is_dir():
        return f"❌ Invalid path: {root}"
    
    db = _get_database()
    
    # Check if we have a skeleton or profile for this project
    project_path = str(root)
    skeleton = db.get_skeleton(project_path)
    profile = db.get_profile(project_path)
    
    output = f"🔄 Syncing: {root.name}\n\n"
    
    # If no skeleton, create one from profile if available, otherwise minimal
    if skeleton is None:
        output += "📋 First sync - creating project skeleton...\n\n"
        
        # Use profile data if available (no need to re-scan)
        if profile:
            tech = profile.get("technical", {})
            biz = profile.get("business", {})
            primary_lang = tech.get("primary_language", "Unknown")
            languages = tech.get("languages", {})
            domain = biz.get("domain", "General")
            stage = biz.get("stage", "mvp")
            description = None  # Description not in profile
        else:
            # Minimal detection - just infer from project name
            primary_lang = "Unknown"
            languages = {}
            domain = "General"
            stage = "mvp"
            description = None
            
            # Quick domain inference from name only (no file scanning)
            name_lower = root.name.lower()
            if any(x in name_lower for x in ["ai", "ml", "llm", "model"]):
                domain = "AI/ML"
            elif any(x in name_lower for x in ["api", "backend", "server"]):
                domain = "Backend"
            elif any(x in name_lower for x in ["web", "frontend", "ui"]):
                domain = "Frontend"
            elif any(x in name_lower for x in ["mobile", "ios", "android"]):
                domain = "Mobile"
        
        # Save skeleton
        db.save_skeleton(
            path=project_path,
            name=root.name,
            description=description,
            primary_language=primary_lang,
            languages=languages,
            domain=domain,
            stage=stage,
        )
        
        output += f"✅ Skeleton created\n\n"
    
    # Enhanced delta detection using new system
    # 1. Scan current codebase state (only what we need for deltas)
    scanner = CodeScanner()
    integrations_result = await scanner.scan_integrations(root)
    env_vars_result = await scanner.scan_env_vars(root)
    frameworks_result = await scanner.scan_frameworks(root)
    
    # 2. Analyze recent git activity
    git_analyzer = GitDiffAnalyzer()
    git_signals = await git_analyzer.analyze_recent(root, days=7)
    
    # 3. Build current snapshot
    current_snapshot_data = {
        "integrations": integrations_result.get("integrations", []),
        "frameworks": frameworks_result.get("frameworks", []),
        "env_vars": env_vars_result.get("env_vars", []),
    }
    new_snapshot = Snapshot.create("all", current_snapshot_data)
    
    # 4. Compare to last snapshot
    old_snapshot_dict = db.get_latest_snapshot(project_path, "all")
    old_snapshot = None
    if old_snapshot_dict:
        old_snapshot = Snapshot(
            snapshot_type=old_snapshot_dict["snapshot_type"],
            data=old_snapshot_dict["data"],
            hash=old_snapshot_dict["hash"],
        )
    
    comparer = SnapshotComparer()
    semantic_deltas = comparer.compare(old_snapshot, new_snapshot)
    
    # 5. Record semantic deltas
    significant_changes = False
    if semantic_deltas:
        output += "📊 Semantic changes detected:\n"
        for delta in semantic_deltas:
            output += f"   • {delta.summary}\n"
            db.record_delta(
                project_path=project_path,
                delta_type=delta.delta_type.value,
                summary=delta.summary,
                details=delta.details,
            )
            if delta.is_significant:
                significant_changes = True
        output += "\n"
    else:
        output += "✅ No semantic changes detected\n\n"
    
    # 6. Record git activity (if any commits)
    if git_signals.get("commits"):
        commit_count = len(git_signals["commits"])
        output += f"📝 Git activity: {commit_count} commit(s) in last 7 days\n"
        if git_signals.get("focus_areas"):
            output += f"   Focus areas: {', '.join(git_signals['focus_areas'][:3])}\n"
        output += "\n"
    
    # 7. Save new snapshot
    db.save_snapshot(
        project_path=project_path,
        snapshot_type="all",
        data=current_snapshot_data,
        snapshot_hash=new_snapshot.hash,
    )
    
    # 8. Update profile if significant changes detected
    if significant_changes:
        output += "🔄 Significant changes detected - profile should be updated\n"
        output += "   Run 'analyze_codebase' to refresh your profile\n\n"
    
    # Show current state summary
    if current_snapshot_data["integrations"]:
        output += "🔌 Current integrations:\n"
        for integration in current_snapshot_data["integrations"][:5]:
            output += f"   • {integration}\n"
        output += "\n"
    
    # Show recent delta history
    recent_deltas = db.get_recent_deltas(project_path, limit=5, days=7)
    if recent_deltas:
        output += f"📈 Recent activity ({len(recent_deltas)} events):\n"
        for d in recent_deltas[:3]:
            output += f"   • {d['summary']} ({d['recorded_at'][:10]})\n"
    
    output += "\n" + "─" * 40 + "\n"
    output += "💡 Use 'strategy' for advice based on these changes"
    
    return output
