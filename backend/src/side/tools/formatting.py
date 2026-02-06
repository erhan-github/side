"""
Sidelith UX Core - The "Killer Features" Formatting Hub.

Implements the professional branding and presentation patterns for tool outputs:
- Strategic Box-Drawing: Consistent framing for all diagnostic reports.
- Confidence Scoring: Visual probability and risk metrics.
- Strategy Hooks: Dynamic follow-up prompts for continuous engagement.
- Curiosity Gap: Strategic info-density management.

Branding Terminology:
- Strategic Verdict (decide tool)
- Strategic IQ Check (strategy tool)
- Mission Control (plan tool)
- Virtual User Lab (simulate tool)
- Codebase X-Ray (run_audit tool)
"""

from datetime import datetime, timezone
from typing import Any, Optional, List
from dataclasses import dataclass
from mcp.types import Content, TextContent, ImageContent

@dataclass
class ToolResult:
    """Standardized result from an MCP tool execution."""
    content: List[Content]
    is_error: bool = False
    
    @classmethod
    def text(cls, text: str) -> "ToolResult":
        """Create a text-only success result."""
        return cls(content=[TextContent(type="text", text=text)])
        
    @classmethod
    def error(cls, text: str) -> "ToolResult":
        """Create a text-only error result."""
        return cls(content=[TextContent(type="text", text=text)], is_error=True)

    @classmethod
    def image(cls, data: bytes, mime_type: str, caption: str = "") -> "ToolResult":
        """Create an image result (with optional text caption)."""
        content: List[Content] = [
            ImageContent(type="image", data=data, mimeType=mime_type)
        ]
        if caption:
            content.append(TextContent(type="text", text=caption))
        return cls(content=content)


# ============================================================================
# MARKETING-ALIGNED TOOL NAMES
# ============================================================================

TOOL_NAMES = {
    "decide": "STRATEGIC VERDICT",
    "strategy": "STRATEGIC IQ CHECK",
    "plan": "MISSION CONTROL",
    "check": "PROGRESS SYNC",
    "simulate": "VIRTUAL USER LAB",
    "run_audit": "CODEBASE X-RAY",
}

TOOL_COSTS = {
    "decide": "128 tokens",
    "strategy": "256 tokens",
    "plan": "128 tokens",
    "check": "64 tokens",
    "simulate": "64 tokens",
    "run_audit": "512 tokens",
}


# ============================================================================
# BOX DRAWING TEMPLATES
# ============================================================================

def box_header(emoji: str, title: str, cost: str = "") -> str:
    """Create a premium box header."""
    cost_str = f" [{cost}]" if cost else ""
    title_line = f"{emoji} {title}{cost_str}"
    width = max(50, len(title_line) + 4)
    
    return f"┌─ {title_line} {'─' * (width - len(title_line) - 4)}┐\n"


def box_footer(follow_up: Optional[str] = None) -> str:
    """Create a box footer with optional follow-up hook."""
    if follow_up:
        return f"│\n│  ▸ {follow_up}\n└{'─' * 50}┘"
    return f"└{'─' * 50}┘"


def box_line(content: str, indent: int = 2) -> str:
    """Create a line inside a box."""
    return f"│{' ' * indent}{content}\n"


def box_empty() -> str:
    """Create an empty line in box."""
    return "│\n"


def box_separator() -> str:
    """Create a separator line in box."""
    return f"├{'─' * 50}┤\n"


# ============================================================================
# CONFIDENCE & PROGRESS BARS
# ============================================================================

def confidence_bar(score: int, max_score: int = 100, width: int = 20) -> str:
    """Create a visual confidence bar.
    
    Example: ████████████░░░░░░░░  87% confidence
    """
    ratio = min(score / max_score, 1.0)
    filled = int(ratio * width)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return f"{bar}  {int(ratio * 100)}% confidence"


