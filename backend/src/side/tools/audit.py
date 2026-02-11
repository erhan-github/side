"""
Audit tool handler for Side.
Handles: run_audit
Implements System-level audit using OSS tools (Semgrep) + LLM synthesis.
"""

import logging
from pathlib import Path
from typing import Any
from side.tools.audit_adapters import SemgrepAdapter, Finding

from side.utils.paths import get_repo_root

logger = logging.getLogger(__name__)

async def handle_run_audit(arguments: dict[str, Any]) -> str:
    """
    Run Side System Audit using Polyglot OSS tools + LLM synthesis.
    
    Architecture:
    1. Detect project languages (fingerprinting)
    2. Run appropriate tools (Semgrep, Bandit, ESLint) in parallel
    3. Aggregate & Save findings
    4. LLM synthesizes remediation (Phase 4)
    """
    import asyncio
    from side.tools.core import get_engine
    from side.intel.language_detector import detect_primary_languages
    from side.tools.audit_adapters import (
        SemgrepAdapter, 
        BanditAdapter, 
        ESLintAdapter,
        GosecAdapter,
        SwiftLintAdapter,
        DetektAdapter,
        DocVerifyAdapter
    )
    
    dimension = arguments.get('dimension', 'general')
    severity_filter = arguments.get('severity', 'high,medium,critical').upper().split(',')
    project_path = get_repo_root()
    
    # Charge for Audit (10 SUs)
    from side.tools.core import get_engine
    db = get_engine()
    project_id = db.get_project_id()
    
    if not db.identity.charge_action(project_id, "SYSTEM_AUDIT"):
        return "🚫 [INSUFFICIENT FUNDS]: System Audit requires 10 SUs. Run 'side login' or upgrade."
    
    # 1. Detect Languages
    languages = detect_primary_languages(project_path)
    
    # 2. Select & Initialize Adapters
    adapters = [SemgrepAdapter(project_path), DocVerifyAdapter(project_path)] # Semgrep and DocVerify are polyglot baselines
    
    if "python" in languages:
        adapters.append(BanditAdapter(project_path))
    
    if "javascript" in languages or "typescript" in languages:
        adapters.append(ESLintAdapter(project_path))
    
    if "go" in languages:
        adapters.append(GosecAdapter(project_path))
        
    if "swift" in languages:
        adapters.append(SwiftLintAdapter(project_path))
        
    if "kotlin" in languages:
        adapters.append(DetektAdapter(project_path))
    
    print(f"🛡️  [AUDIT]: Initiating scan across {', '.join(languages)}...")
    print(f"🎯 [FILTER]: Severity in {severity_filter}")
    
    # 3. Handle JIT Installation
    active_adapters = []
    for adapter in adapters:
        if adapter.is_available():
            active_adapters.append(adapter)
        else:
            # Agentic JIT: Attempt to install any missing tool directly relevant to detected languages
            print(f"📦 [JIT INSTALL]: Installing missing audit probe '{adapter.get_tool_name()}'...")
            if adapter.install():
                active_adapters.append(adapter)
            else:
                # If install fails (e.g. no npm/brew), falling back to degraded warning
                print(f"❌ [DEGRADED]: Audit probe '{adapter.get_tool_name()}' install failed.")
                print(f"💡 {adapter.get_install_instructions()}")

    if not active_adapters:
        return "❌ [ERROR]: All audit probes failed. Please install Semgrep: pip install semgrep"

    # 3. Run Scans in Parallel
    print(f"🔍 [SCANNING]: Engaging {len(active_adapters)} probes in parallel...")
    tasks = [adapter.scan() for adapter in active_adapters]
    results = await asyncio.gather(*tasks)
    
    # 5. Aggregate Findings & Filter Severity
    all_findings = []
    for findings in results:
        # Filter findings based on severity argument
        filtered = [f for f in findings if f.severity.value in severity_filter]
        all_findings.extend(filtered)
    
    if not all_findings:
        return "✅ [SYSTEM AUDIT]: Project vitals are clean. No mission-critical issues found."

    print(f"🧠 [ANALYSIS]: Distilling top 20/{len(all_findings)} findings into patterns...")
    from side.tools.audit_adapters.synthesizer import AuditSynthesizer
    synthesizer = AuditSynthesizer()
    
    # Sort by severity (CRITICAL > HIGH > MEDIUM > LOW > INFO)
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
    all_findings.sort(key=lambda x: severity_order.get(x.severity.value, 5))
    
    findings_to_synthesize = all_findings[:20]
    synthesized_results = await synthesizer.synthesize(findings_to_synthesize)
    
    # Update the original list with synthesized results
    for i, sr in enumerate(synthesized_results):
        all_findings[i] = sr
    
    # 5. Save structured findings to database
    db = get_engine()
    project_id = db.get_project_id()
    
    saved_count = 0
    with db.engine.connection() as conn:
        for finding in all_findings:
            try:
                conn.execute("""
                    INSERT INTO audits (
                        project_id, tool, severity, message, file_path, 
                        rule_id, line_number, cwe_id, confidence,
                        explanation, suggested_fix
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_id,
                    finding.tool,
                    finding.severity.value,
                    finding.message,
                    finding.file_path,
                    finding.rule_id,
                    finding.line,
                    finding.cwe_id,
                    finding.confidence,
                    finding.explanation,
                    finding.suggested_fix
                ))
                saved_count += 1
            except Exception as e:
                logger.warning(f"Failed to save finding: {e}")
    
    # 6. Pattern Extraction (Phase 6)
    try:
        print("🎯 [PATTERNS]: Extracting architecture signals for your Pattern Store...")
        from side.intel.pattern_distiller import PatternDistiller
        distiller = PatternDistiller(db.strategic)
        await distiller.distill_audit_findings(all_findings)
    except Exception as e:
        logger.warning(f"Pattern extraction failed: {e}")

    # 7. Generate report using Standard Formatter
    from side.tools.formatting import format_audit_summary, format_audit_finding
    
    # Calculate stats
    critical_count = len([f for f in all_findings if f.severity.value == "CRITICAL"])
    high_count = len([f for f in all_findings if f.severity.value == "HIGH"])
    medium_count = len([f for f in all_findings if f.severity.value == "MEDIUM"])
    
    top_issue = all_findings[0].message if all_findings else "None"
    
    report = format_audit_summary(
        critical=critical_count,
        high=high_count,
        medium=medium_count,
        top_issue=top_issue,
        follow_ups=["View details in Strategic Database", "Run 'side strategy' for remediation plan"]
    )
    
    # Append top 5 findings details
    report += "\n\n"
    for finding in all_findings[:5]:
        report += format_audit_finding(
            finding_type=finding.message,
            severity=finding.severity.value,
            file_path=f"{finding.file_path}:{finding.line}",
            code_snippet=finding.code_snippet or "",
            fix=finding.suggested_fix or "See detailed report",
            risk=finding.explanation or "Potential risk identified",
            follow_up="Apply fix"
        )
        report += "\n"
    
    if len(all_findings) > 5:
        report += f"\n... and {len(all_findings) - 5} more issues saved to database."
    
    logger.info(f"✅ Saved {saved_count}/{len(all_findings)} findings from {len(active_adapters)} tools")
    
    return report

if __name__ == "__main__":
    import asyncio
    import sys
    
    args = {}
    if len(sys.argv) > 1:
        args['dimension'] = sys.argv[1]
    
    try:
        result = asyncio.run(handle_run_audit(args))
        print("\n" + result)
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
