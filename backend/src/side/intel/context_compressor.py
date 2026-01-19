"""
Context Compressor for Side.

Handles intelligent context reduction for large-scale repositories
and long conversation histories.
"""

import json
import logging
import datetime
from datetime import timezone
from typing import Any, List, Dict

logger = logging.getLogger(__name__)

class ContextCompressor:
    """
    Intelligently compresses strategic context to fit LLM window limits.
    
    Priority Model:
    1. Question (Absolute Priority)
    2. Profile (Critical Context)
    3. Active Goals (Strategic Direction)
    4. Recent Decisions (Short-term Memory)
    5. Learnings (Synthesized Knowledge)
    6. Articles (Supporting Intelligence)
    """

    def __init__(self, token_limit: int = 30000):
        # 30k char limit is safe even for gemma2:9b (8k tokens approx)
        self.char_limit = token_limit

    def _is_recent(self, item: Dict[str, Any], now: datetime.datetime) -> bool:
        """Check if an item was created within the last 30 days."""
        created_at = item.get("created_at")
        if not created_at:
            return True
        try:
            # Handle both isoformat and potential Z
            ts = created_at.replace('Z', '+00:00')
            dt = datetime.datetime.fromisoformat(ts)
            return (now - dt).days < 30
        except Exception:
            return True

    def _get_total_len(self, *args: str) -> int:
        """Calculate total character length of multiple strings."""
        return sum(len(str(a)) for a in args)

    async def compress(
        self,
        question: str,
        profile: Dict[str, Any],
        decisions: List[Dict[str, Any]],
        goals: List[Dict[str, Any]],
        learnings: List[Dict[str, Any]],
        articles: List[Dict[str, Any]],
        recent_changes: str = ""
    ) -> Dict[str, str]:
        """
        Compresses context with [Dominance V2] Semantic Pruning.
        """
        now = datetime.datetime.now(timezone.utc)
        
        # 0. Semantic Pruning: Filter items older than 30 days unless they are 'Critical'
        decisions = [d for d in decisions if self._is_recent(d, now)]
        goals = [g for g in goals if self._is_recent(g, now) or g.get("priority", 0) > 5]
        learnings = [l for l in learnings if self._is_recent(l, now)]

        # 1. Essential context
        q_str = question.strip()
        p_str = json.dumps(profile, indent=2)
        
        # 2. Build blocks with 'Strategic Halflife' (Newest first)
        compressed_goals = self._format_list(goals, "Goal", max_items=5, recent_first=True)
        compressed_decisions = self._format_list(decisions, "Decision", max_items=8, recent_first=True)
        compressed_learnings = self._format_list(learnings, "Insight", max_items=5, recent_first=True)
        compressed_articles = self._format_list(articles, "Article", max_items=3, recent_first=True)

        total = self._get_total_len(q_str, p_str, compressed_goals, compressed_decisions, compressed_learnings, compressed_articles, recent_changes)

        if total > self.char_limit:
            logger.info(f"⚡ [GOD MODE] Context {total} > {self.char_limit}. Executing Intelligence Decay.")
            # Drop lowest priority first: Articles
            compressed_articles = "_[Articles truncated for space]_"
            
            total = self._get_total_len(q_str, p_str, compressed_goals, compressed_decisions, compressed_learnings, compressed_articles, recent_changes)
            if total > self.char_limit:
                # Drop older Learnings radically
                compressed_learnings = self._format_list(learnings, "Insight", max_items=2, recent_first=True)
                
                total = self._get_total_len(q_str, p_str, compressed_goals, compressed_decisions, compressed_learnings, compressed_articles, recent_changes)
                if total > self.char_limit:
                    # Radical compression: Limit Decisions to most recent 2
                    compressed_decisions = self._format_list(decisions, "Decision", max_items=2, recent_first=True)
        
        return {
            "question": q_str,
            "profile": p_str,
            "active_goals": compressed_goals,
            "past_decisions": compressed_decisions,
            "key_learnings": compressed_learnings,
            "articles": compressed_articles,
            "recent_changes": recent_changes[:5000]
        }

    def _format_list(self, items: List[Dict[str, Any]], label: str, max_items: int, recent_first: bool = False) -> str:
        """Format a list of items into a concise string, optionally prioritizing recent ones."""
        if not items:
            return f"No {label.lower()}s found."
        
        # Sort by created_at if possible
        if recent_first:
            try:
                working_items = sorted(items, key=lambda x: str(x.get("created_at", "")), reverse=True)
            except Exception:
                working_items = items
        else:
            working_items = items
        
        selected = working_items[:max_items]
        lines = []
        for i, item in enumerate(selected):
            content = item.get("question") or item.get("insight") or item.get("title") or str(item)
            if len(str(content)) > 300:
                content = content[:297] + "..."
            
            # Add a timestamp or indicator if possible
            date = str(item.get("created_at", ""))[:10] if item.get("created_at") else ""
            prefix = f"[{date}] " if date else ""
            lines.append(f"{i+1}. {prefix}{content}")
            
        if len(items) > max_items:
            lines.append(f"... and {len(items) - max_items} older/stale {label.lower()}s ignored for clarity.")
            
        return "\n".join(lines)
