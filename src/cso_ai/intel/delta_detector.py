"""
CSO.ai Delta Detector - Comprehensive change detection.

Detects semantic changes in codebase:
- Integration changes (LLM providers, APIs, services)
- Tech stack changes (frameworks, dependencies)
- Architecture changes (new modules, patterns)
- Config changes (env vars, settings)
"""

import hashlib
import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from cso_ai.intel.business import BusinessAnalyzer


class DeltaType(str, Enum):
    """Semantic delta types for tracking changes."""

    # Integrations
    INTEGRATION_ADDED = "integration_added"
    INTEGRATION_REMOVED = "integration_removed"
    INTEGRATION_SWITCHED = "integration_switched"

    # Stack
    FRAMEWORK_ADDED = "framework_added"
    FRAMEWORK_REMOVED = "framework_removed"
    DEPENDENCY_MAJOR_UPDATE = "dependency_major_update"

    # Architecture
    MODULE_CREATED = "module_created"
    MODULE_DELETED = "module_deleted"
    PATTERN_CHANGED = "pattern_changed"

    # Config
    ENV_VAR_ADDED = "env_var_added"
    ENV_VAR_REMOVED = "env_var_removed"
    CONFIG_CHANGED = "config_changed"


@dataclass
class Delta:
    """Represents a semantic change detected in the codebase."""

    delta_type: DeltaType
    summary: str
    details: dict[str, Any] = field(default_factory=dict)
    is_significant: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Serialize delta to dict."""
        return {
            "delta_type": self.delta_type.value,
            "summary": self.summary,
            "details": self.details,
            "is_significant": self.is_significant,
        }


@dataclass
class Snapshot:
    """Point-in-time snapshot of codebase state."""

    snapshot_type: str  # 'integrations', 'stack', 'architecture', 'config', 'all'
    data: dict[str, Any]
    hash: str

    @classmethod
    def create(cls, snapshot_type: str, data: dict[str, Any]) -> "Snapshot":
        """Create a snapshot with computed hash."""
        data_str = str(sorted(data.items()))
        snapshot_hash = hashlib.sha256(data_str.encode()).hexdigest()[:16]
        return cls(snapshot_type=snapshot_type, data=data, hash=snapshot_hash)


class CodeScanner:
    """Scans actual code files for integrations, APIs, and patterns."""

    # Directories to skip
    SKIP_DIRS: set[str] = {
        "node_modules",
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
        ".next",
        "target",
        ".idea",
        ".vscode",
        "Pods",
        ".build",
        "DerivedData",
        "vendor",
        ".cursor",
    }

    # Code file extensions to scan
    CODE_EXTENSIONS: set[str] = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".swift",
        ".kt",
        ".java",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".cs",
        ".cpp",
        ".c",
        ".m",
        ".scala",
        ".ex",
        ".exs",
        ".dart",
        ".vue",
        ".svelte",
    }

    def __init__(self) -> None:
        """Initialize code scanner."""
        pass

    def _walk_code_files(self, root: Path) -> list[Path]:
        """Walk all code files, skipping ignored directories."""
        files = []

        def should_skip(path: Path) -> bool:
            return any(part in self.SKIP_DIRS for part in path.parts)

        for path in root.rglob("*"):
            if path.is_file() and not should_skip(path):
                if path.suffix.lower() in self.CODE_EXTENSIONS:
                    files.append(path)

        return files

    async def scan_integrations(self, root: Path) -> dict[str, Any]:
        """
        Scan code for integration usage (imports, API URLs, env vars).

        Returns dict with detected integrations and evidence.
        """
        files = self._walk_code_files(root)
        detected: dict[str, list[str]] = {}  # integration -> [evidence files]

        # Get expanded integration patterns from BusinessAnalyzer (class attribute)
        patterns = BusinessAnalyzer.INTEGRATION_PATTERNS

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                rel_path = str(file_path.relative_to(root))

                # Check each integration pattern
                for integration, pattern_list in patterns.items():
                    for pattern in pattern_list:
                        pattern_lower = pattern.lower()

                        # Check for import statements
                        import_patterns = [
                            rf"import\s+{re.escape(pattern_lower)}",
                            rf"from\s+{re.escape(pattern_lower)}\s+import",
                            rf"require\(['\"]{re.escape(pattern_lower)}['\"]\)",
                            rf"require\(['\"]{re.escape(pattern_lower)}/",
                        ]

                        # Check for API URLs
                        url_patterns = [
                            rf"api\.{re.escape(pattern_lower.replace('@', '').replace('/', '.'))}\.com",
                            rf"https?://[^'\"]*{re.escape(pattern_lower)}",
                        ]

                        # Check for SDK instantiation
                        sdk_patterns = [
                            rf"{integration}\(",
                            rf"new\s+{integration}\(",
                            rf"{pattern_lower}\.",
                        ]

                        # Check for env var references
                        env_patterns = [
                            rf"{pattern_lower.upper().replace('@', '').replace('-', '_')}_API_KEY",
                            rf"process\.env\.{re.escape(pattern_lower.upper())}",
                            rf"os\.environ\.get\(['\"]{re.escape(pattern_lower.upper())}",
                        ]

                        all_patterns = (
                            import_patterns + url_patterns + sdk_patterns + env_patterns
                        )

                        for regex_pattern in all_patterns:
                            if re.search(regex_pattern, content, re.IGNORECASE):
                                if integration not in detected:
                                    detected[integration] = []
                                if rel_path not in detected[integration]:
                                    detected[integration].append(rel_path)
                                break  # Found this integration in this file

            except (OSError, UnicodeDecodeError):
                continue

        return {"integrations": list(detected.keys()), "evidence": detected}

    async def scan_env_vars(self, root: Path) -> dict[str, Any]:
        """Scan for environment variable references in code and config files."""
        files = self._walk_code_files(root)
        env_vars: set[str] = set()

        # Also check config files
        config_files = [
            root / ".env.example",
            root / ".env.template",
            root / "config.toml",
            root / "config.yaml",
            root / "config.yml",
        ]

        for config_file in config_files:
            if config_file.exists():
                files.append(config_file)

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")

                # Find env var patterns
                patterns = [
                    r"([A-Z_][A-Z0-9_]+)\s*=",  # .env files: KEY=value
                    r"os\.environ\.get\(['\"]([A-Z_][A-Z0-9_]+)['\"]",  # Python
                    r"process\.env\.([A-Z_][A-Z0-9_]+)",  # Node.js
                    r"ENV\[['\"]([A-Z_][A-Z0-9_]+)['\"]",  # Ruby
                    r"System\.getenv\(['\"]([A-Z_][A-Z0-9_]+)['\"]",  # Java
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    env_vars.update(matches)

            except (OSError, UnicodeDecodeError):
                continue

        return {"env_vars": sorted(list(env_vars))}

    async def scan_frameworks(self, root: Path) -> dict[str, Any]:
        """Scan for framework usage in code."""
        from cso_ai.intel.technical import TechnicalAnalyzer

        files = self._walk_code_files(root)
        frameworks: set[str] = set()

        # Check framework patterns from TechnicalAnalyzer
        framework_patterns = TechnicalAnalyzer.FRAMEWORK_PATTERNS

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")

                for framework, patterns in framework_patterns.items():
                    for pattern in patterns:
                        if re.search(rf"\b{re.escape(pattern)}\b", content, re.IGNORECASE):
                            frameworks.add(framework)
                            break

            except (OSError, UnicodeDecodeError):
                continue

        return {"frameworks": sorted(list(frameworks))}


class GitDiffAnalyzer:
    """Analyzes git diffs semantically to detect what changed."""

    async def analyze_recent(
        self, root: Path, days: int = 7
    ) -> dict[str, Any]:
        """
        Analyze recent git commits for semantic changes.

        Returns dict with change signals.
        """
        git_dir = root / ".git"
        if not git_dir.exists():
            return {}

        signals: dict[str, Any] = {
            "commits": [],
            "changed_files": [],
            "focus_areas": [],
        }

        try:
            # Get recent commit messages
            result = subprocess.run(
                ["git", "log", f"--since={days}.days.ago", "--oneline", "-20"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                commits = [
                    line.strip()
                    for line in result.stdout.strip().split("\n")
                    if line.strip()
                ]
                signals["commits"] = commits[:10]

            # Get changed files
            result = subprocess.run(
                [
                    "git",
                    "log",
                    f"--since={days}.days.ago",
                    "--name-only",
                    "--format=",
                ],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                files = set(
                    line.strip()
                    for line in result.stdout.strip().split("\n")
                    if line.strip() and not line.startswith(" ")
                )
                signals["changed_files"] = sorted(list(files))[:20]

            # Infer focus areas from commit messages and file paths
            all_text = " ".join(signals["commits"] + signals["changed_files"]).lower()
            focus_keywords = {
                "auth": ["auth", "login", "logout", "session", "jwt"],
                "api": ["api", "endpoint", "route", "rest"],
                "database": ["database", "db", "migration", "schema"],
                "ui": ["ui", "frontend", "component", "css"],
                "testing": ["test", "spec", "mock", "pytest", "jest"],
                "integration": ["integrate", "groq", "anthropic", "openai"],
                "refactor": ["refactor", "cleanup", "reorganize"],
            }

            for area, keywords in focus_keywords.items():
                if any(kw in all_text for kw in keywords):
                    signals["focus_areas"].append(area)

        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass

        return signals


class SnapshotComparer:
    """Compares snapshots to detect semantic deltas."""

    def compare(
        self, old_snapshot: Snapshot | None, new_snapshot: Snapshot
    ) -> list[Delta]:
        """
        Compare two snapshots and generate deltas.

        Args:
            old_snapshot: Previous snapshot (None if first snapshot)
            new_snapshot: Current snapshot

        Returns:
            List of detected deltas
        """
        deltas: list[Delta] = []

        if old_snapshot is None:
            # First snapshot - no deltas to detect
            return deltas

        old_data = old_snapshot.data
        new_data = new_snapshot.data

        # Compare integrations
        if "integrations" in old_data and "integrations" in new_data:
            old_integrations = set(old_data["integrations"])
            new_integrations = set(new_data["integrations"])

            added = new_integrations - old_integrations
            removed = old_integrations - new_integrations

            for integration in added:
                deltas.append(
                    Delta(
                        delta_type=DeltaType.INTEGRATION_ADDED,
                        summary=f"Added integration: {integration}",
                        details={"integration": integration},
                    )
                )

            for integration in removed:
                deltas.append(
                    Delta(
                        delta_type=DeltaType.INTEGRATION_REMOVED,
                        summary=f"Removed integration: {integration}",
                        details={"integration": integration},
                    )
                )

            # Detect switches (common LLM provider switches)
            llm_providers = {"Groq", "OpenAI", "Anthropic", "Mistral", "Cohere"}
            removed_llm = removed & llm_providers
            added_llm = added & llm_providers

            if removed_llm and added_llm:
                from_integration = list(removed_llm)[0]
                to_integration = list(added_llm)[0]
                deltas.append(
                    Delta(
                        delta_type=DeltaType.INTEGRATION_SWITCHED,
                        summary=f"Switched LLM provider: {from_integration} -> {to_integration}",
                        details={
                            "from": from_integration,
                            "to": to_integration,
                        },
                        is_significant=True,
                    )
                )

        # Compare frameworks
        if "frameworks" in old_data and "frameworks" in new_data:
            old_frameworks = set(old_data["frameworks"])
            new_frameworks = set(new_data["frameworks"])

            for framework in new_frameworks - old_frameworks:
                deltas.append(
                    Delta(
                        delta_type=DeltaType.FRAMEWORK_ADDED,
                        summary=f"Added framework: {framework}",
                        details={"framework": framework},
                    )
                )

            for framework in old_frameworks - new_frameworks:
                deltas.append(
                    Delta(
                        delta_type=DeltaType.FRAMEWORK_REMOVED,
                        summary=f"Removed framework: {framework}",
                        details={"framework": framework},
                    )
                )

        # Compare env vars
        if "env_vars" in old_data and "env_vars" in new_data:
            old_env_vars = set(old_data["env_vars"])
            new_env_vars = set(new_data["env_vars"])

            for env_var in new_env_vars - old_env_vars:
                deltas.append(
                    Delta(
                        delta_type=DeltaType.ENV_VAR_ADDED,
                        summary=f"Added environment variable: {env_var}",
                        details={"env_var": env_var},
                        is_significant=False,  # Env vars are less significant
                    )
                )

            for env_var in old_env_vars - new_env_vars:
                deltas.append(
                    Delta(
                        delta_type=DeltaType.ENV_VAR_REMOVED,
                        summary=f"Removed environment variable: {env_var}",
                        details={"env_var": env_var},
                        is_significant=False,
                    )
                )

        return deltas
