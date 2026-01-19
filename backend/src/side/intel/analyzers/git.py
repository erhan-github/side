import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timezone
from .base import BaseAnalyzer, Finding

@dataclass
class GitSignals:
    """Git repository signals."""
    is_git_repo: bool = False
    total_commits: int = 0
    recent_commits: int = 0  
    contributors: list[str] = field(default_factory=list)
    active_branches: list[str] = field(default_factory=list)
    last_commit_date: str | None = None
    commit_frequency: str | None = None  
    recent_commit_messages: list[str] = field(default_factory=list)
    recent_changed_files: list[str] = field(default_factory=list)
    current_focus_areas: list[str] = field(default_factory=list)
    is_summarized: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_git_repo": self.is_git_repo,
            "total_commits": self.total_commits,
            "recent_commits": self.recent_commits,
            "contributors": self.contributors[:5],
            "active_branches": self.active_branches[:3],
            "last_commit_date": self.last_commit_date,
            "commit_frequency": self.commit_frequency,
            "recent_commit_messages": self.recent_commit_messages[:5],
            "recent_changed_files": self.recent_changed_files[:5],
            "current_focus_areas": self.current_focus_areas,
            "is_summarized": self.is_summarized
        }

class GitAnalyzer(BaseAnalyzer):
    """Analyzes git repository signals and documentation drift."""
    
    async def analyze(self, root: Path, files: list[Path]) -> dict[str, Any]:
        signals = GitSignals()
        all_findings = []
        git_dir = root / ".git"

        if not git_dir.exists():
            return {"signals": signals.to_dict(), "findings": []}

        signals.is_git_repo = True
        try:
            # Stats collection
            signals.total_commits = int(self._git_cmd(root, ["rev-list", "--count", "HEAD"]) or 0)
            signals.recent_commits = int(self._git_cmd(root, ["rev-list", "--count", "--since=30.days", "HEAD"]) or 0)
            signals.last_commit_date = (self._git_cmd(root, ["log", "-1", "--format=%ci"]) or "")[:10]

            # Stale Docs Check (Moved from ForensicEngine)
            vision_path = root / 'VISION.md'
            if vision_path.exists():
                doc_ts = self._get_commit_ts(root, "VISION.md")
                repo_ts = self._get_commit_ts(root)
                
                if doc_ts and repo_ts:
                    days_stale = (repo_ts - doc_ts).days
                    if days_stale > 7:
                        all_findings.append(Finding(
                            type='STALE_DOCS',
                            severity='MEDIUM' if days_stale < 30 else 'HIGH',
                            file='VISION.md', line=None,
                            message=f'Documentation is {days_stale} days behind code evolution.',
                            action='Update VISION.md to reflect current architecture.'
                        ))

            # Commit frequency
            if signals.recent_commits >= 20: signals.commit_frequency = "daily"
            elif signals.recent_commits >= 5: signals.commit_frequency = "weekly"
            elif signals.recent_commits >= 1: signals.commit_frequency = "monthly"
            else: signals.commit_frequency = "sporadic"

        except Exception:
            pass

        return {"signals": signals.to_dict(), "findings": all_findings}

    def _git_cmd(self, root: Path, args: list[str]) -> Optional[str]:
        try:
            res = subprocess.run(["git"] + args, cwd=root, capture_output=True, text=True, timeout=5)
            return res.stdout.strip() if res.returncode == 0 else None
        except Exception: return None

    def _get_commit_ts(self, root: Path, file: Optional[str] = None) -> Optional[datetime]:
        args = ["log", "-1", "--format=%ct"]
        if file: args.append(file)
        ts_str = self._git_cmd(root, args)
        if ts_str:
            return datetime.fromtimestamp(int(ts_str), tz=timezone.utc)
        return None
