
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Signal:
    """A single intelligence signal from any source."""
    source: str          # e.g., "FORENSIC", "LOG_SCAVENGER", "SHADOW_INTENT"
    file_path: str       # The file this signal relates to (if any)
    content: str         # The actual data (error message, code snippet, etc.)
    severity: str        # "CRITICAL", "ERROR", "WARNING", "INFO"
    timestamp: float     # Unix timestamp
    symbols: List[str]   # Mentioned functions/classes ["auth", "Session.user"]
    token_cost: int      # Estimated tokens for this signal

class RelevanceEngine:
    """
    [ACE-1] The Relevance Scorer.
    Scores signals by semantic distance to the user's focus.
    Higher score = more relevant. Range: 0.0 to 1.0.
    """
    
    # Weights for scoring factors
    WEIGHT_IMPORT_DISTANCE = 0.35
    WEIGHT_RECENCY = 0.25
    WEIGHT_SEVERITY = 0.25
    WEIGHT_SYMBOL_MATCH = 0.15

    def __init__(self, dependency_graph: Dict[str, Set[str]] = None):
        """
        Args:
            dependency_graph: A dict mapping file_path -> set of imported file_paths.
                              Pre-computed from the Fractal Index.
        """
        self.dependency_graph = dependency_graph or {}

    def score(self, signal: Signal, focus_file: str, focus_symbols: List[str] = None) -> float:
        """
        Scores a signal based on its relevance to the current focus.
        
        Args:
            signal: The signal to score.
            focus_file: The user's currently active file.
            focus_symbols: Symbols near the user's cursor (function names, etc.)
        
        Returns:
            A float between 0.0 and 1.0.
        """
        focus_symbols = focus_symbols or []
        
        # 1. Import Distance Score
        import_score = self._score_import_distance(signal.file_path, focus_file)
        
        # 2. Recency Score (last 60s = 1.0, decays over 10 minutes)
        recency_score = self._score_recency(signal.timestamp)
        
        # 3. Severity Score
        severity_score = self._score_severity(signal.severity)
        
        # 4. Symbol Match Score
        symbol_score = self._score_symbol_match(signal.symbols, focus_symbols, focus_file)
        
        # Weighted Sum
        final_score = (
            self.WEIGHT_IMPORT_DISTANCE * import_score +
            self.WEIGHT_RECENCY * recency_score +
            self.WEIGHT_SEVERITY * severity_score +
            self.WEIGHT_SYMBOL_MATCH * symbol_score
        )
        
        return min(1.0, max(0.0, final_score))

    def _score_import_distance(self, signal_file: str, focus_file: str) -> float:
        """Files in the direct dependency chain score 1.0. Distance degrades."""
        if not signal_file or not focus_file:
            return 0.3  # Generic signal, some relevance
        
        if signal_file == focus_file:
            return 1.0  # Same file = maximum relevance
        
        # Check direct imports
        focus_deps = self.dependency_graph.get(focus_file, set())
        if signal_file in focus_deps:
            return 0.9  # Direct import
        
        # Check reverse imports (files that import focus_file)
        for file, deps in self.dependency_graph.items():
            if focus_file in deps and file == signal_file:
                return 0.85  # Reverse dependency
        
        # Check 2nd-degree imports
        for dep in focus_deps:
            if signal_file in self.dependency_graph.get(dep, set()):
                return 0.6  # 2nd-degree import
        
        return 0.2  # Unrelated file

    def _score_recency(self, timestamp: float) -> float:
        """Signals from the last 60s score 1.0. Decays over 10 minutes."""
        age_seconds = time.time() - timestamp
        if age_seconds < 60:
            return 1.0
        elif age_seconds < 600:  # 10 minutes
            return 1.0 - (age_seconds - 60) / 540  # Linear decay
        else:
            return 0.1  # Old but not zero

    def _score_severity(self, severity: str) -> float:
        """CRITICAL = 1.0, ERROR = 0.8, WARNING = 0.5, INFO = 0.2."""
        severity_map = {
            "CRITICAL": 1.0,
            "FATAL": 1.0,
            "ERROR": 0.8,
            "WARNING": 0.5,
            "WARN": 0.5,
            "INFO": 0.2,
            "DEBUG": 0.1,
        }
        return severity_map.get(severity.upper(), 0.3)

    def _score_symbol_match(self, signal_symbols: List[str], focus_symbols: List[str], focus_file: str) -> float:
        """Score higher if the signal mentions the same symbols the user is looking at."""
        if not signal_symbols:
            return 0.3
        
        # Extract focus file basename (e.g., "auth" from "auth.py")
        focus_name = Path(focus_file).stem if focus_file else ""
        
        matches = 0
        total_checks = len(focus_symbols) + 1  # +1 for focus_name
        
        # Check if any signal symbol matches focus file name
        for sym in signal_symbols:
            if focus_name and focus_name.lower() in sym.lower():
                matches += 1
                break
        
        # Check symbol overlap
        focus_set = set(s.lower() for s in focus_symbols)
        signal_set = set(s.lower() for s in signal_symbols)
        matches += len(focus_set & signal_set)
        
        return min(1.0, matches / max(1, total_checks))

if __name__ == "__main__":
    # Quick Test
    engine = RelevanceEngine({"auth.py": {"session.py", "token.py"}})
    
    signal = Signal(
        source="FORENSIC",
        file_path="session.py",
        content="session.user can be None",
        severity="ERROR",
        timestamp=time.time() - 30,  # 30 seconds ago
        symbols=["Session", "user"],
        token_cost=50
    )
    
    score = engine.score(signal, "auth.py", ["Session", "validate"])
    print(f"Relevance Score: {score:.2f}")
