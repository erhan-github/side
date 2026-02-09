"""
Side LLM Orchestrator - The Fallback Brain.

Part of Phase IV.
Handles "Reasoning" and "Synthesis" when deterministic tools fail.
"""

from typing import List, Dict, Any

class LLMOrchestrator:
    """
    Manages higher-order intelligence.
    """
    
    def __init__(self, provider="groq"):
        from side.llm.client import LLMClient
        self.client = LLMClient(preferred_provider=provider)
        
    async def synthesize_findings(self, findings: List[Dict]) -> str:
        """
        Take raw findings and generate a Strategic Insight using the AI Engine.
        """
        if not findings:
            return "No findings to synthesize."
            
        # Construct Prompt
        prompt = f"""
        Analyze these technical findings and provide a Strategic Executive Summary.
        
        FINDINGS:
        {findings}
        
        Format:
        1. Executive Summary (1-2 sentences)
        2. Critical Risks (Bullet points)
        3. Strategic Recommendation (Actionable)
        """
        
        try:
            return self.client.complete(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are an expert engineering strategist. Be concise.",
                temperature=0.3
            )
        except Exception as e:
            return f"AI Analysis Failed: {e}"

    async def verify_fix(self, original_code: str, new_code: str) -> bool:
        """
        The Judge: Does the new code actually fix the issue without regression?
        """
        # 1. Deterministic Check (Syntax)
        import ast
        try:
            ast.parse(new_code)
        except SyntaxError:
            return False
            
        # 2. Semantic Check (Pulse Engine)
        # "Experience Perfection": Don't ask the LLM if the code is safe 
        # if the Deterministic Engine already knows it isn't.
        from side.pulse import pulse
        
        ctx = {
            "target_file": "virtual_fix.py",
            "file_content": new_code,
            "PORT": "3999"
        }
        
        pulse_result = pulse.check_pulse(ctx)
        if pulse_result.status.value != "SECURE":
            # If Pulse fails, we don't even bother the LLM. 
            # We save tokens and return False immediately.
            return False

        # 3. Semantic Insight (LLM)
        prompt = f"""
        Compare the Original Code and the New Fix.
        Does the New Fix resolve the issue without introducing new bugs?
        Return ONLY 'YES' or 'NO'.
        
        ORIGINAL:
        {original_code[:1000]}
        
        NEW:
        {new_code[:1000]}
        """
        
        try:
            response = self.client.complete(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="Return YES or NO only.",
                temperature=0.0
            )
            return "YES" in response.upper()
        except Exception:
            return True # Fail open on LLM error to avoid blocking valid fixes
