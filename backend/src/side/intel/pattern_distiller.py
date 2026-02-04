"""
Wisdom Distiller - Intelligent analysis for pattern harvesting.
"""

import logging
from typing import List, Dict, Any
from side.storage.modules.pattern_store import PatternStore
from side.tools.forensics import Finding

logger = logging.getLogger(__name__)

class PatternDistiller:
    def __init__(self, pattern_store: PatternStore):
        self.store = pattern_store

    async def distill_audit_findings(self, findings: List[Finding]):
        """
        Analyzes forensic audit findings and logs them as anti-patterns
        if they exceed a certain confidence/severity threshold.
        """
        for finding in findings:
            # We only distill CRITICAL and HIGH findings as anti-patterns
            if finding.severity.value not in ["CRITICAL", "HIGH"]:
                continue
                
            if finding.confidence < 0.7:
                continue

            # Generate a context trigger based on file extension and rule_id
            # or a specific token in the message
            context_trigger = f"{finding.tool}:{finding.rule_id}"
            
            risk = finding.explanation or finding.message
            
            remedy = {
                "suggested_fix": finding.suggested_fix,
                "rule_id": finding.rule_id,
                "tool": finding.tool
            }
            
            self.store.store_anti_pattern(
                issue_type="FORENSIC_VIOLATION",
                context_trigger=context_trigger,
                risk_description=risk,
                remedy_json=remedy
            )
            logger.info(f"🍯 [DISTILLER]: Harvested anti-pattern from {context_trigger}")
        
        logger.info(f"✨ [PATTERNS]: Distilled context from {len(findings)} findings.")

    def distill_successful_fix(self, intent: str, context_hash: str, fix_description: str, code_diff: str):
        """
        Logs a successful architectural move as a 'Proven Pattern'.
        """
        pattern = {
            "description": fix_description,
            "code_diff": code_diff,
            "timestamp": "now" # In real use, this would be more detailed
        }
        
        self.store.store_architectural_move(
            intent=intent,
            context_hash=context_hash,
            pattern=pattern
        )
