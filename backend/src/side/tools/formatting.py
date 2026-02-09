"""
Sidelith UX Core - Professional CLI Formatting.
"""

from typing import Any, Optional, List, Dict
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
        """Create an image result."""
        content: List[Content] = [
            ImageContent(type="image", data=data, mimeType=mime_type)
        ]
        if caption:
            content.append(TextContent(type="text", text=caption))
        return cls(content=content)

# ============================================================================
# PROFESSIONAL FORMATTING HELPERS
# ============================================================================

def format_header(title: str, subtitle: str = "") -> str:
    """Standard header format."""
    header = f"=== {title.upper()} ==="
    if subtitle:
        header += f"\n{subtitle}"
    return header + "\n"

def format_section(title: str, content: str) -> str:
    """Standard section format."""
    return f"\n--- {title.upper()} ---\n{content}\n"

def format_key_value(key: str, value: Any) -> str:
    """Standard key-value pair."""
    return f"{key}: {value}"

def format_list(items: List[str], bullet: str = "-") -> str:
    """Standard list format."""
    return "\n".join(f"{bullet} {item}" for item in items)    

# ============================================================================
# TOOL-SPECIFIC FORMATTERS
# ============================================================================

def format_decision(
    question: str,
    verdict: str,
    reasoning: str,
    confidence: int = 85,
    comparison: Optional[dict] = None,
    context: str = "",
    follow_up: str = ""
) -> str:
    """Format an architectural decision."""
    output = format_header("Architectural Decision")
    output += format_key_value("Question", question) + "\n"
    output += format_key_value("Verdict", verdict) + "\n"
    output += format_key_value("Confidence", f"{confidence}%") + "\n\n"
    
    if context:
        output += format_section("Context", context)

    output += format_section("Reasoning", reasoning)

    if comparison:
        comp_str = ""
        for option, metrics in comparison.items():
            comp_str += f"\n{option}:\n"
            for k, v in metrics.items():
                comp_str += f"  - {k}: {v}\n"
        output += format_section("Comparison", comp_str)
        
    if follow_up:
        output += f"\n-> Suggested Next Step: {follow_up}\n"
        
    return output

def format_strategy(
    question: str,
    iq_display: str, 
    dimensions: dict,
    top_focus: str,
    llm_context: str = "",
    elapsed: float = 0.0,
    follow_up: str = ""
) -> str:
    """Format strategic review."""
    output = format_header("Strategic Analysis")
    output += format_key_value("Inquiry", question) + "\n\n"
    
    # Dimensions
    dim_str = ""
    for dim, score in dimensions.items():
        status = "Good" if score >= 25 else "Attention Needed"
        dim_str += f"- {dim}: {score} ({status})\n"
    output += format_section("Dimensions", dim_str)
    
    output += format_key_value("Top Focus", top_focus) + "\n"
    
    if llm_context:
        output += format_section("Analysis", llm_context)
        
    if follow_up:
        output += f"\n-> Suggested Next Step: {follow_up}\n"
        
    return output

def format_simulation(
    persona_name: str,
    persona_quote: str,
    satisfaction: float,
    pain_points: list[str],
    would_pay: str,
    follow_up: str = ""
) -> str:
    """Format user simulation."""
    output = format_header(f"Simulation: {persona_name}")
    output += f'"{persona_quote}"\n\n'
    output += format_key_value("Satisfaction", f"{satisfaction}/10") + "\n"
    
    if pain_points:
        output += format_section("Pain Points", format_list(pain_points))
        
    output += format_key_value("Value Perception", would_pay) + "\n"
    
    if follow_up:
        output += f"\n-> Suggested Next Step: {follow_up}\n"
        
    return output

def format_audit_summary(
    critical: int,
    high: int,
    medium: int,
    top_issue: str,
    follow_ups: list[str] = None
) -> str:
    """Format audit summary."""
    output = format_header("Codebase Audit Summary")
    output += f"CRITICAL: {critical} | HIGH: {high} | MEDIUM: {medium}\n\n"
    output += format_key_value("Top Issue", top_issue) + "\n"
    
    if follow_ups:
        output += format_section("Recommended Actions", format_list(follow_ups))
        
    return output

def format_audit_finding(
    finding_type: str,
    severity: str,
    file_path: str,
    code_snippet: str,
    fix: str,
    risk: str,
    follow_up: str = ""
) -> str:
    """Format a single finding."""
    output = format_header(f"Finding: {severity} - {finding_type}")
    output += format_key_value("File", file_path) + "\n\n"
    
    if code_snippet:
        output += "Context:\n"
        output += "----------------------------------------\n"
        output += code_snippet + "\n"
        output += "----------------------------------------\n\n"
        
    output += format_key_value("Risk", risk) + "\n"
    output += format_key_value("Proposed Fix", fix) + "\n"
    
    if follow_up:
        output += f"\n-> Suggested Next Step: {follow_up}\n"
        
    return output

def format_plan(goals: list[dict], follow_up: str = "") -> str:
    """Format strategic plan."""
    output = format_header("Strategic Plan")
    
    if not goals:
        return output + "No goals defined.\n"
        
    for goal in goals:
        idx = "✅" if goal.get('status') in ['done', 'completed'] else "⬜"
        title = goal.get('title', 'Untitled')
        output += f"{idx} {title}\n"
        
    if follow_up:
        output += f"\n-> Suggested Next Step: {follow_up}\n"
        
    return output

# Compatibility Helpers
def get_premium_header(tool_name: str, cost: str = "") -> str:
    return format_header(tool_name, cost)

def add_source_attribution(content: str, tool_name: str, data_sources: list[str]) -> str:
    return content + f"\n[Sources: {', '.join(data_sources)}]"

def get_stack_summary(profile: Any) -> str:
    if hasattr(profile, 'languages') and profile.languages:
        langs = list(profile.languages.keys())[:3]
        return ', '.join(langs)
    return 'Detecting...'
    
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


