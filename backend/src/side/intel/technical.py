from pathlib import Path
from typing import Any
from dataclasses import dataclass, field
from .analyzers.base import CodeNode, Finding
from .analyzers.git import GitAnalyzer
from .analyzers.dependencies import DependencyAnalyzer
from .analyzers.universal import UniversalAnalyzer

@dataclass
class TechnicalIntel:
    """Technical intelligence about a codebase (Backward兼容)."""
    languages: dict[str, int] = field(default_factory=dict)
    primary_language: str | None = None
    dependencies: dict[str, list[str]] = field(default_factory=dict)
    frameworks: list[str] = field(default_factory=list)
    code_graph: dict[str, CodeNode] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list) # Unified findings
    health_signals: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "languages": self.languages,
            "primary_language": self.primary_language,
            "dependencies": self.dependencies,
            "frameworks": self.frameworks,
            "code_graph_size": len(self.code_graph),
            "findings_count": len(self.findings),
            "health_signals": self.health_signals,
        }

class TechnicalAnalyzer:
    """Facade for modular analyzers."""
    
    def __init__(self):
        self.git = GitAnalyzer()
        self.deps = DependencyAnalyzer()
        self.universal = UniversalAnalyzer()

    async def analyze(self, path: str | Path) -> TechnicalIntel:
        root = Path(path).resolve()
        # Single-pass file collection
        all_files = list(root.rglob('*'))
        all_files = [f for f in all_files if f.is_file() and not any(p in f.parts for p in {'.git', 'node_modules', '.venv', '__pycache__', 'dist', 'build'})]
        
        # Parallel delegation
        git_res = await self.git.analyze(root, all_files)
        deps_res = await self.deps.analyze(root, all_files)
        univ_res = await self.universal.analyze(root, all_files)
        
        # Unified aggregation
        findings = univ_res.get("findings", [])
        findings.extend(git_res.get("findings", []))
        findings.extend(deps_res.get("findings", []))

        intel = TechnicalIntel(
            dependencies=deps_res["dependencies"],
            frameworks=deps_res["frameworks"],
            code_graph=univ_res.get("code_graph", {}),
            findings=findings
        )
        intel.health_signals["git"] = git_res.get("signals", {})
        
        return intel

import os # Need os for walk in facade