def progress_bar(done: int, total: int, width: int = 20) -> str:
    """Create a visual progress bar.
    
    Example: ████████████░░░░░░░░  60% (6/10)
    """
    ratio = done / total if total > 0 else 0
    filled = int(ratio * width)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return f"{bar}  {int(ratio * 100)}% ({done}/{total})"


def strategic_iq_display(score: int, max_score: int = 160) -> str:
    """Create the Strategic IQ display with a central School Grade."""
    percentage = min(int((score / max_score) * 100), 100)
    
    # Simple A-F Scale (consistent with audit system)
    if percentage >= 90: grade, label = "A", "Production Ready"
    elif percentage >= 80: grade, label = "B", "Needs Polish"
    elif percentage >= 70: grade, label = "C", "MVP Quality"
    elif percentage >= 60: grade, label = "D", "Significant Issues"
    else: grade, label = "F", "Critical Fixes Needed"
    
    return f"""        GRADE: {grade} ({label})
        SCORE: {score}/{max_score}
    {confidence_bar(score, max_score)}"""


# ============================================================================
# DECISION FORMATTING (for `decide` tool)
# ============================================================================

def format_decision(
    question: str,
    verdict: str,
    reasoning: str,
    confidence: int = 85,
    comparison: Optional[dict] = None,
    context: str = "",
    follow_up: str = "Want the implementation guide?"
) -> str:
    """Format an architectural decision in the killer features style.
    
    Args:
        question: The original question
        verdict: The one-line recommendation (e.g., "Use PostgreSQL")
        reasoning: Brief explanation (2-3 lines max)
        confidence: Confidence score 0-100
        comparison: Optional dict like {"Redux": {"Setup": "45 min", "Bundle": "+12kb"}, "Context": {...}}
        context: Personalized context (e.g., "Your app: 12 components")
        follow_up: The follow-up question hook
    
    Returns:
        Beautifully formatted decision
    """
    output = box_header("💎", "DECISION", "128 Tokens")
    output += box_empty()
    output += box_line(f"VERDICT: {verdict}")
    output += box_line(confidence_bar(confidence))
    output += box_empty()
    
    # Add comparison table if provided
    if comparison:
        output += box_line("┌" + "─" * 35 + "┐")
        headers = list(comparison.keys())
        metrics = list(comparison[headers[0]].keys()) if headers else []
        
        # Header row
        header_row = f"│ {'':9} │"
        for h in headers[:2]:
            header_row += f" {h:10} │"
        output += box_line(header_row)
        output += box_line("├" + "─" * 35 + "┤")
        
        # Data rows
        for metric in metrics:
            row = f"│ {metric:9} │"
            for h in headers[:2]:
                val = comparison[h].get(metric, "")
                row += f" {str(val):10} │"
            output += box_line(row)
        
        output += box_line("└" + "─" * 35 + "┘")
        output += box_empty()
    
    # Personalized context
    if context:
        output += box_line(f"Your project: {context}")
        output += box_empty()
    
    # Reasoning (brief)
    for line in reasoning.split("\n")[:2]:
        output += box_empty()
    output += box_line("📎 Decision saved to Strategic Database")
    output += box_footer(follow_up)
    
    return output


# ============================================================================
# STRATEGY FORMATTING (for `strategy` tool)
# ============================================================================

