"""
Deep Security Probe - LLM-powered security analysis.

Uses Side Intelligence to find business logic vulnerabilities that static analysis misses.
"""

from typing import List
from pathlib import Path
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier

class DeepSecurityProbe:
    """Forensic-level deep security audit probe."""
    
    id = "forensic.deep_security"
    name = "Deep Semantic Security Scan"
    tier = Tier.DEEP
    dimension = "Security"
    
    async def run(self, context: ProbeContext) -> List[AuditResult]:
        if not context.llm_client or not context.llm_client.is_available():
            return [AuditResult(
                check_id="DEEP-SEC-000",
                check_name="Deep Security Analysis",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.INFO,
                notes="LLM Client not available or API Key missing"
            )]

        return [
            await self._check_semantic_vulnerabilities(context),
        ]

    async def _check_semantic_vulnerabilities(self, context: ProbeContext) -> AuditResult:
        """
        Scan for business logic vulnerabilities.
        Focuses on sensitive files (auth, payments, api).
        """
        evidence = []
        
        # 1. Select High-Risk Files
        high_risk_keywords = ['auth', 'login', 'payment', 'api', 'security', 'role', 'permission']
        candidates = []
        
        for file_path in context.files:
            # Simple keyword matching in filename
            if any(k in file_path.lower() for k in high_risk_keywords) and file_path.endswith(('.py', '.ts', '.js')):
                try:
                    candidates.append((file_path, Path(file_path).read_text()))
                except Exception:
                    pass

        if not candidates:
             return AuditResult(
                check_id="DEEP-SEC-001",
                check_name="Semantic Security Scan",
                dimension=self.dimension,
                status=AuditStatus.PASS,
                severity=Severity.LOW,
                notes="No high-risk files flagged for Deep Scan"
            )

        # Limit to top 3 for cost control
        candidates = candidates[:3]
        
        for file_path, content in candidates:
            try:
                prompt = f"""
                You are a Semantic Security Auditor. Analyze this code for BUSINESS LOGIC vulnerabilities.
                Ignore syntax errors. Look for:
                1. Authentication bypasses (e.g. returning early without checking password)
                2. Authorization flaws (e.g. checking `is_admin` but not enforcing it)
                3. IDOR (Insecure Direct Object References)
                4. Logic flaws in payment/critical flows
                
                File: `{file_path}`
                
                Code:
                ```
                {content[:5000]} 
                ```
                (Truncated to 5000 chars)
                
                Report CRITICAL logic flaws only. If safe, say "SAFE".
                """
                
                response = context.llm_client.complete(
                    messages=[{"role": "user", "content": prompt}],
                    system_prompt="You are a cynical security researcher. Assume the code is broken.",
                    temperature=0.0
                )
                
                if "SAFE" not in response and len(response) > 20:
                    evidence.append(AuditEvidence(
                        description=f"Potential Logic Vulnerability in {Path(file_path).name}",
                        file_path=file_path,
                        context=response[:500] + "...",
                        suggested_fix="Manual Security Review"
                    ))
                    
            except Exception as e:
                print(f"Deep Security Scan failed for {file_path}: {e}")
                continue

        return AuditResult(
            check_id="DEEP-SEC-001",
            check_name="Semantic Security Scan",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.CRITICAL,
            evidence=evidence,
            notes=f"Scanned {len(candidates)} high-risk files with Side Intelligence",
            recommendation="Conduct manual pentest on flagged files"
        )
