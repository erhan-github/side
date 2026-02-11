"""
Pattern Distiller - Intelligent analysis for strategic harvesting.
"""

import logging
from typing import List, Dict, Any
from side.storage.modules.substores.patterns import PublicPatternStore
from side.tools.audit_adapters import Finding

logger = logging.getLogger(__name__)

class PatternExtractor:
    def __init__(self, pattern_store: PublicPatternStore):
        self.store = pattern_store

    async def extract_audit_patterns(self, findings: List[Finding]):
        """
        Analyzes audit findings and logs them as anti-patterns
        if they exceed a certain confidence/severity threshold.
        """
        for finding in findings:
            # We only extract CRITICAL and HIGH findings as anti-patterns
            if finding.severity.value not in ["CRITICAL", "HIGH"]:
                continue
                
            if finding.confidence < 0.7:
                continue

            # Generate a context trigger
            context_trigger = f"{finding.tool}:{finding.rule_id}"
            risk = finding.explanation or finding.message
            
            remedy = {
                "suggested_fix": finding.suggested_fix,
                "rule_id": finding.rule_id,
                "tool": finding.tool
            }
            
            self.store.store_anti_pattern(
                issue_type="AUDIT_VIOLATION",
                context_trigger=context_trigger,
                risk_description=risk,
                remedy_json=remedy
            )
            logger.info(f"🎯 [PATTERN_EXTRACTOR]: Extracted pattern from {context_trigger}")
        
        logger.info(f"✨ [PATTERNS]: Extracted {len(findings)} patterns.")

    def extract_proven_pattern(self, intent: str, context_hash: str, fix_description: str, code_diff: str):
        """
        Logs a successful move as a 'Proven Pattern'.
        """
        pattern = {
            "description": fix_description,
            "code_diff": code_diff,
            "timestamp": "now"
        }
        
        self.store.store_architectural_move(
            intent=intent,
            context_hash=context_hash,
            pattern=pattern
        )
