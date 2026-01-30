import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import ast
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
        
        # [KAR-4]: Universal Brain Path (Default to .side/brain or ENV)
        env_brain = os.getenv("SIDE_BRAIN_PATH")
        self.brain_path = Path(env_brain) if env_brain else project_path / ".side" / "brain"

    async def feed(self) -> Dict[str, Any]:
        """
        Actively scans the repository using the Fractal Engine (Protocol v3).
        Generates distributed .side/local.json context and rolls up to sovereign.json.
        """
        import json
        from datetime import datetime, timezone
        from side.intel.fractal_indexer import run_fractal_scan
        
        # 1. Run the Fractal Scan (Distributed Indexing)
        start_time = time.time()
        logger.info("🧠 [BRAIN]: Initiating Parallel Fractal Context Scan...")
        run_fractal_scan(self.project_path)
        scan_duration = time.time() - start_time
        logger.info(f"🧠 [BRAIN]: Scan completed in {scan_duration:.2f}s.")
        
        # 2. Rollup to Monolith (For v1/v2 Compatibility)
        # We read the root local.json (ENCRYPTED) and wrap it as the Master Brain
        root_index_path = self.project_path / ".side" / "local.json"
        if not root_index_path.exists():
            return {"error": "Fractal Scan Failed"}
            
        raw_data = shield.unseal_file(root_index_path)
        local_data = json.loads(raw_data)
        
        # 3. Construct the Sovereign Graph (Unified Intent Layer)
        project_id = self.engine.get_project_id()
        
        # Ingest Strategic Intent (Plans & Directives)
        plans = self.strategic.list_plans(project_id)
        objectives = [p for p in plans if p['type'] == 'objective' and p['status'] != 'done']
        tasks = [p for p in plans if p['type'] == 'task' and p['status'] != 'done']
        
        # Ingest Recent Intel (Silicon Pulse & Activity)
        activities = self.forensic.get_recent_activities(project_id, limit=10)
        
        sovereign_graph = {
            "$schema": "./backend/src/side/schema/sovereign.schema.json",
            "version": "3.1.0 (Unified HUD Edition)",
            "last_scan": datetime.now(timezone.utc).isoformat(),
            "dna": {
                "detected_stack": ["M2 Pro Accelerated"], # Todo: Extract from tree/hardware.py
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
            "history_fragments": []
        }
        
        # 4. Persist Master Index (ENCRYPTED)
        sovereign_file = self.project_path / ".side" / "sovereign.json"
        sovereign_file.parent.mkdir(parents=True, exist_ok=True)
        shield.seal_file(sovereign_file, json.dumps(sovereign_graph, indent=2))
        
        # 5. Harvest Documentation DNA [KAR-4]
        await self._harvest_documentation_dna()
        
        # 6. [INTEL-4] Sync Mmap Store for NEON Acceleration
        try:
            wisdom = self.strategic.list_public_wisdom()
            fragments = []
            for w in wisdom:
                sig_hash = w.get('signal_hash')
                w_id = w.get('id')
                if sig_hash is not None and w_id:
                    # Convert UUID string to 16-byte buffer
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
