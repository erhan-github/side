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
            "fractal_root": local_data
        }
        
        # 4. Persist Master Index (ENCRYPTED)
        sovereign_file = self.project_path / ".side" / "sovereign.json"
        sovereign_file.parent.mkdir(parents=True, exist_ok=True)
        shield.seal_file(sovereign_file, json.dumps(sovereign_graph, indent=2))
        
        logger.info(f"🧠 [BRAIN]: Fractal Feed complete. Root Checksum: {local_data.get('checksum')}")
        return sovereign_graph

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
