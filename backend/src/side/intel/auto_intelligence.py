import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import ast
from datetime import datetime, timezone
from side.intel.memory import MemoryManager
from side.llm.client import LLMClient
from side.utils.crypto import shield
from side.intel.bridge import BrainBridge

logger = logging.getLogger(__name__)

class AutoIntelligence:
    """
    The 'Context Server'.
    Automatically monitors the user's focus and injects:
    1. Sovereign Memories (JSON).
    2. Strategic Artifacts (Markdown).
    3. Past Failures (Ledger).
    """

    def __init__(self, project_path: Path, buffer=None):
        import os
        from side.storage.modules.base import SovereignEngine
        from side.storage.modules.strategic import StrategicStore
        from side.storage.modules.forensic import ForensicStore
        from side.storage.modules.mmap_store import MmapStore
        self.project_path = project_path
        self.engine = SovereignEngine()
        self.strategic = StrategicStore(self.engine)
        self.forensic = ForensicStore(self.engine)
        self.buffer = buffer
        self.mmap = MmapStore(project_path)
        self.memory = MemoryManager(self.strategic, project_id=self.engine.get_project_id())
        
        # [KAR-4]: Universal Brain Path Discovery
        # Primary: Standard Antigravity Path (~/.gemini/antigravity/brain)
        # Fallback: Environment Variable (for dev/CI)
        env_brain = os.getenv("SIDE_BRAIN_PATH")
        antigravity_brain = Path.home() / ".gemini" / "antigravity" / "brain"
        
        self.brain_path = Path(env_brain) if env_brain else antigravity_brain

    async def feed(self) -> Dict[str, Any]:
        """
        Actively scans the repository using the Fractal Engine (Protocol v3).
        Generates distributed .side/local.json context and rolls up to sovereign.json.
        """
        from side.intel.fractal_indexer import run_fractal_scan
        
        # 1. Run the Fractal Scan (Distributed Indexing)
        start_time = time.time()
        logger.info("🧠 [BRAIN]: Initiating Parallel Fractal Context Scan...")
        run_fractal_scan(self.project_path)
        scan_duration = time.time() - start_time
        logger.info(f"🧠 [BRAIN]: Scan completed in {scan_duration:.2f}s.")
        
        # 2. Re-gen the Checkpoint (The Weights)
        sovereign_graph = await self.sync_checkpoint()
        
        # 5. Harvest Documentation DNA [KAR-4]
        await self._harvest_documentation_dna()
        
        # 6. [INTEL-4] Sync Mmap Store for NEON Acceleration
        await self._sync_mmap_wisdom()
        
        return sovereign_graph

    async def sync_checkpoint(self) -> Dict[str, Any]:
        """
        [KARPATHY PROTOCOL]: Serializes the current 'Weights' to sovereign.json.
        Acts as the Model Checkpoint for Amnesia Recovery.
        """
        import json
        
        # 1. Load context from fractal root
        root_index_path = self.project_path / ".side" / "local.json"
        local_data = {}
        if root_index_path.exists():
            raw_data = shield.unseal_file(root_index_path)
            local_data = json.loads(raw_data)
        
        project_id = self.engine.get_project_id()
        bridge = BrainBridge(self.brain_path)
        strategic_timeline = bridge.scan_nodes()
        
        # 2. Gather State (The Weights)
        plans = self.strategic.list_plans(project_id)
        objectives = [p for p in plans if p['type'] == 'objective' and p['status'] != 'done']
        tasks = [p for p in plans if p['type'] == 'task' and p['status'] != 'done']
        activities = self.forensic.get_recent_activities(project_id, limit=10)
        
        sovereign_graph = {
            "$schema": "./backend/src/side/schema/sovereign.schema.json",
            "version": "3.1.0 (Unified HUD Edition)",
            "last_scan": datetime.now(timezone.utc).isoformat(),
            "dna": {
                "detected_stack": ["M2 Pro Accelerated"], 
                "primary_languages": []
            },
            "intent": {
                "objectives": objectives,
                "directives": tasks,
                "latest_destination": "Peru Summit v1.0",
                "intel_signals": activities
            },
            "stats": {
                "nodes": len(local_data.get("context", {}).get("files", [])),
                "mode": "Distributed"
            },
            "fractal_root": local_data,
            "history_fragments": [],
            "strategic_timeline": strategic_timeline
        }
        
        # 3. Persist Master Checkpoint (The Weights)
        sovereign_file = self.project_path / ".side" / "sovereign.json"
        sovereign_file.parent.mkdir(parents=True, exist_ok=True)
        shield.seal_file(sovereign_file, json.dumps(sovereign_graph, indent=2))
        
        logger.debug("💾 [CHECKPOINT]: Sovereign Weights serialized.")
        return sovereign_graph

    async def _sync_mmap_wisdom(self):
        """Syncs public wisdom to Mmap Store for NEON acceleration."""
        try:
            wisdom = self.strategic.list_public_wisdom()
            fragments = []
            for w in wisdom:
                sig_hash = w.get('signal_hash')
                w_id = w.get('id')
                if sig_hash is not None and w_id:
                    import uuid
                    try:
                        uuid_obj = uuid.UUID(w_id)
                        fragments.append((sig_hash, uuid_obj.bytes))
                    except:
                        continue
            
            if fragments:
                 self.mmap.sync_from_ledger(fragments)
        except Exception as e:
            logger.warning(f"MMAP Sync Failed: {e}")


    async def incremental_feed(self, file_path: Path):
        """
        [KAR-8.2] Incremental Strategic Sync.
        Handles instant ingestion of focused artifacts (task.md, walkthroughs).
        """
        logger.info(f"⚡ [BRAIN]: Incremental sync triggered for {file_path.name}")
        
        # 1. Surgical Harvest
        if "task.md" in file_path.name or "WALKTHROUGH.md" in file_path.name:
            # We refresh the Strategic Timeline in the master graph
            bridge = BrainBridge(self.brain_path)
            nodes = bridge.scan_nodes()
            
            sovereign_file = self.project_path / ".side" / "sovereign.json"
            if sovereign_file.exists():
                import json
                raw = shield.unseal_file(sovereign_file)
                data = json.loads(raw)
                data["strategic_timeline"] = nodes
                data["last_scan"] = datetime.now(timezone.utc).isoformat()
                shield.seal_file(sovereign_file, json.dumps(data, indent=2))
                logger.info("✨ [BRAIN]: Strategic Timeline synced to Sovereign Anchor.")
            
        # 2. DNA Harvest (Wisdom)
        if file_path.suffix == ".md":
             await self._harvest_single_doc(file_path)

    async def _harvest_single_doc(self, file_path: Path):
        """Harvests wisdom from a single markdown file."""
        from side.utils.hashing import sparse_hasher
        import uuid
        try:
            content = file_path.read_text()
            sections = content.split("\n#")
            project_id = self.engine.get_project_id()
            
            for section in sections:
                if len(section.strip()) < 50: continue
                sig_hash = sparse_hasher.fingerprint(section, salt=project_id)
                fragment_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{file_path.name}:{sig_hash}"))
                
                with self.engine.connection() as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO public_wisdom (
                            id, origin_node, category, signal_pattern, 
                            signal_hash, wisdom_text, source_type, source_file, confidence
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (fragment_id, "local", "documentation", file_path.name,
                          sig_hash, section[:1000].strip(), "documentation", str(file_path), 9))
            logger.info(f"🦅 [DNA]: Harvested fragments from {file_path.name}")
        except Exception as e:
            logger.warning(f"Failed to harvest {file_path.name}: {e}")

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
                # We only reach here if it's high-entropy or has symbol changes
                
                # Calculate dynamic SU cost using Groq (MVP)
                est_tokens_in = min(3500, len(diff_content))
                est_tokens_out = 150
                
                if not self.engine.accounting.deduct_task_su(
                    project_id=project_id,
                    task_type="semantic_boost",
                    llm_tokens_in=est_tokens_in,
                    llm_tokens_out=est_tokens_out,
                    llm_model="llama-3.1-70b-versatile",  # Groq for MVP
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
                system = "Extract the 'Strategic Why' from this commit. Be concise. What architectural decision was made? Format: 'Decision: [Why we did it]'. If it aligns with objectives, mention how. Ignore trivialities."
                
                wisdom = await llm.complete_async(prompt, system, max_tokens=150)
                
                fragments.append({
                    "hash": h[:8],
                    "date": date,
                    "summary": msg,
                    "symbols": modified_symbols,
                    "aligned_objectives": [obj['id'] for obj in correlated_objectives],
                    "wisdom": wisdom.strip()
                })
                logger.info(f"✨ [BOOSTED]: {h[:8]} - {msg[:30]} (Aligned: {len(correlated_objectives)})")
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

    async def prune_wisdom(self) -> int:
        """Entry point for manual or scheduled neural decay."""
        return await self.autonomous_janitor()

    def _extract_symbols(self, diff_content: str) -> List[str]:
        """
        Uses native Python AST to find which functions or classes were modified in a diff.
        Currently highly optimized for Python files.
        """
        import re
        symbols = set()
        
        # Heuristic: Find lines starting with + or - that look like def or class
        # (Slightly faster than parsing the whole file for every diff)
        lines = diff_content.splitlines()
        for line in lines:
            if line.startswith("+") and not line.startswith("+++"):
                match = re.search(r"(def|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)", line)
                if match:
                    symbols.add(match.group(2))
        
        return list(symbols)

    async def autonomous_janitor(self, throttle_hook=None) -> int:
        """
        The 'Neural Decay' Protocol. 
        Prunes obsolete, redundant, or conflicting strategic fragments.
        Uses SimHash bit-similarity to identify 'Dead Wisdom'.
        [INTEL-2]: Supports adaptive throttle hooks for thermal safety.
        """
        from side.storage.modules.base import SovereignEngine
        from side.storage.modules.strategic import StrategicStore
        from side.utils.hashing import sparse_hasher
        
        engine = SovereignEngine()
        strategic = StrategicStore(engine)
        
        pruned_count = 0
        
        # 1. PRUNE: Conflict Decay (Rejections vs Successful Ledger Actions)
        rejections = strategic.list_rejections(limit=100)
        
        for rej in rejections:
            if throttle_hook: await throttle_hook()
            
            rej_id = rej['id']
            rej_hash = rej.get('signal_hash')
            if not rej_hash: continue
            pass

        # 2. PRUNE: Redundancy (SimHash Deduplication)
        wisdom = strategic.list_public_wisdom()
        hashes = {} # hash -> id
        
        for w in wisdom:
            if throttle_hook: await throttle_hook()
            
            w_hash = w.get('signal_hash')
            if not w_hash: continue
            
            # Find near-duplicates
            duplicate_found = False
            for existing_hash, existing_id in hashes.items():
                if sparse_hasher.similarity(w_hash, existing_hash) > 0.70:
                    # [STRATEGIC AUDIT]: Never deduplicate (delete) a pinned wisdom
                    if w.get('is_pinned'):
                        continue
                    low_id = w['id']
                    with engine.connection() as conn:
                        conn.execute("DELETE FROM public_wisdom WHERE id = ?", (low_id,))
                    pruned_count += 1
                    duplicate_found = True
                    break
            
            if not duplicate_found:
                hashes[w_hash] = w['id']

        # 3. Timeline Decay: Prune rejections passed their half-life (Neural Decay KAR-1)
        purged_stale = self.strategic.purge_stale_rejections(days=180)
        pruned_count += purged_stale

        # 4. Limit Decay: Ensure 'rejections' doesn't exceed 200 entries (pinned excluded).
        with engine.connection() as conn:
            cursor = conn.execute("DELETE FROM rejections WHERE is_pinned = 0 AND id NOT IN (SELECT id FROM rejections ORDER BY created_at DESC LIMIT 200)")
            pruned_count += cursor.rowcount

        logger.info(f"🧹 [JANITOR]: Neural Decay complete. Purged {pruned_count} strategic fragments.")
        return pruned_count

    async def _harvest_documentation_dna(self):
        """
        [KAR-4] Universal Strategic Memory.
        Scans walkthroughs and notes to extract 'Documentation DNA'.
        """
        from side.utils.hashing import sparse_hasher
        import uuid
        
        # 1. SCAN LOCATIONS
        doc_paths = [
            self.project_path / "README.md",
            self.brain_path,
        ]
        
        for path in doc_paths:
            if not path.exists():
                continue
            
            files = [path] if path.is_file() else list(path.glob("*.md"))
            
            for f in files:
                try:
                    content = f.read_text()
                    # Segment by headers
                    sections = content.split("\n#")
                    for section in sections:
                        if len(section.strip()) < 50:
                            continue
                            
                        # Generate Signal Hash [SILO PROTOCOL]: Salted with Project ID
                        project_id = self.engine.get_project_id()
                        sig_hash = sparse_hasher.fingerprint(section, salt=project_id)
                        
                        # Store as Public Wisdom (Documentation-Sourced)
                        # We use a UUID based on the file and hash to avoid duplicates
                        fragment_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{f.name}:{sig_hash}"))
                        
                        if self.buffer:
                            await self.buffer.ingest("wisdom", {
                                "id": fragment_id,
                                "origin": "local",
                                "category": "documentation",
                                "pattern": f.name,
                                "signal_hash": sig_hash,
                                "text": section[:1000].strip(),
                                "source_type": "documentation",
                                "source_file": str(f),
                                "confidence": 8
                            })
                        else:
                            with self.engine.connection() as conn:
                                conn.execute("""
                                    INSERT OR REPLACE INTO public_wisdom (
                                        id, origin_node, category, signal_pattern, 
                                        signal_hash, wisdom_text, source_type, source_file, confidence
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    fragment_id, "local", "documentation", f.name,
                                    sig_hash, section[:1000].strip(), "documentation", str(f), 8
                                ))
                            
                except Exception as e:
                    logger.warning(f"Failed to harvest DNA from {f}: {e}")

    def gather_context(self, active_file: str = None, topic: str = None) -> str:
        """
        Builds the 100% Context Prompt.
        """
        context_parts = []
        
        # 0. SOVEREIGN ANCHOR (The Boot Disk)
        anchor_path = self.project_path / "SOVEREIGN_ANCHOR.md"
        if anchor_path.exists():
             context_parts.append(f"⚓ [SOVEREIGN ANCHOR]:\n{anchor_path.read_text()}")

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

    def _walk_fractal_tree(self, path: Path, prefix: str = "") -> str:
        """
        Recursively walks the distributed Fractal Index to build a Merkle Tree.
        """
        import json
        tree_out = ""
        index_path = path / ".side" / "local.json"
        
        if not index_path.exists():
            return tree_out
            
        try:
            raw = shield.unseal_file(index_path)
            data = json.loads(raw)
            files = sorted(data.get("context", {}).get("files", []), key=lambda x: x['name'])
            children = sorted(data.get("context", {}).get("children", {}).items())
            
            # 1. Render Files
            for i, f in enumerate(files):
                is_last_item = (i == len(files) - 1) and not children
                connector = "└── " if is_last_item else "├── "
                f_hash = f.get('hash', 'no_hash')[:8]
                tree_out += f"{prefix}{connector}{f['name']} [{f_hash}]\n"
                
            # 2. Render Children (Sub-directories)
            for i, (name, checksum) in enumerate(children):
                is_last_child = (i == len(children) - 1)
                connector = "└── " if is_last_child else "├── "
                tree_out += f"{prefix}{connector}{name}/ [Merkle: {checksum[:8]}]\n"
                
                # Recursive Step
                new_prefix = prefix + ("    " if is_last_child else "│   ")
                tree_out += self._walk_fractal_tree(path / name, new_prefix)
                
            return tree_out
        except Exception as e:
            return f"{prefix}└── [ERROR: {e}]\n"

    def _get_raw_schemas(self) -> str:
        """
        [CODE-FIRST TRUTH]: Generates JSON Schemas directly from Pydantic Models.
        """
        import json
        try:
            from side.models.intent import ConversationSession
            from side.models.physics import PulseResult
            from side.models.ledger import LedgerEntry
            from side.models.brain import SovereignGraph
            
            schemas = []
            
            models = [
                ("INTENT", ConversationSession),
                ("PHYSICS", PulseResult),
                ("LEDGER", LedgerEntry),
                ("BRAIN", SovereignGraph)
            ]
            
            for name, model in models:
                try:
                    # Generate Schema
                    schema_dict = model.model_json_schema()
                    schema_str = json.dumps(schema_dict, indent=2)
                    schemas.append(f"# --- {name} (Pydantic V2) ---\n{schema_str}")
                except Exception as e:
                    schemas.append(f"# [ERROR] Could not generate schema for {name}: {e}")
                    
            return "\n\n".join(schemas)
            
        except ImportError as e:
            return f"# [CRITICAL ERROR] Model Import Failed: {e}"

    def get_episodic_context(self, limit: int = 15) -> str:
        """
        [PHOENIX PROTOCOL]: Retrieves the 'RAM' (Recent Context) from the Ledger.
        Uses EpisodicProjector to build a coherent narrative of the last few events.
        """
        try:
            from side.intel.episodic_projector import EpisodicProjector
            projector = EpisodicProjector(self.forensic, self.strategic)
            return projector.get_episode_stream(limit=limit)
        except Exception as e:
            return f"## [RAM ERROR]: Failed to load episodic context: {e}"

    def get_surgical_context(self, query: str, limit: int = 3) -> str:
        """
        [PHOENIX PROTOCOL LAYER 3]: Surgical Attention.
        Scans the Live Filesystem (rglob) for files matching the user's query.
        Returns the content of the most relevant code files.
        """
        try:
            # 2. Dynamic Search (Live Codebase) - Replaces static Fractal Map lookup
            # Heuristic: Find files with exact or partial name match
            candidates = []
            q_lower = query.lower()
            
            # Use rglob for recursive search. 
            # Limit to likely code directories to avoid finding random stuff in node_modules or .git
            # We search from project root but filter later or just search specific subdirs
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
            
            # Sort by score descending
            candidates.sort(key=lambda x: x[0], reverse=True)
            # Deduplicate by path
            seen = set()
            unique_candidates = []
            for score, path in candidates:
                if path not in seen:
                    unique_candidates.append((score, path))
                    seen.add(path)
            
            top_files = unique_candidates[:limit]
            
            if not top_files:
                return f"- [LAYER 3]: No direct code matches found for '{query}' in the Live File System."
                
            # 3. Fetch Content
            output = [f"## 3. SURGICAL CONTEXT (Matched '{query}'):"]
            for _, rel_path in top_files:
                full_path = self.project_path / rel_path
                if full_path.exists():
                    # Cap context at 2000 chars per file to save tokens
                    content = full_path.read_text()[:2000]
                    output.append(f"\n### FILE: {rel_path}\n```\n{content}\n...\n```")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"- [LAYER 3 ERROR]: Surgical retrieval failed: {e}"

    def _get_operational_reality(self) -> str:
        """
        Derives the 'Truth' from the actual code metrics, not user plans.
        Source: Git Log (History) + Git Status (Now).
        """
        try:
            import subprocess
            
            # 1. Recent History (What we ACTUALLY did)
            cmd_log = ["git", "log", "-n", "5", "--pretty=format:%h %s (%cr)"]
            log_out = subprocess.check_output(cmd_log, cwd=self.project_path, text=True).strip()
            
            # 2. current Friction (What is bleeding right now)
            cmd_status = ["git", "status", "-s"]
            status_out = subprocess.check_output(cmd_status, cwd=self.project_path, text=True).strip()
            
            # Format nicely
            reality = "**Recent Commits (The Vector):**\n"
            for line in log_out.splitlines():
                reality += f"- {line}\n"
                
            reality += "\n**Active Measures (The Now):**\n"
            if status_out:
                for line in status_out.splitlines()[:10]: # Limit to 10
                    reality += f"- {line}\n"
            else:
                reality += "- Clean Working Tree (Steady State).\n"
                
            return reality
        except Exception as e:
            return f"- [ERROR] Could not derive Operational Reality: {e}"

    def generate_anchor(self) -> str:
        """
        [KAR-9] The Sovereign Anchor (Boot Disk).
        Generates a Zero-Fake, Cryptographic Blueprint.
        """
        import json
        
        project_id = self.engine.get_project_id()
        # REPLACED: strategy_content = self._get_active_strategy()
        operational_truth = self._get_operational_reality()
        
        merkle_tree = f". [{project_id}]\n"
        merkle_tree += self._walk_fractal_tree(self.project_path)
        
        schemas = self._get_raw_schemas()
        
        anchor_content = f"""# SOVEREIGN ANCHOR: {project_id}
> **Generated:** {datetime.now(timezone.utc).isoformat()}
> **Purpose:** LLM Boot Disk (Forensic Reality)
> **Verification:** SHA-256 Merkle Proof & Live Schema

## 1. OPERATIONAL REALITY (The Truth)
*Source: Git Forensic Log (Objective)*
{operational_truth}

## 2. DATA SOVEREIGNTY (The Law)
*Source: Live Codebase (Verified)*
```python
{schemas}
```

## 3. FRACTAL REALITY (The Map)
*Merkle Tree Snapshot*
```text
{merkle_tree}
```

## 4. SYSTEM PROMPTS (The Instruction)
- **Role:** You represent the Sovereign Will of the repository.
- **Priority:** Trust the Code (Objective) over the Plan (Subjective).
- **Style:** Zero-Latency, High-Precision, No Fluff.

---
*Use this anchor to re-align your weights with the Sovereign Reality.*
"""
        anchor_path = self.project_path / "SOVEREIGN_ANCHOR.md"
        anchor_path.write_text(anchor_content)
        logger.info(f"⚓ [ANCHOR]: Forensic Sovereign Anchor dropped at {anchor_path}")
        return str(anchor_path)

    async def recovery_pass(self) -> None:
        """
        The Phoenix Protocol: Rebuilds the Sovereign Context from the Ledger.
        Triggered when .side is wiped or context is corrupted.
        """
        logger.info("🔥 [PHOENIX]: Regenerating project soul from the Ledger...")
        
        # 1. Restore Project Identity
        from side.storage.modules.base import SovereignEngine
        project_id = SovereignEngine.get_project_id(self.project_path)
        logger.info(f"📍 [IDENTITY]: Project Recognized: {project_id}")

        # 2. Re-mine Historical Wisdom (The Memories)
        # We run a deep historic feed to restore strategic fragments
        logger.info("🕰️ [PHOENIX]: Re-mining Strategic Wisdom (12-month lookback)...")
        await self.historic_feed(months=12)
        
        # 3. Re-run Fractal Scan (The Body)
        # We build a fresh distributed index of the current filesystem
        logger.info("🧠 [PHOENIX]: Re-building Fractal Context Graph...")
        await self.feed()
        
        logger.info("✨ [PHOENIX]: Recovery Complete. Sovereign Context is Immortal.")

    def enrich_system_prompt(self, base_prompt: str, context: str) -> str:
        """
        Dynamically rewrites the System Prompt with Context.
        """
        return f"""{base_prompt}

=== SOVEREIGN CONTEXT INJECTION ===
{context}
===================================
"""
