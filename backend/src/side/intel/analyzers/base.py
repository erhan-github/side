from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field

@dataclass
class Finding:
    """Structured finding from forensic analysis."""
    type: str          # 'SECURITY_PURITY', 'ARCH_PURITY', 'PERFORMANCE', etc.
    severity: str      # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    file: str          # Relative path from project root
    line: Optional[int]  # Line number if applicable
    message: str       # Human-readable description
    action: str        # Recommended fix
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        from dataclasses import asdict
        return asdict(self)

@dataclass
class CodeNode:
    """A node in the code graph (Class, Function, or Module)."""
    name: str
    type: str  # 'class', 'function', 'module'
    file_path: str
    start_line: int
    end_line: int
    complexity: int = 1
    docstring: bool = False
    dependencies: list[str] = field(default_factory=list)
    definitions: list[str] = field(default_factory=list)

class BaseAnalyzer(ABC):
    """Abstract base analyzer for code intelligence."""
    
    @abstractmethod
    async def analyze(self, root: Path, files: list[Path]) -> dict[str, Any]:
        """
        Perform analysis on the provided files.
        Returns a dict with 'code_graph' (dict of CodeNodes) and 'findings' (list of Findings).
        """
        pass