def format_strategy(
    question: str,
    iq_display: str,
    dimensions: dict,
    top_focus: str,
    llm_context: str = "",
    elapsed: float = 0.0,
    follow_up: str = "Run full forensic audit?"
) -> str:
    """Format strategic review in the killer features style with institutional grades.
    
    Args:
        question: The strategic inquiry
        iq_display: The pre-formatted IQ grade/score string
        dimensions: Dict of dimension scores
        top_focus: Main focus area
        llm_context: Deep strategic insight from LLM
        elapsed: Response time
        follow_up: Next step prompt
    """
    output = box_header("📊", "STRATEGIC IQ", "256 Tokens")
    output += box_empty()
    output += box_line(f"INQUIRY: {question[:60]}...")
    output += box_empty()
    output += box_line(iq_display)
    output += box_empty()
    
    # Dimension breakdown
    output += box_line("┌─────────────┬──────┬────────┐")
    header_row = "│ Dimension   │ Score│ Status │"
    output += box_line(header_row)
    output += box_line("├─────────────┼──────┼────────┤")
    
    for dim, score in dimensions.items():
        status = "✅" if score >= 30 else "💡" if score >= 25 else "⚠️" if score >= 20 else "🔴"
        output += box_line(f"│ {dim:11} │  {score:2}  │   {status}   │")
    
    output += box_line("└─────────────┴──────┴────────┘")
    output += box_empty()
    output += box_line(f"TOP FOCUS: {top_focus}")
    
    # LLM Strategic Context (The Vibe)
    if llm_context:
        output += box_empty()
        output += box_line("⚡ THE STRATEGIC VIBE:")
        for line in llm_context.split("\n")[:3]:
            output += box_line(f"  {line.strip()}")
    
    output += box_line("📎 Strategy saved to Strategic Database")
    if elapsed > 0:
        output += box_line(f"⚡ Response time: {elapsed*1000:.0f}ms")
    output += box_footer(follow_up)
    
    return output


# ============================================================================
# SIMULATION FORMATTING (for `simulate` tool)
# ============================================================================

def format_simulation(
    persona_name: str,
    persona_quote: str,
    satisfaction: float,
    pain_points: list[str],
    would_pay: str,
    follow_up: str = "Want me to redesign this flow?"
) -> str:
    """Format virtual user simulation in the killer features style.
    
    Args:
        persona_name: e.g., "TINA THE TEACHER"
        persona_quote: The emotional quote from persona
        satisfaction: Score 0-10
        pain_points: List of 2-3 pain points
        would_pay: Price or churn prediction
        follow_up: The follow-up hook
    """
    output = box_header("🎭", persona_name, "64 Tokens")
    output += box_line(f'"{persona_quote}"')
    output += box_separator()
    output += box_empty()
    
    # Reaction with emoji scale
    emoji = "😠" if satisfaction < 4 else "😐" if satisfaction < 6 else "😊" if satisfaction < 8 else "🤩"
    output += box_line(f"REACTION: {emoji} {'Frustrated' if satisfaction < 4 else 'Neutral' if satisfaction < 6 else 'Satisfied' if satisfaction < 8 else 'Delighted'} ({satisfaction}/10)")
    output += box_empty()
    
    # Pain points
    output += box_line("PAIN POINTS:")
    for i, pain in enumerate(pain_points[:3], 1):
        output += box_line(f'  {i}. "{pain}"')
    output += box_empty()
    
    # Business impact
    output += box_line(f"WOULD PAY: {would_pay}")
    output += box_footer(follow_up)
    
    return output


# ============================================================================
# AUDIT FORMATTING (for `run_audit` tool)
# ============================================================================

def format_audit_summary(
    critical: int,
    high: int,
    medium: int,
    top_issue: str,
    follow_ups: list[str] = None
) -> str:
    """Format audit summary using curiosity gap pattern.
    
    Shows magnitude, not details. Let user choose what to explore.
    """
    if follow_ups is None:
        follow_ups = ["Show all findings?", "Fix critical issues first?", "Update Strategic Database?"]
    
    output = box_header("🔍", "AUDIT COMPLETE", "512 Tokens")
    output += box_empty()
    
    # Magnitude display (color-coded in concept)
    severity_line = f"{critical} CRITICAL • {high} HIGH • {medium} MEDIUM"
    output += box_line(severity_line)
    output += box_empty()
    output += box_line(f"TOP ISSUE: {top_issue}")
    output += box_empty()
    
    # Follow-up options
    for hook in follow_ups[:3]:
        output += box_line(f"▸ {hook}")
    
    output += box_footer()
    
    return output


