from __future__ import annotations
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
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from side.storage.modules.base import ContextEngine

logger = logging.getLogger(__name__)

class AutoIntelligence:
    """
    The 'Context Server'.
    Automatically monitors the user's focus and injects:
    1. Project Memories (JSON).
    2. Local Git History.
    3. Activity log (Audit Trail).
    """

    def __init__(self, project_path: Path, engine: ContextEngine, buffer=None):
        import os
        from side.storage.modules.mmap_store import MmapStore
        self.project_path = project_path
        self.engine = engine
        self.strategic = engine.strategic
        self.forensic = engine.forensic
        self.buffer = buffer
        self.mmap = MmapStore(project_path)
        self.memory = MemoryManager(self.strategic, project_id=self.engine.get_project_id())
        
        # [KAR-4]: Universal Brain Path Discovery
        # Primary: Standard Antigravity Path (~/.gemini/antigravity/brain)
        # Fallback: Environment Variable (for dev/CI)
        env_brain = os.getenv("SIDE_BRAIN_PATH")
        antigravity_brain = Path.home() / ".gemini" / "antigravity" / "brain"
        
        self.brain_path = Path(env_brain) if env_brain else antigravity_brain

    async def setup(self):
        """
        Initializes the intelligence context.
        Generates distributed .side/local.json context and rolls up to consolidated metadata.
        """
        from side.intel.fractal_indexer import run_fractal_scan
        from side.storage.modules.identity import IdentityStore
        
        # [ECONOMY]: Charge for Context Boost (15 SUs)
        project_id = self.engine.get_project_id()
        identity = IdentityStore(self.engine)
        
        if not identity.charge_action(project_id, "CONTEXT_BOOST"):
             logger.warning(f"⚠️ [ECONOMY]: Insufficient SUs for Context Boost (Index).")
             # We allow it to run in "Degraded" but should we?
             # For Alpha, let's allow it but warn.
        
        # 1. Run the Fractal Scan (Distributed Indexing)
        start_time = time.time()
        logger.info("🧠 [BRAIN]: Initiating Parallel Fractal Context Scan...")
        run_fractal_scan(self.project_path)
        scan_duration = time.time() - start_time
        logger.info(f"🧠 [BRAIN]: Scan completed in {scan_duration:.2f}s.")
        
        # 2. Re-gen the Checkpoint (The Weights)
        config = await self.sync_checkpoint()
        
        # 5. Extract documentation patterns
        # await self._extract_documentation_patterns()
        await self._sync_mmap_patterns()
        
        return config

    async def sync_checkpoint(self):
        """
        [SERIALIZATION PROTOCOL]: Serializes the current 'Weights' to local telemetry.
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
        
        # [SOVEREIGN GAVEL]: Enforce Pydantic V2 Strictness
        from side.models.brain import SovereignGraph, BrainStats, DNA, IntentSnapshot
        
        # Construct Policy Object
        graph_obj = ContextEngine(
            dna=DNA(
                version="3.0",
                last_updated=datetime.now(timezone.utc).isoformat(),
                project_id=self.engine.get_project_id()
            ),
            stats=BrainStats(
                total_files=len(list(self.project_path.rglob("*"))),
                context_density=0.9
            ),
            intent_history=[]
        )
        
        # 3. Persist Master Checkpoint (The Weights)
        metadata_file = self.project_path / ".side" / "project_metadata.json"
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        shield.seal_file(metadata_file, graph_obj.model_dump_json(indent=2))
        logger.debug("💾 [CHECKPOINT]: Project metadata serialized (STRICT).")
        return graph_obj

    async def _sync_mmap_patterns(self):
        """Syncs public patterns to Mmap Store for low-latency acceleration."""
        try:
            patterns = self.strategic.list_public_patterns()
            fragments = []
            for p in patterns:
                sig_hash = p.get('signal_hash')
                p_id = p.get('id')
                if sig_hash is not None and p_id:
                    import uuid
                    try:
                        uuid_obj = uuid.UUID(p_id)
                        fragments.append((sig_hash, uuid_obj.bytes))
                    except:
                        continue
            
            if fragments:
                 self.mmap.sync_from_ledger(fragments)
            
            metadata_file = self.project_path / ".side" / "project_metadata.json"
            if metadata_file.exists():
                raw = shield.unseal_file(metadata_file)
                data = json.loads(raw)
                # Logic to append fragments to data...
                shield.seal_file(metadata_file, json.dumps(data, indent=2))
                logger.info("✨ [CONTEXT]: Technical timeline synced.")
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
            
        # 2. Pattern Harvest
        # [PURGE]: Unstructured .md files are no longer harvested.
        # if file_path.suffix == ".md":
        #      await self._harvest_single_doc(file_path)

    async def _extract_documentation_patterns(self, file_path: Path):
        """Extracts technical patterns from a single markdown file."""
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
                        INSERT OR REPLACE INTO public_patterns (
                            id, origin_node, category, signal_pattern, 
                            signal_hash, pattern_text, source_type, source_file, confidence
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (fragment_id, "local", "documentation", file_path.name,
                          sig_hash, section[:1000].strip(), "documentation", str(file_path), 9))
            logger.info(f"📁 [PATTERNS]: Extracted fragments from {file_path.name}")
        except Exception as e:
            logger.warning(f"Failed to harvest {file_path.name}: {e}")

    async def historic_feed(self, months: int = 3) -> List[Dict[str, Any]]:
        """
        Phased Git Analysis: Extracts 'Architectural Patterns' from commits.
        """
        import subprocess
        from side.llm.client import LLMClient
        
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

    async def prune_patterns(self) -> int:
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
        from side.storage.modules.base import ContextEngine
        from side.storage.modules.strategic import StrategicStore
        from side.utils.hashing import sparse_hasher
        
        engine = ContextEngine()
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
        patterns = strategic.list_public_patterns()
        hashes = {} # hash -> id
        
        for w in patterns:
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
                        conn.execute("DELETE FROM public_patterns WHERE id = ?", (low_id,))
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
                        
                        # Store as Ppublic_patterns (Documentation-Sourced)
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
                                    INSERT OR REPLACE INTO public_patterns (
                                        id, origin_node, category, signal_pattern, 
                                        signal_hash, wisdom_text, source_type, source_file, confidence
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    fragment_id, "local", "documentation", f.name,
                                    sig_hash, section[:1000].strip(), "documentation", str(f), 8
                                ))
                            
                except Exception as e:
                    logger.warning(f"Failed to harvest DNA from {f}: {e}")

    def gather_context(self, active_file: str = None, topic: str = None, include_code: bool = True) -> str:
        """
        Builds the 100% Context Prompt.
        """
        context_parts = []
        
        # 0. ANCHOR LOGIC
        anchor_path = self.project_path / "SOVEREIGN_ANCHOR.md"
        if anchor_path.exists():
             context_parts.append(f"⚓ [SOVEREIGN ANCHOR]:\n{anchor_path.read_text()}")

        # 1. STRATEGIC ARTIFACTS
        artifacts = ["VISION.md", "STRATEGY.md", "ARCHITECTURE.md"]
        for art in artifacts:
             p = self.project_path / art
             if p.exists():
                 context_parts.append(f"📜 [{art}]:\n{p.read_text()[:4000]}...")
        
        # 2. HYBRID SEARCH (Wisdom & Patterns)
        search_q = f"{topic} {active_file}" if topic else str(active_file)
        if search_q and len(search_q) > 3:
            # A. Architectural Wisdom
            wisdom_hits = self.strategic.search_wisdom(search_q, limit=3)
            if wisdom_hits:
                w_text = "\n".join([f"- {w['wisdom_text']} (Confidence: {w['confidence']})" for w in wisdom_hits])
                context_parts.append(f"🧠 [WISDOM]:\n{w_text}")
            
            # B. Verified Patterns
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

        # 4. ACTIVE FOCUS (The Code)
        if active_file:
             context_parts.append(f"📍 [ACTIVE FOCUS]: User is working on '{active_file}'.")
             if include_code:
                 try:
                     full_path = self.project_path / active_file
                     if full_path.exists() and full_path.is_file():
                         # Include first 3000 chars for context
                         content = full_path.read_text()[:3000]
                         context_parts.append(f"💻 [SOURCE CODE]:\n```\n{content}\n```")
                 except Exception as e:
                     logger.debug(f"Failed to inject active file code: {e}")

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

    async def optimize_weights(self) -> dict:
        """
        [LAYER 4]: Optimizes Sovereign Weights (sovereign.json).
        Triggers Strategic Observer to distill facts.
        """
        import json
        from side.intel.observer import StrategicObserver
        
        project_id = self.engine.get_project_id()
        
        # 1. Update sovereign.json (The Weights)
        # We ensure the file exists and has the latest schema pointers
        sovereign_path = self.project_path / ".side" / "sovereign.json"
        
        if not sovereign_path.exists():
            weights = {
                "version": "4.0.0 (Observer Edition)",
                "project_id": project_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "intent": {},
                "metrics": {}
            }
        else:
            weights = json.loads(shield.unseal_file(sovereign_path))
            
        weights["last_scan"] = datetime.now(timezone.utc).isoformat()
        
        # 2. Trigger Strategic Observer (The Compiler)
        observer = StrategicObserver(self.forensic)
        new_facts = await observer.distill_observations(project_id, limit=20)
        
        if "metrics" not in weights:
            weights["metrics"] = {}
        weights["metrics"]["recent_facts"] = new_facts
        
        # Save Weights
        # We use a shielded write to prevent corruption
        shield.seal_file(sovereign_path, json.dumps(weights, indent=2))
        logger.info(f"⚓ [WEIGHTS]: Optimized sovereign.json (Facts: +{new_facts})")
        
        return weights

        
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

=== STRATEGIC CONTEXT ===
{context}
==========================
"""
