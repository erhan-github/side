import logging
import json
from pathlib import Path
from side.utils.crypto import shield

logger = logging.getLogger(__name__)

class ContextHandler:
    def __init__(self, project_path: Path, engine, strategic, memory):
        self.project_path = project_path
        self.engine = engine
        self.strategic = strategic
        self.memory = memory

    def gather_context(self, active_file: str = None, topic: str = None, include_code: bool = True) -> str:
        """
        Builds the System Context Prompt.
        """
        context_parts = []
        
        # 0. ANCHOR LOGIC
        anchor_path = self.project_path / "SYSTEM_ANCHOR.md"
        if anchor_path.exists():
             context_parts.append(f"SYSTEM ANCHOR:\n{anchor_path.read_text()}")

        # 1. STRATEGIC ARTIFACTS
        artifacts = ["VISION.md", "STRATEGY.md", "ARCHITECTURE.md"]
        for art in artifacts:
             p = self.project_path / art
             if p.exists():
                 context_parts.append(f"[{art}]:\n{p.read_text()[:4000]}...")
        
        # 2. HYBRID SEARCH
        search_q = f"{topic} {active_file}" if topic else str(active_file)
        if search_q and len(search_q) > 3:
            wisdom_hits = self.strategic.search_wisdom(search_q, limit=3)
            if wisdom_hits:
                w_text = "\n".join([f"- {w['wisdom_text']} (Confidence: {w['confidence']})" for w in wisdom_hits])
                context_parts.append(f"WISDOM:\n{w_text}")
            
            try:
                from side.storage.modules.patterns import PatternStore
                pat_store = PatternStore(self.engine)
                pat_hits = pat_store.search_patterns(search_q, limit=2)
                if pat_hits:
                    p_text = "\n".join([f"- {p['intent']}: {json.dumps(p['tool_sequence'])}" for p in pat_hits])
                    context_parts.append(f"PATTERNS:\n{p_text}")
            except Exception:
                pass

        # 3. MEMORY RECALL
        memories = self.memory.recall(search_q)
        if memories:
            context_parts.append(memories)

        # 4. ACTIVE FOCUS
        if active_file:
             context_parts.append(f"ACTIVE FOCUS: User is working on '{active_file}'.")
             if include_code:
                 try:
                     full_path = self.project_path / active_file
                     if full_path.exists() and full_path.is_file():
                         content = full_path.read_text()[:3000]
                         context_parts.append(f"SOURCE CODE:\n```\n{content}\n```")
                 except Exception as e:
                     logger.debug(f"Failed to inject active file code: {e}")

        return "\n\n".join(context_parts)

    def get_surgical_context(self, query: str, limit: int = 3) -> str:
        """
        File Search: Finds most relevant code files.
        """
        try:
            candidates = []
            q_lower = query.lower()
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
                    elif q_lower in path_str and f.suffix in ['.py', '.ts', '.tsx']: score = 10
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
                return f"No code matches found for '{query}'."
                
            output = [f"## RELEVANT CODE (Matched '{query}'):"]
            for _, rel_path in top_files:
                full_path = self.project_path / rel_path
                if full_path.exists():
                    content = full_path.read_text()[:2000]
                    output.append(f"\n### FILE: {rel_path}\n```\n{content}\n...\n```")
            return "\n".join(output)
        except Exception as e:
            return f"Retrieval failed: {e}"

    def get_episodic_context(self, forensic, limit: int = 15) -> str:
        """
        Retrieves recent context from the Ledger.
        """
        try:
            from side.intel.episodic_projector import EpisodicProjector
            projector = EpisodicProjector(forensic, self.strategic)
            return projector.get_episode_stream(limit=limit)
        except Exception as e:
            return f"Failed to load episodic context: {e}"

    def get_git_status(self) -> str:
        """
        Derives operational status from Git.
        """
        try:
            import subprocess
            cmd_log = ["git", "log", "-n", "5", "--pretty=format:%h %s (%cr)"]
            log_out = subprocess.check_output(cmd_log, cwd=self.project_path, text=True).strip()
            cmd_status = ["git", "status", "-s"]
            status_out = subprocess.check_output(cmd_status, cwd=self.project_path, text=True).strip()
            reality = "**Recent Commits:**\n"
            for line in log_out.splitlines():
                reality += f"- {line}\n"
            reality += "\n**Current Status:**\n"
            if status_out:
                for line in status_out.splitlines()[:10]:
                    reality += f"- {line}\n"
            else:
                reality += "- Clean Working Tree.\n"
            return reality
        except Exception as e:
            return f"Could not derive git status: {e}"

    async def refresh_context_for_file(self, path: Path):
        """Placeholder for context refresh logic."""
        logger.info(f"Refreshed context for {path.name}")
        self.project_path = project_path
        self.engine = engine
        self.strategic = strategic
        self.memory = memory

    def gather_context(self, active_file: str = None, topic: str = None, include_code: bool = True) -> str:
        """
        Builds the 100% Context Prompt.
        """
        context_parts = []
        
        # 0. ANCHOR LOGIC
        anchor_path = self.project_path / "SYSTEM_ANCHOR.md"
        if anchor_path.exists():
             context_parts.append(f"⚓ [SYSTEM ANCHOR]:\n{anchor_path.read_text()}")

        # 1. STRATEGIC ARTIFACTS
        artifacts = ["VISION.md", "STRATEGY.md", "ARCHITECTURE.md"]
        for art in artifacts:
             p = self.project_path / art
             if p.exists():
                 context_parts.append(f"📜 [{art}]:\n{p.read_text()[:4000]}...")
        
        # 2. HYBRID SEARCH
        search_q = f"{topic} {active_file}" if topic else str(active_file)
        if search_q and len(search_q) > 3:
            wisdom_hits = self.strategic.search_wisdom(search_q, limit=3)
            if wisdom_hits:
                w_text = "\n".join([f"- {w['wisdom_text']} (Confidence: {w['confidence']})" for w in wisdom_hits])
                context_parts.append(f"🧠 [WISDOM]:\n{w_text}")
            
            try:
                from side.storage.modules.patterns import PatternStore
                pat_store = PatternStore(self.engine)
                pat_hits = pat_store.search_patterns(search_q, limit=2)
                if pat_hits:
                    p_text = "\n".join([f"- {p['intent']}: {json.dumps(p['tool_sequence'])}" for p in pat_hits])
                    context_parts.append(f"✨ [PATTERNS]:\n{p_text}")
            except Exception:
                pass

        # 3. MEMORY RECALL
        memories = self.memory.recall(search_q)
        if memories:
            context_parts.append(memories)

        # 4. ACTIVE FOCUS
        if active_file:
             context_parts.append(f"📍 [ACTIVE FOCUS]: User is working on '{active_file}'.")
             if include_code:
                 try:
                     full_path = self.project_path / active_file
                     if full_path.exists() and full_path.is_file():
                         content = full_path.read_text()[:3000]
                         context_parts.append(f"💻 [SOURCE CODE]:\n```\n{content}\n```")
                 except Exception as e:
                     logger.debug(f"Failed to inject active file code: {e}")

        return "\n\n".join(context_parts)

    def get_surgical_context(self, query: str, limit: int = 3) -> str:
        """
        Surgical Attention: Finds most relevant code files.
        """
        try:
            candidates = []
            q_lower = query.lower()
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
                    elif q_lower in path_str and f.suffix in ['.py', '.ts', '.tsx']: score = 10
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
                return f"- [LAYER 3]: No direct code matches found for '{query}' in the Live File System."
                
            output = [f"## 3. SURGICAL CONTEXT (Matched '{query}'):"]
            for _, rel_path in top_files:
                full_path = self.project_path / rel_path
                if full_path.exists():
                    content = full_path.read_text()[:2000]
                    output.append(f"\n### FILE: {rel_path}\n```\n{content}\n...\n```")
            return "\n".join(output)
        except Exception as e:
            return f"- [LAYER 3 ERROR]: Surgical retrieval failed: {e}"

    def get_episodic_context(self, forensic, limit: int = 15) -> str:
        """
        Retrieves recent context from the Ledger.
        """
        try:
            from side.intel.episodic_projector import EpisodicProjector
            projector = EpisodicProjector(forensic, self.strategic)
            return projector.get_episode_stream(limit=limit)
        except Exception as e:
            return f"## [RAM ERROR]: Failed to load episodic context: {e}"

    def _get_operational_reality(self) -> str:
        """
        Derives the 'Truth' from the actual code metrics.
        """
        try:
            import subprocess
            cmd_log = ["git", "log", "-n", "5", "--pretty=format:%h %s (%cr)"]
            log_out = subprocess.check_output(cmd_log, cwd=self.project_path, text=True).strip()
            cmd_status = ["git", "status", "-s"]
            status_out = subprocess.check_output(cmd_status, cwd=self.project_path, text=True).strip()
            reality = "**Recent Commits (The Vector):**\n"
            for line in log_out.splitlines():
                reality += f"- {line}\n"
            reality += "\n**Active Measures (The Now):**\n"
            if status_out:
                for line in status_out.splitlines()[:10]:
                    reality += f"- {line}\n"
            else:
                reality += "- Clean Working Tree (Steady State).\n"
            return reality
        except Exception as e:
            return f"- [ERROR] Could not derive Operational Reality: {e}"
