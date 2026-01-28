import logging
from pathlib import Path
from typing import Dict, Any, List
from side.intel.memory import MemoryManager
from side.llm.client import LLMClient
from side.utils.crypto import shield

logger = logging.getLogger(__name__)

class AutoIntelligence:
    """
    The 'Context Server'.
    Automatically monitors the user's focus and injects:
    1. Sovereign Memories (JSON).
    2. Strategic Artifacts (Markdown).
    3. Past Failures (Ledger).
    """

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.memory = MemoryManager(project_path)
        self.brain_path = project_path / ".side" / "brain"

    async def feed(self) -> Dict[str, Any]:
        """
        Actively scans the repository using the Fractal Engine (Protocol v3).
        Generates distributed .side/local.json context and rolls up to sovereign.json.
        """
        import json
        from datetime import datetime, timezone
        from side.intel.fractal_indexer import run_fractal_scan
        
        # 1. Run the Fractal Scan (Distributed Indexing)
        logger.info("🧠 [BRAIN]: Initiating Fractal Context Scan...")
        run_fractal_scan(self.project_path)
        
        # 2. Rollup to Monolith (For v1/v2 Compatibility)
        # We read the root local.json (ENCRYPTED) and wrap it as the Master Brain
        root_index_path = self.project_path / ".side" / "local.json"
        if not root_index_path.exists():
            return {"error": "Fractal Scan Failed"}
            
        raw_data = shield.unseal_file(root_index_path)
        local_data = json.loads(raw_data)
        
        # 3. Construct the Sovereign Graph (Legacy Wrapper)
        sovereign_graph = {
            "$schema": "./backend/src/side/schema/sovereign.schema.json",
            "version": "3.0.0 (Fractal)",
            "last_scan": datetime.now(timezone.utc).isoformat(),
            "dna": {
                "detected_stack": ["Detected via Fractal Tree"], # Todo: Extract from tree
                "primary_languages": []
            },
            "stats": {
                "nodes": len(local_data.get("context", {}).get("files", [])), # Approximate
                "mode": "Distributed"
            },
            "nodes": [], # Legacy nodes empty, tools must learn Protocol v3 walk
            "fractal_root": local_data,
            "history_fragments": []
        }
        
        # 4. Persist Master Index (ENCRYPTED)
        sovereign_file = self.project_path / ".side" / "sovereign.json"
        sovereign_file.parent.mkdir(parents=True, exist_ok=True)
        shield.seal_file(sovereign_file, json.dumps(sovereign_graph, indent=2))
        
        logger.info(f"🧠 [BRAIN]: Fractal Feed complete. Root Checksum: {local_data.get('checksum')}")
        return sovereign_graph

    async def historic_feed(self, months: int = 12) -> List[Dict[str, Any]]:
        """
        Phased Git Analysis: Extracts 'Historical Wisdom' from commits.
        Uses LLMClient to convert 'Raw Diffs' into 'Strategic Decisions'.
        """
        import subprocess
        from side.llm.client import LLMClient
        
        logger.info(f"🕰️ [TIME TRAVEL]: Mining last {months} months of repository soul...")
        
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

        llm = LLMClient()
        fragments = []
        
        for line in commits:
            try:
                h, author, date, msg = line.split("|", 3)
                
                # Get the diff for this commit
                diff_cmd = ["git", "show", "--pretty=format:", h]
                diff_res = subprocess.run(diff_cmd, cwd=self.project_path, capture_output=True, text=True)
                diff_content = diff_res.stdout[:4000] # Cap diff size for context efficiency
                
                # 2. Extract 'The Why' using LLM
                prompt = [
                    {"role": "user", "content": f"Commit: {msg}\nDiff:\n{diff_content}"}
                ]
                system = "Extract the 'Strategic Why' from this commit. Be concise. What architectural decision was made? Format: 'Decision: [Why we did it]'. Ignore trivialities."
                
                wisdom = await llm.complete_async(prompt, system, max_tokens=150)
                
                fragments.append({
                    "hash": h[:8],
                    "date": date,
                    "summary": msg,
                    "wisdom": wisdom.strip()
                })
                logger.info(f"✨ [MINED]: {h[:8]} - {msg[:30]}...")
            except Exception as e:
                logger.debug(f"Failed to mine commit: {e}")
                continue

        # 3. Update sovereign.json with fragments
        sovereign_file = self.project_path / ".side" / "sovereign.json"
        if sovereign_file.exists():
            import json
            raw = shield.unseal_file(sovereign_file)
            data = json.loads(raw)
            data["history_fragments"] = fragments
            shield.seal_file(sovereign_file, json.dumps(data, indent=2))
            
        return fragments

    def gather_context(self, active_file: str = None, topic: str = None) -> str:
        """
        Builds the 100% Context Prompt.
        """
        context_parts = []
        
        # 1. ARTIFACT INJECTION (The Strategy)
        # We look for key markdown files in the Brain or Root
        artifacts = ["VISION.md", "STRATEGY.md", "ARCHITECTURE.md"]
        for art in artifacts:
             # Check root
             p = self.project_path / art
             if p.exists():
                 context_parts.append(f"📜 [{art}]:\n{p.read_text()[:2000]}...") # Cap at 2k chars
             
             # Check brain
             # We might iterate over UUID folders if we knew the ID, but for now scan recursively?
             # Simple heuristic: Look in the generic brain folder if it existed, but here we assume root for Strategy.
        
        # 2. MEMORY RECALL (The Wisdom)
        query = f"{topic} {active_file}" if topic else str(active_file)
        memories = self.memory.recall(query)
        if memories:
            context_parts.append(memories)

        # 3. ACTIVE FILE (The Focus) - managed by caller usually, but we can add meta-data
        if active_file:
             context_parts.append(f"📍 [ACTIVE FOCUS]: User is working on '{active_file}'.")

        final_context = "\n\n".join(context_parts)
        return final_context
        
    def get_condensed_dna(self) -> str:
        """Extract a high-level architectural summary from the Fractal Index."""
        import json
        root_index = self.project_path / ".side" / "local.json"
        if not root_index.exists():
            return "DNA Not Found. Run 'side feed' to initialize."
            
        try:
            raw_data = shield.unseal_file(root_index)
            data = json.loads(raw_data)
            signals = data.get("dna", {}).get("signals", [])
            summary = f"Architectural DNA: {', '.join(signals)}\n"
            summary += f"Context Path: {data.get('path', 'root')}\n"
            # Add top-level folder digests
            folders = [k for k,v in data.get("children", {}).items()]
            summary += f"Derived Modules: {', '.join(folders)}"
            return summary
        except Exception as e:
            return f"Strategic DNA extraction failed: {e}"

    def enrich_system_prompt(self, base_prompt: str, context: str) -> str:
        """
        Dynamically rewrites the System Prompt with Context.
        """
        return f"""{base_prompt}

=== SOVEREIGN CONTEXT INJECTION ===
{context}
===================================
"""
