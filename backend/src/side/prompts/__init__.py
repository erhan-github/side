"""
Unified Intelligence Hub - Sidelith Prompts.
"""

from .library import (
    GuardianPrompt,
    IntentAuditPrompt,
    ForensicsTask,
    SecurityAudit,
    CodeQuality,
    PerformanceCheck,
    SurpriseAnalysisPrompt,
    FactExtractionPrompt,
    ArchitecturalPivotPrompt,
    FocusDetectionPrompt,
    StrategicFrictionPrompt,
    ValueEstimationPrompt,
    TestGenerationPrompt,
    AuditSynthesisPrompt,
    StrategicInsightPrompt,
    FixVerifierPrompt,
    CommitAnalysisPrompt
)
from .personas import Personas
from .configs import LLMConfigs
from .registry import DynamicPromptManager, register_prompt_handlers

__all__ = [
    # --- Templates ---
    "GuardianPrompt",
    "IntentAuditPrompt",
    "ForensicsTask",
    "SecurityAudit",
    "CodeQuality",
    "PerformanceCheck",
    "SurpriseAnalysisPrompt",
    "FactExtractionPrompt",
    "ArchitecturalPivotPrompt",
    "FocusDetectionPrompt",
    "StrategicFrictionPrompt",
    "ValueEstimationPrompt",
    "TestGenerationPrompt",
    "AuditSynthesisPrompt",
    "StrategicInsightPrompt",
    "FixVerifierPrompt",
    "CommitAnalysisPrompt",

    # --- Engine ---
    "Personas",
    "LLMConfigs",
    "DynamicPromptManager",
    "register_prompt_handlers",
]
