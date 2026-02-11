"""
Context tracker service for monitoring user's work patterns.

Analyzes file changes and git activity to understand what user is working on.
"""

import asyncio
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from collections import deque
from side.storage.modules.transient import SessionCache
from side.utils.llm_helpers import extract_json
from side.prompts import Personas, ArchitecturalPivotPrompt, FocusDetectionPrompt, LLMConfigs

logger = logging.getLogger(__name__)


class ContextTracker:
    """
    Tracks user's work context to provide relevant recommendations.

    Analyzes:
    - Recently edited files
    - Git commits
    - Current branch
    - Focus areas (auth, API, frontend, etc.)
    - Cognitive Flow (V_cognitive)
    """

    def __init__(self, operational: Any, strategic: Any = None, identity: Any = None):
        """
        Initialize context tracker.

        Args:
            operational: Operational store instance
            strategic: Strategic store instance
            identity: Identity store instance
        """
        self.operational = operational
        self.strategic = strategic
        self.identity = identity
        
        # Cognitive State (Flow State Tracking)
        self._last_active_time = datetime.now(timezone.utc)
        self._window_seconds = 1800 # 30 Minute Sliding Window
        # Samples: deque of (timestamp, duration, is_ide)
        self._samples: deque[tuple[float, float, bool]] = deque()

        # Focus area patterns
        self._focus_patterns = {
            "authentication": ["auth", "login", "signup", "session", "token", "jwt"],
            "api": ["api", "endpoint", "route", "controller", "handler"],
            "frontend": ["component", "ui", "view", "page", "template"],
            "database": ["model", "schema", "migration", "query", "db"],
            "testing": ["test", "spec", "mock", "fixture"],
            "infrastructure": ["docker", "k8s", "deploy", "ci", "cd", "config"],
            "security": ["security", "crypto", "hash", "encrypt", "sanitize"],
            "performance": ["cache", "optimize", "perf", "benchmark"],
        }

    async def update_context(self, project_path: str | Path, changed_files: set[Path]) -> None:
        """
        Update work context based on file changes.

        Args:
            project_path: Path to project
            changed_files: Set of changed file paths
        """
        project_path = Path(project_path).resolve()

        try:
            # Get recent files (relative paths)
            recent_files = [
                str(f.relative_to(project_path))
                for f in list(changed_files)[:10]
                if f.is_relative_to(project_path)
            ]

            # Get recent commits
            recent_commits = await self._get_recent_commits(project_path, limit=5)

            # Get current branch
            current_branch = self._get_current_branch(project_path)

            # Detect focus area
            focus_area, confidence = self._detect_focus_area(recent_files, recent_commits)

            # Save to database
            self.operational.save_work_context(
                project_path=str(project_path),
                focus_area=focus_area,
                recent_files=recent_files,
                recent_commits=recent_commits,
                current_branch=current_branch,
                confidence=confidence,
            )

            # Update Cognitive Flow (Hyper-Perception)
            await self._update_cognitive_flow()

            logger.info(
                f"Updated context: {focus_area} (confidence: {confidence:.2f}) | Flow: {self.operational.get_setting('cognitive_flow_score')}"
            )

        except Exception as e:
            logger.error(f"Error updating context: {e}", exc_info=True)

    async def _get_recent_commits(self, project_path: Path, limit: int = 5) -> list[dict[str, Any]]:
        """Get recent git commits with Complexity Delta (T-003)."""
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    f"-{limit}",
                    "--pretty=format:%H|%an|%s|%ct",
                ],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return []

            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("|")
                if len(parts) == 4:
                    h = parts[0][:8]
                    commits.append({
                        "hash": h,
                        "author": parts[1],
                        "message": parts[2],
                        "timestamp": int(parts[3]),
                        "entropy": self._get_git_entropy(project_path, h),
                        "signature": await self._get_semantic_signature(project_path, h, parts[2]) # T-007
                    })

            return commits

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    async def _deduct_su(self, action_key: str, project_id: str = "default"):
        """Deducts SUs for high-value cognitive acts."""
        if not self.identity:
            return
        try:
            cost = self.identity.get_su_cost(action_key)
            self.identity.update_token_balance(project_id, -cost)
            logger.info(f"💰 [ECONOMY]: Deducted {cost} SU for {action_key}")
        except Exception as e:
            logger.warning(f"Economy Error: {e}")

    async def _get_semantic_signature(self, project_path: Path, commit_hash: str, commit_msg: str = "") -> str:
        """
        [SEMANTIC ANALYSIS]: Tiered Inference Protocol (T-007).
        """
        try:
            # ... (Tier 0 filtering logic remains)
            # TIER 0: Raw Heuristics (Zero Cost)
            result = subprocess.run(
                ["git", "show", "--name-only", "--format=", commit_hash],
                cwd=project_path, capture_output=True, text=True, timeout=2
            )
            files = result.stdout.strip().split("\n")
            
            # Filter: Always ignore noise
            if all(f.endswith((".lock", ".json", ".md", ".txt")) for f in files):
                return "Routine Dependency/Doc Maintenance"

            # Extract Modified Symbols
            diff_result = subprocess.run(
                ["git", "show", "--format=", commit_hash],
                cwd=project_path, capture_output=True, text=True, timeout=3
            )
            raw_diff = diff_result.stdout
            
            # Tier 0 Language-Aware Regex (Python, JS, TS)
            patterns = [
                r"^[+-]\s*(?:def|class|async def)\s+([a-zA-Z_][a-zA-Z0-9_]*)", # Python
                r"^[+-]\s*(?:export\s+)?(?:internal\s+)?(?:class|function|interface|type|const|let)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[=:(]", # JS/TS
            ]
            symbols = []
            import re
            for pattern in patterns:
                symbols.extend(re.findall(pattern, raw_diff, re.MULTILINE))
            
            symbols = sorted(list(set(symbols)))
            symbol_str = f" [Modified: {', '.join(symbols)}]" if symbols else ""

            # TIER 2: Strategic Distillation
            # [VIBE-CODER-FIX]: Handle large diffs by chunking
            full_diff_len = len(raw_diff)
            window_size = 2000
            
            # If diff is huge, we only distilled the most 'Strategic' chunks
            chunks = [raw_diff[i:i + window_size] for i in range(0, min(full_diff_len, 6000), window_size)]
            
            from side.llm.client import LLMClient
            client = LLMClient()
            
            # Analyze the most relevant chunk
            best_chunk = chunks[0]
            for chunk in chunks:
                if any(s in chunk for s in symbols):
                    best_chunk = chunk
                    break

            # [INTENT-CORRELATION] Fetch active goals
            goals = []
            if self.strategic:
                plans = self.strategic.list_plans(status="active")
                goals = [p["title"] for p in plans[:3]]
            
            goal_str = f"ACTIVE GOALS: {', '.join(goals)}" if goals else ""

            goal_str = f"ACTIVE GOALS: {', '.join(goals)}" if goals else ""

            prompt = ArchitecturalPivotPrompt.format(
                goal_str=goal_str,
                commit_msg=commit_msg,
                symbols=symbols,
                best_chunk=best_chunk
            )
            config = LLMConfigs.get_config("architectural_pivot")
            
            signature = await client.complete_async(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=Personas.ARCHITECTURE_ANALYST,
                **config
            )
            
            # [BOOST-ECONOMY] Deduct SUs
            await self._deduct_su("SEMANTIC_BOOST")
            if goals and "DRIFT" in signature.upper():
                await self._deduct_su("STRATEGIC_PIVOT")
                
            return f"{signature.strip()}{symbol_str}"
            
            return f"Routine Logic Mutation{symbol_str}"
        except Exception as e:
            return "Indeterminable State Mutation"

    def _get_git_entropy(self, project_path: Path, commit_hash: str) -> dict[str, Any]:
        """Analyses the 'Diff Pulse' of a commit to derive grounding DNA."""
        try:
            result = subprocess.run(
                ["git", "show", "--numstat", "--format=", commit_hash],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=2,
            )
            stats = {"added": 0, "deleted": 0, "files": 0}
            for line in result.stdout.strip().split("\n"):
                parts = line.split("\t")
                if len(parts) >= 3:
                    stats["added"] += int(parts[0]) if parts[0].isdigit() else 0
                    stats["deleted"] += int(parts[1]) if parts[1].isdigit() else 0
                    stats["files"] += 1
            return stats
        except:
            return {}

    def _get_current_branch(self, project_path: Path) -> str | None:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=2,
            )

            if result.returncode == 0:
                return result.stdout.strip() or None

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return None

    async def _detect_focus_area(
        self,
        recent_files: list[str],
        recent_commits: list[dict[str, Any]],
    ) -> tuple[str, float]:
        """
        [AI] Detect current focus area from files and commits using LLM.
        """
        # Combine files and commit messages for context
        files_str = "\n".join(recent_files[:10])
        commits_str = "\n".join([f"- {c['message']}" for c in recent_commits[:5]])
        
        commits_str = "\n".join([f"- {c['message']}" for c in recent_commits[:5]])
        
        prompt = FocusDetectionPrompt.format(
            files_str=files_str,
            commits_str=commits_str
        )
        config = LLMConfigs.get_config("focus_detection")
        try:
            from side.llm.client import LLMClient
            client = LLMClient()
            response = await client.complete_async(
                messages=[{"role": "user", "content": prompt}],
                system_prompt=Personas.CLASSIFIER,
                **config
            )
            
            data = extract_json(response)
            if data:
                return data.get("focus", "General Development"), float(data.get("confidence", 0.5))
                
        except Exception as e:
            logger.warning(f"LLM Focus detection failed: {e}")
            
        # Fallback to simple heuristic if LLM fails (Software 1.0 backup)
        text = (files_str + commits_str).lower()
        if "auth" in text or "login" in text: return "Authentication", 0.4
        if "test" in text: return "Testing", 0.4
        
        return "General Development", 0.3

    async def _update_cognitive_flow(self) -> None:
        """
        [FLOW STATE]: Detects if user is in 'Flow' or 'Search' mode.
        Uses Mac-native osascript to check active window.
        """
        import sys
        if sys.platform != "darwin":
            return

        try:
            # Check active application
            cmd = "osascript -e 'tell application \"System Events\" to get name of first process whose frontmost is true'"
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            active_app = stdout.decode().strip()

            now = datetime.now(timezone.utc)
            delta = (now - self._last_active_time).total_seconds()
            self._last_active_time = now

            ide_apps = ["Cursor", "Visual Studio Code", "Terminal", "iTerm2", "warp"]
            ide_apps = ["Cursor", "Visual Studio Code", "Terminal", "iTerm2", "warp"]
            browser_apps = ["Safari", "Google Chrome", "Arc", "Firefox"]

            is_ide = active_app in ide_apps
            is_browser = active_app in browser_apps

            if is_ide or is_browser:
                # Add sample to sliding window
                import time
                self._samples.append((time.time(), delta, is_ide))

            # 1. SLIDING WINDOW PRUNING: Keep only last 30 mins
            import time
            horizon = time.time() - self._window_seconds
            while self._samples and self._samples[0][0] < horizon:
                self._samples.popleft()

            # 2. CALCULATE V_COGNITIVE (The Focus Ratio)
            t_ide = sum(s[1] for s in self._samples if s[2])
            t_browser = sum(s[1] for s in self._samples if not s[2])
            
            total_window_time = t_ide + t_browser
            v_cognitive = t_ide / total_window_time if total_window_time > 0 else 1.0
            
            # Normalize and Save
            self.operational.set_setting("cognitive_flow_score", str(round(v_cognitive, 3)))
            self.operational.set_setting("active_app", active_app)
            
            # 3. HEARTBEAT: Record activity for Midnight Learning
            if delta < 5.0 and (is_ide or is_browser):
                self.operational.set_setting("last_user_activity", str(time.time()))
                
        except Exception as e:
            logger.debug(f"Cognitive Flow detection failed: {e}")

    async def watch_forever(self, project_path: str | Path) -> None:
        """
        [CONTEXT SCAN]: Continuous monitoring loop.
        """
        logger.info("🧠 [CONTEXT]: Starting continuous perception loop...")
        while True:
            try:
                await self._update_cognitive_flow()
                # We could add more perceptual checks here (e.g. mic volume, camera vision)
                # but for V3 we stick to process and window context.
                await asyncio.sleep(2) # Poll every 2s
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Perception loop error: {e}")
                await asyncio.sleep(10)

    def get_current_context(self, project_path: str | Path) -> dict[str, Any] | None:
        """
        Get current work context for project.

        Args:
            project_path: Path to project

        Returns:
            Context dict or None if not found
        """
        return self.operational.get_latest_work_context(str(Path(project_path).resolve()))
