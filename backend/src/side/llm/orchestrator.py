from typing import List, Dict
from side.prompts import (
    Personas, 
    LLMConfigs, 
    StrategicInsightPrompt, 
    FixVerifierPrompt
)

class LLMOrchestrator:
    """
    Manages higher-order intelligence.
    """
    
    def __init__(self, provider="groq"):
        from side.llm.client import LLMClient
        self.client = LLMClient(preferred_provider=provider)
        self.insight_config = LLMConfigs.get_config("strategic_insight")
        self.fix_config = LLMConfigs.get_config("fix_verifier")
        
    async def synthesize_findings(self, findings: List[Dict]) -> str:
        """
        Take raw findings and generate a Strategic Insight using the AI Engine.
        """
        if not findings:
            return "No findings to synthesize."
            
        # Construct Prompt
        prompt = StrategicInsightPrompt.format(findings=findings)
        
        try:
            return self.client.complete(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=Personas.STRATEGIC_STRATEGIST,
                **self.insight_config
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
        from side.pulse import pulse
        
        ctx = {
            "target_file": "virtual_fix.py",
            "file_content": new_code,
            "PORT": "3999"
        }
        
        pulse_result = pulse.check_pulse(ctx)
        if pulse_result.status.value != "SECURE":
            return False

        # 3. Semantic Insight (LLM)
        prompt = FixVerifierPrompt.format(
            original_code=original_code[:1000],
            new_code=new_code[:1000]
        )
        
        try:
            response = self.client.complete(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=Personas.FIX_JUDGE,
                **self.fix_config
            )
            return "YES" in response.upper()
        except Exception:
            return True # Fail open on LLM error
