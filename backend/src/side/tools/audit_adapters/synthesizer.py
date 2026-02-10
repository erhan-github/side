import logging
from typing import List, Dict, Any
from .base import Finding
from side.llm.client import LLMClient
from side.utils.llm_helpers import extract_json

logger = logging.getLogger(__name__)

class AuditSynthesizer:
    """
    Sidelith's Core Moat - The LLM Synthesis Layer.
    Transforms raw security scanner findings into contextual explanations and actionable fixes.
    """

    def __init__(self):
        # We use 'reasoning' purpose to get high-quality explanations
        self.llm = LLMClient(purpose="reasoning")

    async def synthesize(self, findings: List[Finding]) -> List[Finding]:
        """
        Enriches a list of findings with LLM-generated explanations and fixes.
        Uses batching to balance performance and quality.
        """
        if not findings:
            return []

        if not self.llm.is_available():
            logger.warning("⚠️ LLM not available for synthesis. Returning raw findings.")
            return findings

        # Batch findings in groups of 5 to avoid context limits and get better results
        batch_size = 5
        synthesized_findings = []

        for i in range(0, len(findings), batch_size):
            batch = findings[i:i + batch_size]
            logger.info(f"🧠 [SYNTHESIZER] Processing batch of {len(batch)} findings...")
            
            try:
                enriched_batch = await self._process_batch(batch)
                synthesized_findings.extend(enriched_batch)
            except Exception as e:
                logger.error(f"❌ Synthesis failed for batch: {e}")
                # Fallback: keep original findings for this batch
                synthesized_findings.extend(batch)

        return synthesized_findings

    async def _process_batch(self, findings: List[Finding]) -> List[Finding]:
        """Process a single batch of findings using the LLM."""
        
        # Prepare the context for the LLM
        findings_context = []
        for i, f in enumerate(findings):
            findings_context.append(f"""
FINDING #{i}:
Tool: {f.tool}
Rule: {f.rule_id}
File: {f.file_path}:{f.line}
Message: {f.message}
Code:
```
{f.code_snippet or "Snippet not available"}
```
""")

        system_prompt = """
Analyze security scanner findings and provide:
1. EXPLANATION: A concise, one-sentence explanation of the danger.
2. SUGGESTED_FIX: Precise code that resolves the issue.
3. PRIORITIZATION: Assessment of strategic impact.

RULES:
- Be technical and direct.
- Output strictly JSON objects.
- Ensure fixes are idiomatic and safe.

Format:
[
  {
    "explanation": "string",
    "suggested_fix": "string",
    "strategic_impact": "string"
  }
]
"""

        user_prompt = f"Analyze these {len(findings)} findings and provide synthesis:\n\n" + "\n".join(findings_context)

        messages = [{"role": "user", "content": user_prompt}]
        
        try:
            response_text = await self.llm.complete_async(messages, system_prompt)
            synthesis_data = extract_json(response_text)
            
            if not synthesis_data or not isinstance(synthesis_data, list):
                 logger.warning(f"⚠️ Failed to extract valid JSON list for synthesis.")
                 return findings

            # Map back to findings
            for i, data in enumerate(synthesis_data):
                if i < len(findings):
                    findings[i].explanation = data.get("explanation")
                    findings[i].suggested_fix = data.get("suggested_fix")
                    
                    impact = data.get("strategic_impact")
                    if impact:
                        if not findings[i].metadata:
                            findings[i].metadata = {}
                        findings[i].metadata["strategic_impact"] = impact

            return findings
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse LLM response for synthesis: {e}")
            return findings
