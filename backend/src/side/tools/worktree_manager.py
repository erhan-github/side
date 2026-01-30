import os
import subprocess
import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)

class WorktreeManager:
    """
    [KAR-22.3] Background Worktree Primitives.
    Allows Sidelith to run 'Ghost Refactors' in isolated git worktrees.
    """

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self._worktrees: List[Path] = []

    def create_ghost_worktree(self, branch_name: str, base_branch: str = "main") -> Optional[Path]:
        """
        Creates a temporary worktree for a ghost refactor.
        """
        worktree_path = self.project_path.parent / f".side_ghost_{branch_name}"
        
        try:
            # 1. Ensure the branch exists or create it
            subprocess.run(
                ["git", "branch", branch_name, base_branch],
                cwd=self.project_path,
                check=False,
                capture_output=True
            )
            
            # 2. Add worktree
            logger.info(f"👻 [WORKTREE]: Creating ghost worktree at {worktree_path}...")
            result = subprocess.run(
                ["git", "worktree", "add", str(worktree_path), branch_name],
                cwd=self.project_path,
                check=True,
                capture_output=True,
                text=True
            )
            
            self._worktrees.append(worktree_path)
            return worktree_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ [WORKTREE]: Failed to create ghost worktree: {e.stderr}")
            return None

    def cleanup_ghost_worktree(self, worktree_path: Path):
        """
        Removes a ghost worktree.
        """
        try:
            logger.info(f"🧹 [WORKTREE]: Cleaning up ghost worktree at {worktree_path}...")
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree_path)],
                cwd=self.project_path,
                check=True,
                capture_output=True
            )
            if worktree_path in self._worktrees:
                self._worktrees.remove(worktree_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ [WORKTREE]: Cleanup failed: {e.stderr}")

    def list_ghosts(self) -> List[Path]:
        return self._worktrees
