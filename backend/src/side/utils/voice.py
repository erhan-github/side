"""
System Voice - The voice of the System Intelligence Engine.

Transforms generic audit results into conversational, high-fidelity findings
and machine-optimized actionable prompts.
"""

from typing import Any, List
from pathlib import Path

class SystemVoice:
    """Utility to inject context and density into audit findings."""

    @staticmethod
    def _clean_msg(result: Any) -> str:
        """Helper to get a clean, non-None message from result notes."""
        msg = result.notes if hasattr(result, 'notes') and result.notes and str(result.notes).lower() != "none" else ""
        
        # Aggressive Sanitization: Remove "None. " and duplicates
        import re
        msg = re.sub(r"^none\.\s*", "", str(msg), flags=re.IGNORECASE)
        
        # If notes were just the check name or redundant, return empty
        if msg.lower() == result.check_name.lower():
            return ""
        return msg.strip()

    @staticmethod
    def express_why(result: Any) -> str:
        """Generate prefix-free conversational discovery."""
        from side.utils.paths import mask_path
        file_loc = mask_path(None, human=True) # Default root
        if hasattr(result, 'evidence') and result.evidence:
            first_ev = result.evidence[0]
            if hasattr(first_ev, 'file_path') and first_ev.file_path:
                file_loc = mask_path(first_ev.file_path, human=True)
                if hasattr(first_ev, 'line_number') and first_ev.line_number:
                    file_loc = f"{file_loc}:{first_ev.line_number}"

        msg = SystemVoice._clean_msg(result)
        dim_key = result.check_id.split("-")[0].lower() if hasattr(result, 'check_id') and "-" in result.check_id else "logic"
        
        # Mapping for discovery
        if "SQL" in result.check_id or "Injection" in result.check_name:
             return f"Critical risk in {file_loc}. Direct data interpolation bypasses input sanitization layers, exposing the project to remote code execution or data exfiltration. Overall system reliability compromised."
        
        if "Secret" in result.check_name:
             return f"Security breach in {file_loc}. Hardcoded credentials expose sensitive environment gates. This compromises the isolation of the production environment."

        prefix = f"Logic anomaly in {file_loc}." if "CQ-" in result.check_id or "Logic" in result.check_id else f"Structural anomaly in {file_loc}."
        
        body = f" {msg}." if msg else ""
        
        # Category-Based Technical Impact (Zero Fluff)
        impacts = {
            "sec": " This increases the attack surface and compromises data integrity.",
            "perf": " This leads to resource exhaustion and degrades the system's operational efficiency.",
            "cq": " This introduces technical debt and reduces the long-term maintainability of the codebase.",
            "logic": " This introduces unpredictable state transitions and degrades system reliability.",
            "arch": " This violates structural constraints and complicates future system scaling.",
            "cq": " This introduces technical debt and reduces the long-term maintainability of the codebase.",
            "logic": " This introduces unpredictable state transitions and degrades system reliability.",
            "arch": " This violates structural constraints and complicates future system scaling.",
            "system": " This degrades system consistency and impacts long-term reliability.",
            "term": " This indicates runtime instability and disrupts the local development inner-loop."
        }
        impact = impacts.get(dim_key, impacts["system"])
        if "CQ-" in result.check_id:
             impact = impacts["cq"]
        if "TERM-" in result.check_id:
             impact = impacts["term"]

        return f"{prefix}{body}{impact}"

    @staticmethod
    def express_action(result: Any) -> str:
        """Generate prefix-free machine instruction."""
        from side.utils.paths import mask_path
        file_path = mask_path(None, human=False)
        loc_suffix = ""
        if hasattr(result, 'evidence') and result.evidence:
            first_ev = result.evidence[0]
            if hasattr(first_ev, 'file_path') and first_ev.file_path:
                file_path = mask_path(first_ev.file_path, human=False)
                if hasattr(first_ev, 'line_number') and first_ev.line_number:
                    loc_suffix = f":{first_ev.line_number}"

        recommendation = result.recommendation if hasattr(result, 'recommendation') and result.recommendation else "Review/Refactor"
        return f"Implement '{recommendation}' protocol to resolve '{result.check_name}' via {file_path}{loc_suffix}. [Hardened Logic | Zero Side-Effects]"

    @staticmethod
    def express_friendly(result: Any) -> str:
        """Generate empathy prefix."""
        if "SQL" in result.check_id or "Injection" in result.check_name:
             return "I've flagged code that requires hardening."
        if "Secret" in result.check_name:
             return "I've detected a security risk."
        if "CQ-" in result.check_id or "Logic" in result.check_id:
             return "I've identified a logic refinement."
        if "TERM-" in result.check_id or "Terminal" in result.check_name:
             return "I've analyzed your runtime velocity."
        return "I've detected a technical improvement."

    @staticmethod
    def express_fusion(result: Any) -> str:
        """
        Merge Empathy and Discovery into a single 'Top Notch' prompt.
        Pattern: 'Hey Chat! [Empathy] [Discovery] \n\n So my suggestion is that [Action].'
        """
        friendly = SystemVoice.express_friendly(result)
        why = SystemVoice.express_why(result)
        action = SystemVoice.express_action(result)
        
        return f"Hey Chat! {friendly} {why}\n\nSo my suggestion is that {action}"

    @classmethod
    def inject_fusion(cls, f_dict: dict) -> str:
        """Retrofit or normalize an existing finding."""
        # SYSTEM CHECK: If already perfectly fused AND fluff-free, preserve it.
        msg = f_dict.get('message', '')
        has_fusion = (msg.startswith("Hey Side!") or msg.startswith("Hey Chat!")) and "So my suggestion is that" in msg
        is_fluffy = any(f in msg.lower() for f in ["system quality", "system opportunity", "system risk", "structural friction"])
        
        if has_fusion and not is_fluffy:
            # User asked to "say Hey Chat", so migration is needed if it's "Hey Side"
            if msg.startswith("Hey Side!"):
                return msg.replace("Hey Side!", "Hey Chat!", 1)
            return msg
            
        from dataclasses import dataclass
        @dataclass
        class ResultMock:
            check_id: str
            check_name: str
            notes: str
            recommendation: str
            evidence: list
            
        meta = f_dict.get('metadata', {})
        
        # Recommendation Polish: ensure we don't 'Implement Implement'
        recommendation = f_dict.get('action', 'Review/Refactor')
        if recommendation.startswith("Implement '"):
             import re
             match = re.search(r"Implement '(.*?)' protocol", recommendation)
             if match:
                 recommendation = match.group(1)

        # Deep Sanitize Legacy Findings
        notes = meta.get('why_clean', '')
        if not notes:
             # Extract discovery part (between empathy and action)
             raw_discovery = msg.split("\n\n")[0] if "\n\n" in msg else msg
             
             # Multiline strip of known legacy headers/prefixes
             import re
             # 1. Strip Empathy & category headers globally
             notes = raw_discovery.replace("Hey Side!", "").replace("Hey Chat!", "").strip()
             empathy_fluff = [
                 "I've detected a technical improvement.",
                 "I've flagged code that requires hardening.",
                 "I've detected an integrity risk.",
                 "I've identified a logic refinement.",
                 "I found a strategic opportunity.",
                 "Everything looks great in Security!",
                 "Everything looks great in Logic!",
                 "Everything looks great in Performance!"
             ]
             for ef in empathy_fluff:
                  notes = notes.replace(ef, "")
             
             # 2. Strip Discovery headers globally (Anomaly found in...)
             # Aggressive block-level stripping
             notes = re.sub(r"(System Intelligence|Audit|Logic|Structural|Critical|Security)\s*(anomaly|risk|breach|rot|intelligence|Opportunity)\s*(found|detected|refinement|signals)\s*(in|at|detected|within)\s*.*?(:\d+)?\.\s*", "", notes, flags=re.IGNORECASE)
             notes = re.sub(r"Scanned \d+ .*? files with System Intelligence\.\s*", "", notes, flags=re.IGNORECASE)

             # 3. Strip all known fluff impact phrases (Global search & destroy)
             fluff_patterns = [
                 r"This creates structural friction and impacts the project's system quality\.?",
                 r"This creates technical friction and impacts the project's system quality\.?",
                 r"This creates structural friction and impacts the project's overall reliability\.?",
                 r"This increases the attack surface and compromises overall system security\.?",
                 r"This increases the attack surface and compromises data integrity\.?",
                 r"This leads to resource exhaustion and degrades the system's operational efficiency\.?",
                 r"This introduces technical debt and reduces the long-term maintainability of the codebase\.?",
                 r"This introduces unpredictable state transitions and degrades system reliability\.?",
                 r"This violates structural constraints and complicates future system scaling\.?",
                 r"This creates technical friction and impacts the project's overall reliability\.?",
                 r"This degrades system consistency and impacts long-term reliability\.?",
                 r"Unhandled edge cases degrade the system's reliability and increase long-term technical debt\.?",
                 r"Integrity breach detected in.*?\.\s*",
                 r"Strategic risk detected in.*?\.\s*",
                 r"Found \d+ endpoints, \d+ with visible auth\.?"
             ]
             for p in fluff_patterns:
                  notes = re.sub(p, "", notes, flags=re.IGNORECASE)
             
             # 4. Final path/line strip for any remaining artifacts
             notes = re.sub(r"^[^\s]*\.py(:\d+)?\.?\s*", "", notes.strip())
             # Clean up multiple dots and whitespace
             notes = re.sub(r"\.\s*\.", ".", notes)
             notes = notes.replace("..", ".").strip(". ")
        
        if not notes and msg and not msg.startswith("Hey Side!"):
             notes = msg
        
        if str(notes).lower() == "none" or notes == f_dict.get('type'): notes = ""

        mock = ResultMock(
            check_id=meta.get('check_id', f_dict.get('type', 'Unknown')),
            check_name=f_dict.get('type', 'Unknown'),
            notes=notes,
            recommendation=recommendation,
            evidence=[]
        )
        
        if f_dict.get('file'):
            @dataclass
            class EvMock:
                file_path: str
                line_number: int
            mock.evidence = [EvMock(file_path=f_dict['file'], line_number=f_dict.get('line', 0))]

        return cls.express_fusion(mock)

    @classmethod
    def fusion_literal(cls, emoji: str, category: str, discovery: str, suggestion: str) -> str:
        """Helper for literal fusion blocks."""
        is_nominal = "NOMINAL" in discovery.upper() or "Everything looks great" in discovery or "verified" in discovery.lower()
        if is_nominal and not any(char.isdigit() for char in discovery): # If it has digits like "10 anomalies", it's not nominal
            empathy = f"Logic gates verified in {category}."
        else:
            empathy = f"Operational signals detected in {category}."
            
        # Clean up suggestion to avoid quotes and "Hey Side/Chat" repetition
        clean_suggestion = suggestion.strip('"').strip("'")
        for prefix in ["hey side", "hey chat"]:
             if clean_suggestion.lower().startswith(prefix):
                 clean_suggestion = clean_suggestion[len(prefix):].strip(", ").strip()
        
        if clean_suggestion:
             clean_suggestion = clean_suggestion[0].upper() + clean_suggestion[1:]

        return f"Hey Chat! {empathy} {discovery}\n\nSo my suggestion is that {clean_suggestion}"

    @staticmethod
    def format_combined(result: Any) -> tuple[str, str, str, str]:
        """Convenience method for all modes + Fusion."""
        return (
            SystemVoice.express_why(result), 
            SystemVoice.express_action(result),
            SystemVoice.express_friendly(result),
            SystemVoice.express_fusion(result)
        )
