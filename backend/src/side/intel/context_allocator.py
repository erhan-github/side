
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from side.intel.relevance_engine import Signal, RelevanceEngine

logger = logging.getLogger(__name__)

@dataclass
class ContextPacket:
    """The final, optimized context to be injected into the LLM."""
    signals: List[Signal]
    total_tokens: int
    budget_remaining: int
    focus_file: str
    relevance_scores: Dict[str, float]  # signal_id -> score

class ContextAllocator:
    """
    [ACE-2] The Token Budget Allocator.
    Fills a fixed token budget with the highest-value signals.
    Guarantees the output is NEVER over budget and ALWAYS maximally relevant.
    """
    
    DEFAULT_BUDGET = 8000  # Tokens

    def __init__(self, relevance_engine: RelevanceEngine, budget: int = DEFAULT_BUDGET):
        self.relevance_engine = relevance_engine
        self.budget = budget

    def allocate(
        self,
        signals: List[Signal],
        focus_file: str,
        focus_symbols: List[str] = None
    ) -> ContextPacket:
        """
        Allocates signals into an optimized context packet.
        
        Args:
            signals: All candidate signals from all sources.
            focus_file: The user's currently active file.
            focus_symbols: Symbols near the user's cursor.
        
        Returns:
            A ContextPacket containing the highest-value signals that fit the budget.
        """
        focus_symbols = focus_symbols or []
        
        # 1. Score all signals
        scored_signals = []
        for sig in signals:
            score = self.relevance_engine.score(sig, focus_file, focus_symbols)
            scored_signals.append((sig, score))
        
        # 2. Sort by score (descending)
        scored_signals.sort(key=lambda x: x[1], reverse=True)
        
        # 3. Greedily fill the budget
        selected_signals = []
        total_tokens = 0
        relevance_scores = {}
        
        for sig, score in scored_signals:
            if total_tokens + sig.token_cost <= self.budget:
                selected_signals.append(sig)
                total_tokens += sig.token_cost
                relevance_scores[f"{sig.source}:{sig.file_path}:{sig.timestamp}"] = score
            else:
                # Check if we can fit a smaller signal later
                continue
        
        logger.info(f"📦 [ALLOCATOR]: Selected {len(selected_signals)}/{len(signals)} signals. Tokens: {total_tokens}/{self.budget}")
        
        return ContextPacket(
            signals=selected_signals,
            total_tokens=total_tokens,
            budget_remaining=self.budget - total_tokens,
            focus_file=focus_file,
            relevance_scores=relevance_scores
        )

    def format_for_llm(self, packet: ContextPacket) -> str:
        """Formats the context packet into a prompt-ready string."""
        lines = [
            "=== ADAPTIVE CONTEXT (Ranked by Relevance) ===",
            f"📍 Focus: {packet.focus_file}",
            f"📊 Signals: {len(packet.signals)} | Tokens: {packet.total_tokens}",
            ""
        ]
        
        for sig in packet.signals:
            score = packet.relevance_scores.get(f"{sig.source}:{sig.file_path}:{sig.timestamp}", 0)
            lines.append(f"[{sig.source}] ({sig.severity}) [{score:.2f}] {sig.file_path}")
            lines.append(f"  {sig.content[:200]}...")
            lines.append("")
        
        lines.append("=== END CONTEXT ===")
        return "\n".join(lines)

if __name__ == "__main__":
    import time
    
    # Quick Test
    engine = RelevanceEngine({"auth.py": {"session.py", "token.py"}})
    allocator = ContextAllocator(engine, budget=500)
    
    signals = [
        Signal("FORENSIC", "session.py", "session.user can be None", "ERROR", time.time() - 30, ["Session", "user"], 100),
        Signal("LOG_SCAVENGER", "db.py", "Connection timeout", "WARNING", time.time() - 300, ["Database"], 80),
        Signal("SHADOW_INTENT", "auth.py", "User removed null check", "INFO", time.time() - 5, ["auth", "validate"], 150),
        Signal("STRATEGIC", "task.md", "P0: Fix auth flow", "INFO", time.time() - 3600, ["auth"], 50),
    ]
    
    packet = allocator.allocate(signals, "auth.py", ["validate", "Session"])
    print(allocator.format_for_llm(packet))