def format_audit_finding(
    finding_type: str,
    severity: str,
    file_path: str,
    code_snippet: str,
    fix: str,
    risk: str,
    follow_up: str = "Apply fix automatically?"
) -> str:
    """Format a single forensic finding with code diff."""
    emoji = "🚨" if severity == "CRITICAL" else "⚠️" if severity == "HIGH" else "📋"
    
    output = box_header(emoji, f"{severity} FINDING", "")
    output += box_empty()
    output += box_line(f"{finding_type} in {file_path}")
    output += box_empty()
    
    # Code snippet
    output += box_line("┌" + "─" * 40 + "┐")
    for line in code_snippet.split("\n")[:4]:
        output += box_line(f"│ {line[:38]:38} │")
    output += box_line("└" + "─" * 40 + "┘")
    output += box_empty()
    
    output += box_line(f"RISK: {risk}")
    output += box_line(f"FIX:  {fix}")
    output += box_footer(follow_up)
    
    return output


# ============================================================================
# PLAN FORMATTING (for `plan` tool)
# ============================================================================

def format_plan(goals: list[dict], follow_up: str = "Break down Week 1 into tasks?") -> str:
    """Format the strategic plan in the killer features style."""
    if not goals:
        return box_header("📋", "90-DAY STRATEGIC PLAN", "") + box_empty() + \
               box_line("No goals yet.") + box_empty() + \
               box_line('▸ Try: plan "Launch MVP by end of month"') + \
               box_footer()
    
    output = box_header("📋", "90-DAY STRATEGIC PLAN", "128 Tokens")
    output += box_empty()
    
    # Group goals
    objectives = [g for g in goals if g.get('type') == 'objective']
    milestones = [g for g in goals if g.get('type') == 'milestone']
    tasks = [g for g in goals if g.get('type') == 'task']
    regular_goals = [g for g in goals if g.get('type') in ['goal', None]]
    
    all_items = objectives + milestones + regular_goals + tasks
    
    # Visual OKR display
    output += box_line("┌" + "─" * 40 + "┐")
    output += box_line("│ STRATEGIC OKRS" + " " * 24 + "│")
    output += box_line("├" + "─" * 40 + "┤")
    
    for i, g in enumerate(all_items[:5]):
        status = "✅" if g.get('status') in ['done', 'completed'] else "⬜"
        title = g.get('title', '')[:35]
        output += box_line(f"│ {status} {title:36} │")
    
    if len(all_items) > 5:
        output += box_line(f"│   +{len(all_items) - 5} more items...               │")
    
    output += box_line("└" + "─" * 40 + "┘")
    output += box_empty()
    
    # Progress
    total = len(goals)
    done = len([g for g in goals if g.get('status') in ['done', 'completed']])
    output += box_line(progress_bar(done, total))
    output += box_empty()
    output += box_line("📎 Strategic Database updated")
    output += box_footer(follow_up)
    
    return output


# ============================================================================
# LEGACY COMPATIBILITY (keeping old functions)
# ============================================================================

def get_premium_header(tool_name: str, cost: str = "1 Credit") -> str:
    """Generate a high-tech dashboard header (legacy)."""
    return box_header("🔧", tool_name, cost)


def add_source_attribution(content: str, tool_name: str, data_sources: list[str]) -> str:
    """Add source attribution footer (legacy)."""
    footer = f"\n\n────────────────────────────────────────\n"
    footer += f"📡 Sources: {', '.join(data_sources)}\n"
    footer += f"🔧 Tool: {tool_name}\n"
    return content + footer


def get_stack_summary(profile: Any) -> str:
    """Get concise stack summary."""
    if hasattr(profile, 'languages') and profile.languages:
        langs = list(profile.languages.keys())[:3]
        return ', '.join(langs)
    return 'Detecting...'
