import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from side.llm.client import LLMClient
from side.utils.crypto import shield

logger = logging.getLogger(__name__)

class FeedHandler:
    def __init__(self, project_path: Path, engine, brain_path: Path, strategic):
        self.project_path = project_path
        self.engine = engine
        self.brain_path = brain_path
        self.strategic = strategic

    async def historic_feed(self, months: int = 3) -> List[Dict[str, Any]]:
        """
        Phased Git Analysis: Extracts 'Architectural Patterns' from commits.
        """
        logger.info(f"🕰️ [HISTORICAL]: Analyzing last {months} months of repository activity...")
        
        # 1. Get High-Entropy Commits (feat, fix, refactor, breaking)
        cmd = [
            "git", "log", 
            f"--since={months} months ago",
            "--pretty=format:%H|%an|%ad|%s",
            "--grep=feat\\|fix\\|refactor\\|breaking\\|chore(deps)",
            "--no-merges",
            "-n", "50" # Cap for Alpha
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_path, capture_output=True, text=True)
            commits = result.stdout.splitlines()
        except Exception as e:
            logger.error(f"Git log failed: {e}")
            return []

        llm = LLMClient(purpose="intelligence")
        project_id = self.engine.get_project_id()
        fragments = []
        
        for line in commits:
            try:
                h, author, date, msg = line.split("|", 3)
                
                # Get the diff for this commit
                diff_cmd = ["git", "show", "--pretty=format:", h]
                diff_res = subprocess.run(diff_cmd, cwd=self.project_path, capture_output=True, text=True)
                diff_content = diff_res.stdout
                
                # --- TIERED INFERENCE LOGIC ---
                # Tier 0: AST Symbol Extraction (Local Heuristic)
                modified_symbols = self._extract_symbols(diff_content)
                
                # Gating: If no symbols modified (just comments/logs) and no high-entropy keywords
                high_entropy_keywords = ["sec", "auth", "fix", "breaking", "api", "infra"]
                is_high_entropy = any(kw in msg.lower() for kw in high_entropy_keywords)
                
                if not modified_symbols and not is_high_entropy:
                    logger.info(f"⏭️ [GATED]: Skipping LLM for routine commit {h[:8]} ('{msg[:30]}')")
                    continue

                # Tier 2: Strategic Boost (LLM Analysis)
                est_tokens_in = min(3500, len(diff_content))
                est_tokens_out = 150
                
                if not self.engine.accounting.deduct_task_su(
                    project_id=project_id,
                    task_type="semantic_boost",
                    llm_tokens_in=est_tokens_in,
                    llm_tokens_out=est_tokens_out,
                    llm_model="llama-3.1-70b-versatile",
                    operations=["ast_extraction", "intent_correlation"],
                    value_delivered={"objective_advanced": True} if is_high_entropy else {}
                ):
                    logger.warning(f"⚠️ [ECONOMY]: Skipping boost for {h[:8]} due to zero balance.")
                    continue

                # --- TECH-04: INTENT CORRELATION ---
                correlated_objectives = self.strategic.find_objectives_by_symbols(project_id, modified_symbols)
                objective_titles = [obj['title'] for obj in correlated_objectives]

                prompt = [
                    {"role": "user", "content": f"Commit: {msg}\nSymbols: {modified_symbols}\nAligned Objectives: {objective_titles}\nDiff (Truncated):\n{diff_content[:3000]}"}
                ]
                system = (
                    "Analyze the provided git commit and extract the 'Strategic Why'. "
                    "Focus on architectural decisions and intentional changes. "
                    "Ignore routine boilerplate, log additions, or trivial formatting. "
                    "Format: 'Decision: [Why this change was made and its strategic value]'. "
                    "Be concise and technical."
                )
                
                reasoning = await llm.complete_async(prompt, system, max_tokens=150)
                
                fragments.append({
                    "hash": h[:8],
                    "date": date,
                    "summary": msg,
                    "symbols": modified_symbols,
                    "aligned_objectives": [obj['id'] for obj in correlated_objectives],
                    "reasoning": reasoning.strip()
                })
                logger.info(f"✨ [BOOSTED]: {h[:8]} - {msg[:30]} (Aligned: {len(correlated_objectives)})")
            except Exception as e:
                logger.debug(f"Failed to mine commit: {e}")
                continue

        # 3. Update project_metadata.json with fragments
        metadata_file = self.project_path / ".side" / "project_metadata.json"
        if metadata_file.exists():
            import json
            raw = shield.unseal_file(metadata_file)
            data = json.loads(raw)
            data["history_fragments"] = fragments
            shield.seal_file(metadata_file, json.dumps(data, indent=2))
            
        return fragments

    def _extract_symbols(self, diff_content: str) -> List[str]:
        """
        Uses native Python AST to find which functions or classes were modified in a diff.
        """
        import re
        symbols = set()
        
        lines = diff_content.splitlines()
        for line in lines:
            if line.startswith("+") and not line.startswith("+++"):
                match = re.search(r"\b(def|class|func|function|fun)\s+([a-zA-Z_][a-zA-Z0-9_]*)", line)
                if match:
                    symbols.add(match.group(2))
        
        return list(symbols)

    async def incremental_feed(self, file_path: Path):
        """
        [KAR-8.2] Incremental Strategic Sync.
        """
        logger.info(f"⚡ [BRAIN]: Incremental sync triggered for {file_path.name}")
        
        if "task.md" in file_path.name or "WALKTHROUGH.md" in file_path.name:
            from side.intel.bridge import BrainBridge
            bridge = BrainBridge(self.brain_path)
            nodes = bridge.scan_nodes()
            
            from side.utils.context_cache import ContextCache
            cache = ContextCache(self.project_path, self.engine)
            cache.generate(force=True)
            logger.info("✨ [BRAIN]: Context cache regenerated from database.")
