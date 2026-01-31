"""
Forensics Package - OSS Security Tool Integration.

This package integrates proven open-source security tools:
- Semgrep (universal, primary)
- Bandit (Python-specific)
- ESLint (JavaScript/TypeScript)

Sidelith's value-add: LLM synthesis for remediation, not detection.
"""

from .base import ForensicsAdapter, Finding, Severity
from .semgrep import SemgrepAdapter
from .bandit import BanditAdapter
from .eslint import ESLintAdapter
from .gosec import GosecAdapter
from .swiftlint import SwiftLintAdapter
from .detekt import DetektAdapter
from .synthesizer import ForensicSynthesizer

__all__ = [
    "ForensicsAdapter",
    "Finding",
    "Severity",
    "SemgrepAdapter",
    "BanditAdapter",
    "ESLintAdapter",
    "GosecAdapter",
    "SwiftLintAdapter",
    "DetektAdapter",
    "ForensicSynthesizer"
]
