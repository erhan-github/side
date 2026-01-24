"""
Deep Logic Probe - LLM-powered logic verification.

Uses Side Intelligence (Llama 3) to understand code intent and find subtle bugs.
"""

from typing import List, Tuple
from pathlib import Path
import ast
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier

class DeepLogicProbe:
    """Forensic-level deep logic audit probe."""
    
    id = "forensic.deep_logic"
    name = "Deep Logic Audit"
    tier = Tier.DEEP
    dimension = "Code Quality"
    
    async def run(self, context: ProbeContext) -> List[AuditResult]:
        if not context.llm_client or not context.llm_client.is_available():
            return [AuditResult(
                check_id="DEEP-000",
                check_name="Deep Logic Analysis",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.INFO,
                notes="LLM Client not available or API Key missing"
            )]

        return [
            await self._check_logic_consistency(context),
        ]

    async def _check_logic_consistency(self, context: ProbeContext) -> AuditResult:
        """
        Ask LLM to verify if implementation matches docstring.
        Only scans high-complexity functions to save tokens.
        """
        evidence = []
        
        # 1. Identify "Complex" functions
        candidates = [] # List of (file_path, func_node, source_code)
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
                
            # Skip tests and generated code
            if 'test' in file_path.lower() or 'migration' in file_path.lower():
                continue
                
            try:
                content = Path(file_path).read_text()
                tree = ast.parse(content)
                lines = content.splitlines()
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Filter: Must have docstring AND be > 20 lines
                        docstring = ast.get_docstring(node)
                        if not docstring:
                            continue
                            
                        # Estimate complexity by length (fast heuristic)
                        length = node.end_lineno - node.lineno
                        if length < 20: 
                            continue
                            
                        # Extract source
                        func_source = "\n".join(lines[node.lineno-1:node.end_lineno])
                        candidates.append((file_path, node.name, func_source))
            except Exception:
                continue

        # 2. Select top 3 candidates (Cost Control)
        # In a real run, we might scan all, but strictly limit for now.
        if not candidates:
             return AuditResult(
                check_id="DEEP-001",
                check_name="Logic Consistency",
                dimension=self.dimension,
                status=AuditStatus.PASS,
                severity=Severity.LOW,
                notes="No complex functions found requiring Deep Scan"
            )
            
        candidates = candidates[:3]
        
        # 3. Analyze with LLM
        for file_path, func_name, code in candidates:
            try:
                prompt = f"""
                You are a Senior Python Auditor. Analyze this function for logic bugs and docstring inconsistencies.
                
                Function: `{func_name}` in `{file_path}`
                
                Code:
                ```python
                {code}
                ```
                
                Task:
                1. Does the implementation match the docstring?
                2. Are there any subtle edge-case bugs (off-by-one, NoneType, infinite recursion)?
                3. Is it insecure?
                
                Output specific actionable issues only. If clean, say "CLEAN".
                """
                
                response = context.llm_client.complete(
                    messages=[{"role": "user", "content": prompt}],
                    system_prompt="You are an expert code auditor. Be concise and critical.",
                    temperature=0.0
                )
                
                if "CLEAN" not in response and len(response) > 20:
                    evidence.append(AuditEvidence(
                        description=f"LLM Detected Issues in {func_name}",
                        file_path=file_path,
                        context=response[:200] + "...", # Truncate for report
                        suggested_fix="Review LLM analysis"
                    ))
                    
            except Exception as e:
                print(f"LLM Scan failed for {func_name}: {e}")
                continue

        return AuditResult(
            check_id="DEEP-001",
            check_name="Logic Consistency",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.HIGH,
            evidence=evidence,
            notes=f"Scanned {len(candidates)} complex functions with Side Intelligence",
            recommendation="Review functions flagged by Deep Logic Audit"
        )
