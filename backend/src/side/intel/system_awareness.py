import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from side.storage.modules.base import ContextEngine

logger = logging.getLogger(__name__)

class SystemAwareness:
    """
    The System Awareness Engine.
    Synchronizes the 'Artifact Goals' with the 'AI Mindset'.
    """

    def __init__(self, engine: ContextEngine, brain_dir: Path):
        self.engine = engine
        self.brain_dir = brain_dir
        self.is_active = True
        self._sync_task = None
        self._last_state: Dict[str, Any] = {}

    def start(self):
        """Starts the awareness sync process."""
        if not self._sync_task:
            try:
                loop = asyncio.get_running_loop()
                self._sync_task = loop.create_task(self._process_awareness())
                logger.info("📡 [SYSTEM_AWARENESS]: Awareness Engine active.")
            except RuntimeError:
                logger.debug("📡 [SYSTEM_AWARENESS]: No running loop, delay awareness start.")
                pass

    async def _process_awareness(self):
        """Periodically scans artifacts and git for goal shifts."""
        while self.is_active:
            try:
                await self.sync_artifacts()
                await self.sync_git_state()
            except Exception as e:
                logger.error(f"❌ [SYSTEM_AWARENESS]: Sync failed: {e}")
            await asyncio.sleep(60)  # Check every minute

    async def sync_artifacts(self):
        """
        [UNIVERSAL INGESTION]: Ingests ALL strategic artifacts in the brain directory.
        """
        if not self.brain_dir.exists():
            return

        artifacts = list(self.brain_dir.glob("*.md"))
        new_state = {}
        
        for art_path in artifacts:
            # Skip metadata and resolved snapshots to keep content high-fidelity
            if art_path.name.endswith((".metadata.json", ".resolved")) or ".resolved." in art_path.name:
                continue
            
            try:
                stat = art_path.stat()
                mtime = stat.st_mtime
                new_state[art_path.name] = mtime
                
                # Only re-ingest if file changed
                if self._last_state.get(art_path.name) != mtime:
                    content = art_path.read_text()
                    logger.info(f"📄 [SYSTEM_AWARENESS]: Ingesting artifact: {art_path.name}")
                    
                    # 1. Specialized Goal Parsing for task.md
                    if art_path.name == "task.md":
                        await self._parse_task_goals(content)
                    
                    # 2. General Storage for all artifacts
                    self.engine.schema.save_concept(
                        topic=f"artifact_{art_path.stem}",
                        content=content,
                        category="strategic_artifact"
                    )
            except Exception as e:
                logger.warning(f"⚠️ [SYSTEM_AWARENESS]: Failed to ingest {art_path.name}: {e}")
        
        # Update tracking state
        self._last_state.update(new_state)

    async def _parse_task_goals(self, content: str):
        """Extracts objectives from task.md."""
        current_phase = ""
        in_progress_tasks = []

        for line in content.splitlines():
            if line.startswith("## Phase"):
                current_phase = line.strip("# ")
            if "[/]" in line:
                in_progress_tasks.append(line.split("]")[1].strip())

        logger.info(f"🎯 [SYSTEM_AWARENESS]: Goal Sync: {current_phase} -> {in_progress_tasks}")
        self.engine.schema.save_concept(
            topic="current_objective",
            content=f"Focusing on {current_phase}. Active tasks: {', '.join(in_progress_tasks)}",
            category="project_state"
        )

    async def sync_git_state(self):
        """
        [ATOMIC BLUEPRINT]: Captures a "packed" state of the Git environment.
        """
        import subprocess
        import json
        from datetime import datetime
        try:
            # 1. Latest Commit Info
            commit_res = subprocess.run(
                ["git", "log", "-1", "--pretty=%H|%an|%s"],
                capture_output=True, text=True, cwd=str(Path.cwd())
            )
            commit_data = commit_res.stdout.strip().split("|") if commit_res.returncode == 0 else ["", "", ""]
            
            # 2. Working Tree Status
            status_res = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=str(Path.cwd())
            )
            status_lines = status_res.stdout.strip().splitlines() if status_res.returncode == 0 else []
            staged = len([l for l in status_lines if l.startswith(('A', 'M', 'D', 'R', 'C'))])
            unstaged = len([l for l in status_lines if l.startswith(' ') or l.startswith('?')])

            # 3. Branch Name
            branch_res = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, cwd=str(Path.cwd())
            )
            branch = branch_res.stdout.strip() if branch_res.returncode == 0 else "unknown"

            # [SMART PACKING]: Distill into a machine-readable blueprint
            blueprint = {
                "branch": branch,
                "head": commit_data[0][:8],
                "author": commit_data[1],
                "message": commit_data[2],
                "staged_changes": staged,
                "unstaged_changes": unstaged,
                "is_dirty": (staged + unstaged) > 0,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"🌿 [SYSTEM_AWARENESS]: Git state synchronized (Branch: {branch}, Head: {blueprint['head']})")
            
            self.engine.schema.save_concept(
                topic="git_state",
                content=json.dumps(blueprint),
                category="git_state"
            )
            
            # Also legacy support for intent verifier
            self.engine.ontology.save_concept(
                topic="git_intent",
                content=f"Branch: {branch}\nCommit: {commit_data[2]}",
                category="git_state"
            )

        except Exception as e:
            logger.debug(f"Git Blueprinting skipped: {e}")

    def get_health_pulse(self) -> Dict[str, Any]:
        """Provides data for the Production Health Dashboard."""
        return {
            "status": "AWARE",
            "last_sync": self._last_state.get("phase", "GENESIS"),
            "focus_count": len(self._last_state.get("focus", [])),
            "engine_state": "NOMINAL"
        }

    def stop(self):
        """Stops the awareness process."""
        self.is_active = False
        if self._sync_task:
            self._sync_task.cancel()
