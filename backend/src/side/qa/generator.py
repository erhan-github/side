import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional

from side.llm.client import LLMClient

logger = logging.getLogger(__name__)

class TestGenerator:
    """
    Generates reproduction test cases (Red Tests) from forensic findings.
    Part of the "Generative QA" (Software 2.0) pivot.
    """

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.llm = LLMClient()

    async def generate_repro(self, finding: Dict[str, Any]) -> str:
        """
        Generate a pytest reproduction script for a given finding.
        """
        issue_type = finding.get("check_name", "Unknown Issue")
        notes = finding.get("notes", "")
        evidence = finding.get("evidence", [])
        
        # Extract file context from evidence
        context_files = []
        code_snippets = ""
        
        for ev in evidence[:2]: # Limit context
            if isinstance(ev, dict):
                fpath = ev.get("file_path")
                line = ev.get("line_number")
            else:
                # Handle object attributes if evidence is a class
                fpath = getattr(ev, "file_path", None)
                line = getattr(ev, "line_number", None)
                
            if fpath:
                context_files.append(f"{fpath}:{line}")
                try:
                    # Quick read of the target file
                    full_path = self.project_path / fpath
                    if full_path.exists():
                        content = full_path.read_text()
                        # Extract surrounding lines? For now just header
                        code_snippets += f"\n--- {fpath} ---\n{content[:1000]}\n..."
                except Exception:
                    pass

        prompt = f"""You are a Senior QA Engineer specializing in TDD.
        
Context:
We have detected a potential issue in our codebase.
Issue Type: {issue_type}
Description: {notes}
Files: {', '.join(context_files)}

Code Snippet:
{code_snippets}

Task:
Write a SELF-CONTAINED Python script (using pytest) that attempts to REPRODUCE this issue.
- The test should FAIL if the issue is present (Red Test).
- The test should PASS if the issue is fixed.
- Mock external dependencies where possible.
- Output ONLY the python code for the test file. No markdown, no explanations.
"""
        
        try:
            logger.info(f"🧬 Generating Red Test for {issue_type}...")
            response = await self.llm.complete_async(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are a Forensic Code Auditor. Your output must be a strictly compliant, standalone Python reproduction script. No chatter.",
                temperature=0.1
            )
            return self._clean_code(response)
        except Exception as e:
            logger.error(f"❌ Failed to generate Red Test: {e}")
            return f"# [RED TEST FAILURE]\n# Error generating repro: {e}\n# Please manually verify {context_files}"

    def _clean_code(self, text: str) -> str:
        """Strip markdown code blocks."""
        if "```python" in text:
            text = text.split("```python")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return text.strip()
