"""
CSO.ai Auto-Intelligence - Zero-setup magic.

Automatically detects your stack on first query with minimal overhead.
Caches profile for 24 hours to ensure instant subsequent queries.

Philosophy: No explicit "analyze_codebase" needed. Just ask and it works.
"""

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from cso_ai.intel.domain import DomainDetector
from cso_ai.intel.technical import TechnicalAnalyzer


@dataclass
class QuickProfile:
    """Lightweight profile for instant queries."""

    path: str
    domain: str | None = None  # Auto-detected business domain (e.g. EdTech)
    languages: dict[str, int] = field(default_factory=dict)
    primary_language: str | None = None
    frameworks: list[str] = field(default_factory=list)
    recent_commits: int = 0
    recent_files: list[str] = field(default_factory=list)
    focus_areas: list[str] = field(default_factory=list)
    project_docs: str = ""  # Content of README/VISION/etc
    stated_priorities: list[str] = field(default_factory=list) # Extracted from docs
    alignment_note: str | None = None # Detected drift note
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return {
            "path": self.path,
            "domain": self.domain,
            "languages": self.languages,
            "primary_language": self.primary_language,
            "frameworks": self.frameworks,
            "recent_commits": self.recent_commits,
            "recent_files": self.recent_files,
            "focus_areas": self.focus_areas,
            "project_docs": self.project_docs,
            "stated_priorities": self.stated_priorities,
            "alignment_note": self.alignment_note,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QuickProfile":
        """Deserialize from dict."""
        return cls(
            path=data["path"],
            domain=data.get("domain"),
            languages=data.get("languages", {}),
            primary_language=data.get("primary_language"),
            frameworks=data.get("frameworks", []),
            recent_commits=data.get("recent_commits", 0),
            recent_files=data.get("recent_files", []),
            focus_areas=data.get("focus_areas", []),
            project_docs=data.get("project_docs", ""),
            stated_priorities=data.get("stated_priorities", []),
            alignment_note=data.get("alignment_note"),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
        )

    def is_expired(self) -> bool:
        """Check if profile has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    def get_hash(self) -> str:
        """Get hash for cache key."""
        key_data = {
            "languages": self.languages,
            "frameworks": self.frameworks,
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()


class AutoIntelligence:
    """
    Auto-detects project intelligence with zero setup.

    Design goals:
    - < 500ms for quick analysis
    - 24-hour cache (balance freshness vs speed)
    - Minimal memory footprint
    - No user intervention required
    """

    def __init__(self):
        """Initialize auto-intelligence."""
        self._cache: dict[str, QuickProfile] = {}
        self._tech_analyzer = TechnicalAnalyzer()

    async def get_or_create_profile(self, path: str | None = None) -> QuickProfile:
        """
        Get cached profile or create new one.

        Args:
            path: Project path. Defaults to current working directory.

        Returns:
            QuickProfile with stack information
        """
        if path is None:
            path = os.getcwd()

        path = str(Path(path).resolve())

        # Check in-memory cache first
        if path in self._cache:
            profile = self._cache[path]
            if not profile.is_expired():
                return profile

        # Check database cache (persistent across restarts)
        try:
            from cso_ai.storage.simple_db import SimplifiedDatabase
            db = SimplifiedDatabase()
            db_profile = db.get_profile(path)
            
            if db_profile:
                # Convert from DB format to QuickProfile
                profile = QuickProfile(
                    path=db_profile["path"],
                    languages=db_profile.get("languages", {}),
                    primary_language=db_profile.get("primary_language"),
                    frameworks=db_profile.get("frameworks", []),
                    recent_commits=db_profile.get("recent_commits", 0),
                    recent_files=db_profile.get("recent_files", []),
                    focus_areas=db_profile.get("focus_areas", []),
                    project_docs=db_profile.get("project_docs", ""),
                    stated_priorities=db_profile.get("stated_priorities", []),
                    alignment_note=db_profile.get("alignment_note"),
                    created_at=datetime.fromisoformat(db_profile["created_at"]) if db_profile.get("created_at") else datetime.now(timezone.utc),
                    expires_at=datetime.fromisoformat(db_profile["updated_at"]) + timedelta(hours=24) if db_profile.get("updated_at") else datetime.now(timezone.utc) + timedelta(hours=24),
                )
                
                # Check if expired (24 hours)
                if not profile.is_expired():
                    self._cache[path] = profile
                    return profile
        except Exception:
            # If database fails, continue to analysis
            pass

        # Create new profile by analyzing
        profile = await self._quick_analyze(path)
        
        # Save to in-memory cache
        self._cache[path] = profile
        
        # Save to database for persistence
        try:
            from cso_ai.storage.simple_db import SimplifiedDatabase
            db = SimplifiedDatabase()
            db.save_profile(
                path=profile.path,
                languages=profile.languages,
                primary_language=profile.primary_language,
                frameworks=profile.frameworks,
                recent_commits=profile.recent_commits,
                recent_files=profile.recent_files,
                focus_areas=profile.focus_areas,
                project_docs=profile.project_docs,
                stated_priorities=profile.stated_priorities,
                alignment_note=profile.alignment_note,
            )
        except Exception:
            # If database save fails, that's okay - we have the profile
            pass
        
        return profile

    async def _quick_analyze(self, path: str) -> QuickProfile:
        """
        Quick analysis focusing on essentials.

        Target: < 500ms total
        - Language detection: ~100ms
        - Framework detection: ~100ms
        - Git activity: ~200ms
        """
        root = Path(path)

        if not root.exists() or not root.is_dir():
            # Return empty profile for invalid paths
            return QuickProfile(path=path)

        # Detect languages (fast file counting)
        languages = await self._detect_languages_fast(root)
        primary_language = self._get_primary_language(languages)

        # Detect frameworks from dependencies (fast file reading)
        frameworks = await self._detect_frameworks_fast(root)

        # Get recent git activity (if git repo)
        recent_commits, recent_files, focus_areas = await self._get_git_activity(root)
        
        # Detect business domain (The "Intelligence Agency" Moat)
        detector = DomainDetector()
        domain_info = detector.detect(root)
        domain = domain_info.get("domain", "General Software")

        # Read important docs (README, VISION, etc.)
        project_docs, stated_priorities = await self._read_project_docs(root)

        profile = QuickProfile(
            path=path,
            domain=domain,
            languages=languages,
            primary_language=primary_language,
            frameworks=frameworks,
            recent_commits=recent_commits,
            recent_files=recent_files,
            focus_areas=focus_areas,
            project_docs=project_docs,
            stated_priorities=stated_priorities,
        )

        # Check for Strategic Alignment (Stage 2)
        profile.alignment_note = self._check_strategic_alignment(profile)

        return profile

    async def _read_project_docs(self, root: Path) -> tuple[str, list[str]]:
        """
        Read project docs with Truth Hierarchy (Decay Profiles) and Priority Extraction.
        
        Recognizes that not all docs are equal:
        - Foundational: README, ARCHITECTURE (Trusted for months)
        - Strategic: VISION (Trusted for weeks)
        - Volatile: ROADMAP, ACTIVE (Trusted for days)
        """
        docs = []
        stated_priorities = []
        now = datetime.now()
        
        # Configuration: Truth Hierarchy
        # file_pattern -> (type_name, warning_days_threshold)
        DOC_PROFILES = {
            "README.md": ("Foundational", 180),      # Standard of truth, changes rarely
            "ARCHITECTURE.md": ("Foundational", 180),
            "VISION.md": ("Strategic", 90),          # Vision stays valid longer than tasks
            "docs/VISION.md": ("Strategic", 90),
            "direction/roadmap/ACTIVE.md": ("Volatile", 7), # Sprints change weekly
            "ACTIVE.md": ("Volatile", 7),
            "ROADMAP.md": ("Volatile", 14),
            "TODO.md": ("Volatile", 3),             # TODOs rot instantly
        }
        
        # Priority sort: Volatile (most specific) -> Strategic -> Foundational
        # We read them in specific order to put most relevant context first? 
        # Actually LLM reads top-down. 
        # Strategy: Present Foundational first (Context), then Volatile (Current State).
        files_to_read = [
            "VISION.md", 
            "docs/VISION.md",
            "README.md", 
            "ARCHITECTURE.md", 
            "direction/roadmap/ACTIVE.md",
            "ACTIVE.md",
            "ROADMAP.md",
            "TODO.md"
        ]
        
        for name in files_to_read:
            f = root / name
            if f.exists():
                try:
                    # Determine Profile
                    profile_name, warn_threshold = DOC_PROFILES.get(name, ("General", 30))
                    
                    # Check modification time
                    stats = f.stat()
                    mtime = datetime.fromtimestamp(stats.st_mtime)
                    age_days = (now - mtime).days
                    
                    # Read first 3KB (increased from 2KB for better context)
                    content = f.read_text(encoding="utf-8")[:3000]
                    
                    # Construct Header with "Palantir-level" precision
                    header = f"--- [{profile_name.upper()}] {name} ---\n"
                    header += f"Last updated: {age_days} days ago\n"
                    
                    # Status Injection
                    if age_days > warn_threshold:
                        header += f"⚠️ STATUS: STALE (>{warn_threshold} days). Low reliability.\n"
                    elif age_days <= 2:
                        header += f"✅ STATUS: FRESH (Just updated). High reliability.\n"
                    else:
                        header += f"ℹ️ STATUS: VALID (Within {warn_threshold} day window).\n"
                    
                    # Extraction Logic for stated priorities (Heuristic)
                    if profile_name in ["Strategic", "Volatile"]:
                        stated_priorities.extend(self._extract_priorities_from_text(content))
                        
                    docs.append(f"{header}\n{content}\n")
                except Exception:
                    pass
                    
        return "\n".join(docs)[:6000], list(set(stated_priorities))

    def _extract_priorities_from_text(self, text: str) -> list[str]:
        """Extract priorities/goals from text using heuristics."""
        priorities = []
        lines = text.split("\n")
        
        # Look for bullet points or keywords
        keywords = ["focus:", "goal:", "priority:", "working on:", "target:"]
        
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Match bullet points under sections like ## Priorities
            if line_stripped.startswith("- ") or line_stripped.startswith("* ") or line_stripped.startswith("1. "):
                item = line_stripped.lstrip("-*123456789. ").strip()
                if 3 < len(item) < 100:
                    priorities.append(item)
            
            # Match specific keywords
            for kw in keywords:
                if kw in line_lower:
                    item = line_lower.split(kw, 1)[1].strip()
                    if item:
                        priorities.append(item)
                        
        return priorities[:10]

    def _check_strategic_alignment(self, profile: QuickProfile) -> str | None:
        """
        Detect alignment between STATED priorities (docs) and ACTUAL focus (git).
        
        Returns a note if significant drift is detected.
        """
        if not profile.stated_priorities or not profile.focus_areas:
            return None
            
        stated = [p.lower() for p in profile.stated_priorities]
        actual = [f.lower() for f in profile.focus_areas]
        
        # Check if ANY actual work matches ANY stated priority
        alignment_found = False
        for a_task in actual:
            # Simple keyword matching
            words = a_task.split()
            for p_task in stated:
                if any(word in p_task for word in words if len(word) > 3):
                    alignment_found = True
                    break
            if alignment_found:
                break
                
        if not alignment_found:
            top_stated = profile.stated_priorities[0] if profile.stated_priorities else "Unknown"
            top_actual = profile.focus_areas[0] if profile.focus_areas else "Unknown"
            return f"Strategic Drift: Your documentation says you're focused on '{top_stated}', but your recent work is mostly on '{top_actual}'."
            
        return None

    async def _detect_languages_fast(self, root: Path) -> dict[str, int]:
        """
        FAST language detection using sampling.
        
        Target: <100ms even for huge codebases
        Strategy: Sample files instead of scanning everything
        """
        from cso_ai.intel.technical import TechnicalAnalyzer
        
        counts: dict[str, int] = {}
        files_scanned = 0
        max_files = 500  # Only scan first 500 files
        
        # Use iterator instead of building full list
        for path in root.rglob("*"):
            # Skip directories and ignored paths
            if not path.is_file():
                continue
            
            # Check if should skip (node_modules, .git, etc.)
            if any(part in TechnicalAnalyzer.SKIP_DIRS for part in path.parts):
                continue
            
            # Count this file
            ext = path.suffix.lower()
            if ext in TechnicalAnalyzer.LANGUAGE_MAP:
                lang = TechnicalAnalyzer.LANGUAGE_MAP[ext]
                counts[lang] = counts.get(lang, 0) + 1
            
            files_scanned += 1
            
            # Early termination - we have enough data
            if files_scanned >= max_files:
                break
        
        # Return top 5 languages only
        sorted_langs = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_langs[:5])

    def _get_primary_language(self, languages: dict[str, int]) -> str | None:
        """Get primary language."""
        if not languages:
            return None
        return max(languages.items(), key=lambda x: x[1])[0]

    async def _detect_frameworks_fast(self, root: Path) -> list[str]:
        """Fast framework detection from dependency files."""
        frameworks = []

        # Check package.json
        package_json = root / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                    # Common frameworks
                    if "react" in deps:
                        frameworks.append("React")
                    if "vue" in deps:
                        frameworks.append("Vue")
                    if "next" in deps:
                        frameworks.append("Next.js")
                    if "@angular/core" in deps:
                        frameworks.append("Angular")
            except Exception:
                pass

        # Check pyproject.toml / requirements.txt
        pyproject = root / "pyproject.toml"
        requirements = root / "requirements.txt"

        if pyproject.exists():
            try:
                content = pyproject.read_text()
                if "fastapi" in content.lower():
                    frameworks.append("FastAPI")
                if "django" in content.lower():
                    frameworks.append("Django")
                if "flask" in content.lower():
                    frameworks.append("Flask")
            except Exception:
                pass
        elif requirements.exists():
            try:
                content = requirements.read_text().lower()
                if "fastapi" in content:
                    frameworks.append("FastAPI")
                if "django" in content:
                    frameworks.append("Django")
                if "flask" in content:
                    frameworks.append("Flask")
            except Exception:
                pass

        return frameworks[:5]  # Top 5 only

    async def _get_git_activity(self, root: Path) -> tuple[int, list[str], list[str]]:
        """Get recent git activity (last 7 days)."""
        import subprocess

        if not (root / ".git").exists():
            return 0, [], []

        try:
            # Get commit count (last 7 days)
            result = subprocess.run(
                ["git", "log", "--oneline", "--since=7.days.ago"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=2,
            )
            commits = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0

            # Get changed files (last 7 days)
            result = subprocess.run(
                ["git", "log", "--name-only", "--pretty=format:", "--since=7.days.ago"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=2,
            )
            files = [f for f in result.stdout.strip().split("\n") if f]
            unique_files = list(set(files))[:10]  # Top 10 unique files

            # Infer focus areas from file paths
            focus_areas = self._infer_focus_from_files(unique_files)

            return commits, unique_files, focus_areas

        except Exception:
            return 0, [], []

    def _infer_focus_from_files(self, files: list[str]) -> list[str]:
        """Infer what developer is working on from changed files."""
        focus = set()

        for file in files:
            path_lower = file.lower()

            # API/Backend
            if any(x in path_lower for x in ["api", "endpoint", "route", "controller"]):
                focus.add("API development")

            # Frontend
            if any(x in path_lower for x in ["component", "page", "view", "ui"]):
                focus.add("Frontend")

            # Auth
            if any(x in path_lower for x in ["auth", "login", "user", "session"]):
                focus.add("Authentication")

            # Database
            if any(x in path_lower for x in ["model", "schema", "migration", "db"]):
                focus.add("Database")

            # Testing
            if any(x in path_lower for x in ["test", "spec"]):
                focus.add("Testing")

            # Config/Infrastructure
            if any(x in path_lower for x in ["config", "docker", "deploy", ".yml", ".yaml"]):
                focus.add("Infrastructure")

        return list(focus)[:3]  # Top 3 focus areas

    async def detect_goal_completion(self, goals: list[dict], path: str | None = None) -> list[dict]:
        """
        PROACTIVE: Detect if any goals were completed based on git commits.
        
        Matches commit messages against goal titles using fuzzy matching.
        
        Args:
            goals: List of goal dicts with 'id' and 'title'
            path: Project path (defaults to cwd)
            
        Returns:
            List of {'goal_id', 'goal_title', 'commit_message', 'confidence'}
        """
        if not goals:
            return []
        
        root = Path(path) if path else Path.cwd()
        git_dir = root / ".git"
        if not git_dir.exists():
            return []
        
        try:
            import subprocess
            result = subprocess.run(
                ["git", "-C", str(root), "log", "--oneline", "-10"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return []
            
            commits = result.stdout.strip().split("\n")
            detected = []
            
            for goal in goals:
                title_words = set(goal["title"].lower().split())
                
                for commit in commits:
                    if not commit:
                        continue
                    commit_words = set(commit.lower().split())
                    
                    # Simple word overlap matching
                    overlap = title_words & commit_words
                    # Require at least 2 words or 50% overlap
                    min_required = max(2, len(title_words) // 2)
                    
                    if len(overlap) >= min_required:
                        detected.append({
                            "goal_id": goal["id"],
                            "goal_title": goal["title"],
                            "commit_message": commit,
                            "confidence": len(overlap) / len(title_words)
                        })
                        break  # One match per goal
            
            return detected
            
        except Exception:
            return []
