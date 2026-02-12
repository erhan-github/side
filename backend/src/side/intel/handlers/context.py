import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from side.utils.crypto import shield

logger = logging.getLogger(__name__)

class PromptBuilder:
    """
    Constructs high-fidelity context prompts for LLM interactions.
    Optimized for 'Thin the Fat' architecture to minimize token overhead.
    """
    def __init__(self, project_path: Path, engine, strategic):
        self.project_path = project_path
        self.engine = engine
        self.plans = strategic
        self.token_budget = 16000 # Default budget for total context
        
    def gather_context(self, active_file: str = None, topic: str = None, include_code: bool = True) -> str:
        """
        Builds the 100% Context Prompt using a tiered retrieval strategy.
        """
        context_parts = []
        
        # 0. ANCHOR & ARTIFACTS (Low Fat Retrieval)
        self._add_strategic_artifacts(context_parts)

        # 1. HYBRID WISDOM & PATTERNS
        self._add_wisdom_and_patterns(context_parts, active_file, topic)

        # 2. LONG-TERM MEMORY (Recall)
        search_q = f"{topic} {active_file}" if topic else str(active_file)
        if search_q:
            project_id = self.engine.get_project_id()
            memories_raw = self.plans.recall_facts(query=search_q, project_id=project_id, limit=5)
            if memories_raw:
                summary = "🧠 [RECALLED CONTEXT]:\n"
                for m in memories_raw:
                    summary += f"- {m['content']} (Tags: {m['tags']})\n"
                context_parts.append(summary)

        # 3. ACTIVE FOCUS & SOURCE (Surgical)
        if active_file:
             context_parts.append(f"📍 [ACTIVE FOCUS]: User is working on '{active_file}'.")
             if include_code:
                 self._add_source_code(context_parts, active_file)

        return "\n\n".join(context_parts)

    def _add_strategic_artifacts(self, parts: List[str]):
        """Adds limited chunks of strategic artifacts."""
        anchor_path = self.project_path / "SYSTEM_ANCHOR.md"
        if anchor_path.exists():
             parts.append(f"⚓ [SYSTEM ANCHOR]:\n{anchor_path.read_text()[:4000]}")

        # Scale artifact reading based on type
        for art in ["VISION.md", "STRATEGY.md", "ARCHITECTURE.md"]:
             p = self.project_path / art
             if p.exists():
                 # For now, take first 2000 chars to avoid bloat
                 parts.append(f"📜 [{art}]:\n{p.read_text()[:2000]}...")

    def _add_wisdom_and_patterns(self, parts: List[str], active_file: str, topic: str):
        """Injects relevant wisdom and tool patterns."""
        search_q = f"{topic} {active_file}" if topic else str(active_file)
        if not search_q or len(search_q) < 3:
            return

        wisdom_hits = self.plans.search_wisdom(search_q, limit=3)
        if wisdom_hits:
            w_text = "\n".join([f"- {w['wisdom_text']} (Confidence: {w['confidence']})" for w in wisdom_hits])
            parts.append(f"🧠 [WISDOM]:\n{w_text}")
        
        try:
            from side.storage.modules.patterns import PatternStore
            pat_store = PatternStore(self.engine)
            pat_hits = pat_store.search_patterns(search_q, limit=2)
            if pat_hits:
                p_text = "\n".join([f"- {p['intent']}: {json.dumps(p['tool_sequence'])}" for p in pat_hits])
                parts.append(f"✨ [PATTERNS]:\n{p_text}")
        except Exception:
            pass

    def _add_source_code(self, parts: List[str], active_file: str):
        """Adds a surgical chunk of source code."""
        try:
            full_path = self.project_path / active_file
            if full_path.exists() and full_path.is_file():
                content = full_path.read_text()[:3000]
                parts.append(f"💻 [SOURCE CODE]:\n```\n{content}\n```")
        except Exception as e:
            logger.debug(f"Failed to inject source code: {e}")

    def get_surgical_context(self, query: str, limit: int = 3) -> str:
        """
        Surgical Attention: Finds most relevant code files based on semantic query.
        """
        try:
            candidates = []
            q_lower = query.lower()
            # Priority search paths
            search_roots = ["backend/src", "web/app", "web/lib", "web/components"]
            
            for root in search_roots:
                p = self.project_path / root
                if not p.exists(): continue
                for f in p.rglob("*"):
                    if not f.is_file(): continue
                    name = f.name.lower()
                    path_str = str(f).lower()
                    score = 0
                    if q_lower == name: score = 100
                    elif q_lower in name: score = 50
                    elif q_lower in path_str and f.suffix in ['.py', '.ts', '.tsx', '.md']: score = 10
                    
                    if score > 0:
                        rel_path = f.relative_to(self.project_path)
                        candidates.append((score, str(rel_path)))
            
            candidates.sort(key=lambda x: x[0], reverse=True)
            seen = set()
            unique_candidates = []
            for score, path in candidates:
                if path not in seen:
                    unique_candidates.append((score, path))
                    seen.add(path)
            
            top_files = unique_candidates[:limit]
            if not top_files:
                return f"- No direct code matches found for '{query}'."
                
            output = [f"## 3. SURGICAL CONTEXT (Matched '{query}'):"]
            for _, rel_path in top_files:
                full_path = self.project_path / rel_path
                if full_path.exists():
                    # Truncate content for surgical focus
                    content = full_path.read_text()[:2000]
                    output.append(f"\n### FILE: {rel_path}\n```\n{content}\n...\n```")
            return "\n".join(output)
        except Exception as e:
            return f"- [LAYER 3 ERROR]: Surgical retrieval failed: {e}"

    def get_episodic_context(self, audit, limit: int = 15, project_id: str = "global") -> str:
        """
        Retrieves recent context from the Ledger with Causal Threading.
        """
        try:
            from side.intel.session_analyzer import SessionAnalyzer
            analyzer = SessionAnalyzer(audit, self.plans)
            
            # Attempt to find current session for Enterprise-style threading
            latest = audit.get_recent_activities(project_id, limit=1)
            session_id = None
            if latest:
                # Handle both dict and object types from different stores
                session_id = latest[0].get('session_id') if isinstance(latest[0], dict) else getattr(latest[0], 'session_id', None)
            
            if session_id:
                return analyzer.get_causal_context(session_id, limit=limit)
            
            return analyzer.get_session_history(limit=limit)
        except Exception as e:
            logger.error(f"Episodic load failed: {e}")
            return f"## [RAM ERROR]: Failed to load episodic context: {e}"

    def get_ai_memory(self) -> str:
        """
        Derives the 'Truth' from Git status and recent commits.
        """
        try:
            import subprocess
            cmd_log = ["git", "log", "-n", "3", "--pretty=format:%h %s (%cr)"]
            log_out = subprocess.check_output(cmd_log, cwd=self.project_path, text=True, stderr=subprocess.STDOUT).strip()
            cmd_status = ["git", "status", "-s"]
            status_out = subprocess.check_output(cmd_status, cwd=self.project_path, text=True, stderr=subprocess.STDOUT).strip()
            
            state = "**Recent Commits (The Vector):**\n"
            for line in log_out.splitlines():
                state += f"- {line}\n"
            state += "\n**Active Measures (The Now):**\n"
            if status_out:
                for line in status_out.splitlines()[:5]:
                    state += f"- {line}\n"
            else:
                state += "- Clean Working Tree (Steady State).\n"
            return state
        except Exception as e:
            return f"- [ERROR] Could not derive AI Memory: {e}"

    async def refresh_context_for_file(self, path: Path):
        """Async hook for context invalidation/refresh."""
        logger.info(f"Refreshed context for {path.name}")
