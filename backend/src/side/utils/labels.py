"""
Forensic Label Registry - Standardized identifiers and iconography.
"""

from typing import Dict, Any

class ForensicLabel:
    """Central registry for standard finding categories and their visual representations."""
    
    # Label Mapping: Dimension -> (Label, Icon, Color/Tone)
    REGISTRY = {
        "security":          {"tag": "SECURITY",      "icon": "🛡️", "desc": "Security & Protection"},
        "logic":             {"tag": "LOGIC",         "icon": "🧩", "desc": "Logical Consistency"},
        "architecture":      {"tag": "STRUCTURE",     "icon": "🏛️", "desc": "Structural Integrity"},
        "velocity":          {"tag": "SPEED",         "icon": "🏎️", "desc": "Execution Speed"},
        "performance":       {"tag": "PERFORMANCE",   "icon": "⚡", "desc": "Resource Optimization"},
        "marketfit":         {"tag": "STRATEGY",      "icon": "🎯", "desc": "Goal Alignment"},
        "strategy":          {"tag": "STRATEGY",      "icon": "🎯", "desc": "Task Execution"},
        "compliance":        {"tag": "OVERSIGHT",     "icon": "⚖️", "desc": "Policy & Governance"},
        "resilience":        {"tag": "STABILITY",     "icon": "🧬", "desc": "Stability & Testing"},
        "docs":              {"tag": "CLARITY",       "icon": "📄", "desc": "Knowledge Coverage"},
        "law":               {"tag": "LEGAL",         "icon": "📜", "desc": "Legal Compliance"},
        "investor":          {"tag": "VALUE",         "icon": "💰", "desc": "Asset Value"},
        "system":            {"tag": "CORE",          "icon": "⬛", "desc": "Core Integrity"},
        "frontend":          {"tag": "FRONTEND",      "icon": "🎨", "desc": "User Interface Fidelity"},
        "product readiness": {"tag": "PRODUCT",       "icon": "📦", "desc": "Go-to-Market Quality"},
        "live system":       {"tag": "SYSTEM",        "icon": "🌐", "desc": "Operational Health"},
        "code quality":      {"tag": "QUALITY",       "icon": "🧭", "desc": "Standard Compliance"},
    }

    @classmethod
    def get(cls, dimension: str) -> Dict[str, str]:
        """Get label data for a dimension, with fallback."""
        # Case-insensitive matching
        dim_clean = dimension.lower()
        if dim_clean in cls.REGISTRY:
            return cls.REGISTRY[dim_clean]
            
        # Fallback for unknown dimensions
        return {"tag": dimension.upper()[:10], "icon": "🧭", "desc": "Forensic Insight"}

    @classmethod
    def format_title(cls, dimension: str, title: str) -> str:
        """Format a title string with icon and tag: 🛡️ [SECURITY] Title"""
        data = cls.get(dimension)
        return f"{data['icon']} [{data['tag']}] {title}"

    @classmethod
    def format_terminal(cls, dimension: str, title: str) -> str:
        """Format for terminal output: [SECURITY] 🛡️ Title"""
        data = cls.get(dimension)
        return f"[{data['tag']}] {data['icon']} {title}"
