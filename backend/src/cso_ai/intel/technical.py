"""
Technical intelligence analyzer for sideMCP.

Analyzes codebases to understand:
- Languages and frameworks
- Architecture patterns (via AST)
- Code health (Complexity, Graphs)
- Git activity
"""

import ast
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from abc import ABC, abstractmethod
from cso_ai.logging_config import get_logger

try:
    from tree_sitter_languages import get_language, get_parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

logger = get_logger(__name__)


@dataclass
class CodeNode:
    """A node in the code graph (Class, Function, or Module)."""
    name: str
    type: str  # 'class', 'function', 'module'
    file_path: str
    start_line: int
    end_line: int
    complexity: int = 1
    docstring: bool = False
    dependencies: list[str] = field(default_factory=list)  # Imports or interactions
    definitions: list[str] = field(default_factory=list)   # Names defined here


@dataclass
class TechnicalIntel:
    """Technical intelligence about a codebase."""

    languages: dict[str, int] = field(default_factory=dict)
    primary_language: str | None = None
    dependencies: dict[str, list[str]] = field(default_factory=dict)
    frameworks: list[str] = field(default_factory=list)
    code_graph: dict[str, CodeNode] = field(default_factory=dict) # True AST Graph
    health_signals: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "languages": self.languages,
            "primary_language": self.primary_language,
            "dependencies": self.dependencies,
            "frameworks": self.frameworks,
            "code_graph_size": len(self.code_graph),
            "health_signals": self.health_signals,
        }


@dataclass
class GitSignals:
    """Git repository signals."""

    is_git_repo: bool = False
    total_commits: int = 0
    recent_commits: int = 0  # Last 30 days
    contributors: list[str] = field(default_factory=list)
    active_branches: list[str] = field(default_factory=list)
    last_commit_date: str | None = None
    commit_frequency: str | None = None  # daily, weekly, monthly, sporadic
    recent_commit_messages: list[str] = field(default_factory=list)  # Last 10 commits
    recent_changed_files: list[str] = field(default_factory=list)  # Recently modified
    current_focus_areas: list[str] = field(default_factory=list)  # Inferred from commits
    is_summarized: bool = False # [Hyper-Ralph] Scenario 33: Huge repo signal

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_git_repo": self.is_git_repo,
            "total_commits": self.total_commits,
            "recent_commits": self.recent_commits,
            "contributors": self.contributors[:5], # Limit to save space
            "active_branches": self.active_branches[:3],
            "last_commit_date": self.last_commit_date,
            "commit_frequency": self.commit_frequency,
            "recent_commit_messages": self.recent_commit_messages[:5],
            "recent_changed_files": self.recent_changed_files[:5],
            "current_focus_areas": self.current_focus_areas,
            "is_summarized": self.is_summarized
        }


@dataclass
class CodeIssues:
    """TODOs, FIXMEs, and other code issues."""

    todos: list[dict[str, str]] = field(default_factory=list)
    fixmes: list[dict[str, str]] = field(default_factory=list)
    hacks: list[dict[str, str]] = field(default_factory=list)
    total_issues: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "todos": self.todos[:10],  # Limit to 10
            "fixmes": self.fixmes[:10],
            "hacks": self.hacks[:10],
            "total_issues": self.total_issues,
        }


class BaseParser(ABC):
    """Abstract base parser for code analysis."""
    
    @abstractmethod
    def parse_file(self, content: str, rel_path: str) -> list[CodeNode]:
        pass


class PythonParser(BaseParser):
    """Parser for Python using native AST module."""

    def parse_file(self, content: str, rel_path: str) -> list[CodeNode]:
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
            
        nodes = []
        imports = []

        # 1. First pass: Collect imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        # 2. Second pass: Collect Definitions (Classes/Functions)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                nodes.append(CodeNode(
                    name=node.name,
                    type="class",
                    file_path=rel_path,
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    complexity=len(node.body), 
                    docstring=ast.get_docstring(node) is not None,
                    dependencies=imports, 
                    definitions=[n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                ))
            elif isinstance(node, ast.FunctionDef):
                nodes.append(CodeNode(
                    name=node.name,
                    type="function",
                    file_path=rel_path,
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    complexity=len(node.body),
                    docstring=ast.get_docstring(node) is not None,
                    dependencies=[], 
                    definitions=[]
                ))
        
        return nodes


class TreeSitterParser(BaseParser):
    """Parser using Tree-Sitter for Polyglot AST (TS, Rust, Go)."""

    # Node type mappings for different languages
    QUERIES = {
        "typescript": """
            (class_declaration name: (type_identifier) @name) @class
            (interface_declaration name: (type_identifier) @name) @interface
            (function_declaration name: (identifier) @name) @function
            (method_definition name: (property_identifier) @name) @method
        """,
        "rust": """
            (struct_item name: (type_identifier) @name) @struct
            (impl_item type: (type_identifier) @name) @impl
            (function_item name: (identifier) @name) @function
        """,
        "go": """
            (type_spec name: (type_identifier) @name) @struct
            (function_declaration name: (identifier) @name) @function
            (method_declaration name: (field_identifier) @name) @method
        """
    }

    def __init__(self, language_name: str):
        if not TREE_SITTER_AVAILABLE:
            raise ImportError("tree-sitter-languages not installed")
        self.language_name = language_name
        self.language = get_language(language_name)
        self.parser = get_parser(language_name)

    def parse_file(self, content: str, rel_path: str) -> list[CodeNode]:
        tree = self.parser.parse(bytes(content, "utf8"))
        root_node = tree.root_node
        nodes = []
        
        # Recursive traversal to find definitions
        self._traverse(root_node, nodes, rel_path)
        return nodes

    def _traverse(self, node: Any, nodes: list[CodeNode], rel_path: str):
        # Generic mapping logic
        node_type = node.type
        
        # TypeScript / JavaScript
        if node_type in ["class_declaration", "interface_declaration", "struct_item", "type_spec"]:
            name = self._get_name(node)
            if name:
                nodes.append(CodeNode(
                    name=name,
                    type="class", # Generalized
                    file_path=rel_path,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    complexity=node.child_count,
                    docstring=False
                ))
        
        elif node_type in ["function_declaration", "function_item", "method_definition", "method_declaration"]:
            name = self._get_name(node)
            if name:
                 nodes.append(CodeNode(
                    name=name,
                    type="function",
                    file_path=rel_path,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    complexity=node.child_count,
                    docstring=False
                ))

        for child in node.children:
            self._traverse(child, nodes, rel_path)

    def _get_name(self, node: Any) -> str | None:
        # Try to find 'name' field
        name_node = node.child_by_field_name("name")
        if name_node:
            return name_node.text.decode("utf8")
        
        # Fallback: look for identifier child
        for i in range(node.child_count):
            child = node.children[i]
            if "identifier" in child.type:
                return child.text.decode("utf8")
        return None


class TechnicalAnalyzer:
    """
    Analyzes technical aspects of a codebase.

    Provides deep understanding of:
    - Languages used and distribution
    - Frameworks and libraries
    - True AST Graph (Python)
    - Code health signals
    - Git history
    """

    # Language detection by extension
    LANGUAGE_MAP: dict[str, str] = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".jsx": "JavaScript",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".java": "Java",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".php": "PHP",
        ".cs": "C#",
        ".cpp": "C++",
        ".c": "C",
        ".m": "Objective-C",
        ".scala": "Scala",
        ".ex": "Elixir",
        ".exs": "Elixir",
        ".dart": "Dart",
        ".vue": "Vue",
        ".svelte": "Svelte",
    }

    # Framework detection from dependencies
    FRAMEWORK_PATTERNS: dict[str, list[str]] = {
        # Python
        "FastAPI": ["fastapi"],
        "Django": ["django"],
        "Flask": ["flask"],
        "Streamlit": ["streamlit"],
        "LangChain": ["langchain"],
        # JavaScript/TypeScript
        "React": ["react", "react-dom"],
        "Next.js": ["next"],
        "Vue": ["vue"],
        "Nuxt": ["nuxt"],
        "Angular": ["@angular/core"],
        "Svelte": ["svelte"],
        "Express": ["express"],
        "NestJS": ["@nestjs/core"],
        "Remix": ["@remix-run/react"],
        "Astro": ["astro"],
        # Mobile
        "React Native": ["react-native"],
        "Flutter": ["flutter"],
        "SwiftUI": ["SwiftUI"],
        "Expo": ["expo"],
        # Others
        "Tailwind CSS": ["tailwindcss"],
        "Prisma": ["@prisma/client"],
        "Drizzle": ["drizzle-orm"],
        "tRPC": ["@trpc/server"],
    }

    # Directories to skip
    SKIP_DIRS: set[str] = {
        "node_modules", ".git", "__pycache__", ".venv", "venv",
        "dist", "build", ".next", "target", ".idea", ".vscode",
        "Pods", ".build", "DerivedData", "vendor", ".cursor",
    }

    # File extensions to scan for TODOs
    CODE_EXTENSIONS: set[str] = {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".swift", ".kt",
        ".java", ".go", ".rs", ".rb", ".php", ".cs", ".cpp",
        ".c", ".m", ".scala", ".ex", ".exs", ".dart", ".vue", ".svelte",
    }

    # Mapping extensions to Tree-Sitter languages
    # Note: Python handled by native parser for speed/deps independence if needed, 
    # but could switch to tree-sitter too. keeping native for now as it's built-in.
    EXTENSION_TO_LANG: dict[str, str] = {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".js": "javascript",
        ".jsx": "javascript",
        ".rs": "rust",
        ".go": "go",
    }

    def __init__(self) -> None:
        """Initialize the analyzer."""
        self._parsers: dict[str, BaseParser] = {}
        # Pre-initialize Python parser
        self._parsers["python"] = PythonParser()

    def _get_parser(self, file_path: Path) -> BaseParser | None:
        """Get appropriate parser for the file."""
        ext = file_path.suffix.lower()
        lang = self.EXTENSION_TO_LANG.get(ext)
        if not lang:
            return None
            
        # Use native Python parser
        if lang == "python":
            return self._parsers["python"]
            
        # Use Tree-Sitter for others
        if not TREE_SITTER_AVAILABLE:
            return None
            
        if lang not in self._parsers:
            try:
                self._parsers[lang] = TreeSitterParser(lang)
            except Exception as e:
                logger.debug(f"Failed to init TreeSitter parser for {lang}: {e}")
                self._parsers[lang] = None # Prevent retry
                return None
                
        return self._parsers.get(lang)

    async def analyze(self, path: str | Path) -> TechnicalIntel:
        """
        Analyze a codebase for technical intelligence.
        
        [Hyper-Ralph] Scenario 33: Added 'Huge Repo' protection.
        If a repo has >5000 files, we switch to shallow analysis mode.
        """
        root = Path(path).resolve()
        intel = TechnicalIntel()

        # Handle empty repo quickly
        try:
            if not any(root.iterdir()):
                 intel.health_signals["status"] = "EMPTY_REPO"
                 return intel
        except (PermissionError, OSError):
             intel.health_signals["status"] = "INACCESSIBLE"
             return intel

        # Pre-check repo size
        all_files = self._walk_files(root)
        is_huge = len(all_files) > 5000
        
        if is_huge:
             logger.warning(f"Project at {path} is HUGE ({len(all_files)} files). Engaging Shallow Analysis Mode.")
             intel.health_signals["analysis_depth"] = "shallow"
             # Filter to only analyze 'important' looking files or top-level ones
             all_files = [f for f in all_files if len(f.parts) <= len(root.parts) + 3] # Limit depth to 3
             all_files = all_files[:1000] # Hard cap

        # Analyze aspect
        intel.languages = await self._detect_languages_with_files(all_files)
        intel.primary_language = self._get_primary_language(intel.languages)
        intel.dependencies = await self._parse_dependencies(root)
        intel.frameworks = self._detect_frameworks(intel.dependencies)
        intel.health_signals = await self._analyze_health(root)

        # 🚀 POLYGLOT AST ANALYSIS
        # We recursively scan files to build the Code Graph using appropriate parsers
        analyzable_files = [f for f in all_files if f.suffix in self.EXTENSION_TO_LANG]
        
        # Cap analysis for speed (per language group or total?)
        # Let's cap total AST processing to 300 files to remain snappy
        for source_file in analyzable_files[:300]:
             try:
                 parser = self._get_parser(source_file)
                 if parser:
                     content = source_file.read_text(encoding="utf-8", errors="replace")
                     rel_path = str(source_file.relative_to(root))
                     nodes = parser.parse_file(content, rel_path)
                     for node in nodes:
                         intel.code_graph[f"{node.file_path}:{node.name}"] = node
             except Exception as e:
                 logger.debug(f"AST Error in {source_file}: {e}")

        # Git analysis (handles huge history internally)
        git_signals = await self._analyze_git(root)
        intel.health_signals["git"] = git_signals.to_dict()
        
        if not git_signals.is_git_repo:
             intel.health_signals["git_status"] = "NOT_A_REPO"

        code_issues = await self._extract_code_issues_from_files(all_files)
        intel.health_signals["code_issues"] = code_issues.to_dict()

        return intel

    async def _detect_languages(self, root: Path) -> dict[str, int]:
        """Count files by programming language."""
        return await self._detect_languages_with_files(self._walk_files(root))

    async def _detect_languages_with_files(self, files: list[Path]) -> dict[str, int]:
        """Count provided files by programming language."""
        counts: dict[str, int] = {}
        for file_path in files:
            ext = file_path.suffix.lower()
            if ext in self.LANGUAGE_MAP:
                lang = self.LANGUAGE_MAP[ext]
                counts[lang] = counts.get(lang, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def _get_primary_language(self, languages: dict[str, int]) -> str | None:
        """Determine the primary language."""
        if not languages:
            return None
        return next(iter(languages))

    async def _parse_dependencies(self, root: Path) -> dict[str, list[str]]:
        """Parse all dependency files."""
        deps: dict[str, list[str]] = {}

        # package.json (npm)
        pkg_json = root / "package.json"
        if pkg_json.exists():
            deps["npm"] = self._parse_package_json(pkg_json)

        # requirements.txt (pip)
        req_txt = root / "requirements.txt"
        if req_txt.exists():
            deps["pip"] = self._parse_requirements_txt(req_txt)

        # pyproject.toml (Python)
        pyproject = root / "pyproject.toml"
        if pyproject.exists():
            deps["python"] = self._parse_pyproject_toml(pyproject)

        # Podfile (CocoaPods)
        podfile = root / "Podfile"
        if podfile.exists():
            deps["cocoapods"] = self._parse_podfile(podfile)

        # Package.swift (Swift PM)
        pkg_swift = root / "Package.swift"
        if pkg_swift.exists():
            deps["swift"] = self._parse_package_swift(pkg_swift)

        # go.mod
        go_mod = root / "go.mod"
        if go_mod.exists():
            deps["go"] = self._parse_go_mod(go_mod)

        # Cargo.toml
        cargo = root / "Cargo.toml"
        if cargo.exists():
            deps["cargo"] = self._parse_cargo_toml(cargo)

        return deps

    def _parse_package_json(self, path: Path) -> list[str]:
        """Parse package.json dependencies."""
        import json
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            deps = list(data.get("dependencies", {}).keys())
            deps.extend(data.get("devDependencies", {}).keys())
            return deps
        except (json.JSONDecodeError, OSError):
            return []

    def _parse_requirements_txt(self, path: Path) -> list[str]:
        """Parse requirements.txt."""
        try:
            content = path.read_text(encoding="utf-8")
            deps = []
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    pkg = line.split("==")[0].split(">=")[0].split("<=")[0].split("[")[0]
                    deps.append(pkg.strip())
            return deps
        except OSError:
            return []

    def _parse_pyproject_toml(self, path: Path) -> list[str]:
        """Parse pyproject.toml dependencies."""
        try:
            content = path.read_text(encoding="utf-8")
            deps = []
            in_deps = False
            for line in content.splitlines():
                if "dependencies" in line and "=" in line:
                    in_deps = True
                    continue
                if in_deps:
                    if line.strip().startswith("]"):
                        in_deps = False
                    elif '"' in line:
                        match = re.search(r'"([^">=<\[]+)', line)
                        if match:
                            deps.append(match.group(1).strip())
            return deps
        except OSError:
            return []

    def _parse_podfile(self, path: Path) -> list[str]:
        """Parse Podfile dependencies."""
        try:
            content = path.read_text(encoding="utf-8")
            pods = re.findall(r"pod\s+['\"]([^'\"]+)['\"]", content)
            return pods
        except OSError:
            return []

    def _parse_package_swift(self, path: Path) -> list[str]:
        """Parse Package.swift dependencies."""
        try:
            content = path.read_text(encoding="utf-8")
            packages = re.findall(r'\.package\([^)]*url:\s*"([^"]+)"', content)
            names = []
            for url in packages:
                if "/" in url:
                    name = url.rstrip("/").split("/")[-1]
                    if name.endswith(".git"):
                        name = name[:-4]
                    names.append(name)
            return names
        except OSError:
            return []

    def _parse_go_mod(self, path: Path) -> list[str]:
        """Parse go.mod dependencies."""
        try:
            content = path.read_text(encoding="utf-8")
            deps = []
            in_require = False
            for line in content.splitlines():
                if line.strip().startswith("require"):
                    in_require = True
                    continue
                if in_require:
                    if line.strip() == ")":
                        in_require = False
                    else:
                        parts = line.strip().split()
                        if parts:
                            deps.append(parts[0])
            return deps
        except OSError:
            return []

    def _parse_cargo_toml(self, path: Path) -> list[str]:
        """Parse Cargo.toml dependencies."""
        try:
            content = path.read_text(encoding="utf-8")
            deps = []
            in_deps = False
            for line in content.splitlines():
                if "[dependencies]" in line or "[dev-dependencies]" in line:
                    in_deps = True
                    continue
                if in_deps:
                    if line.startswith("["):
                        in_deps = False
                    elif "=" in line:
                        pkg = line.split("=")[0].strip()
                        if pkg:
                            deps.append(pkg)
            return deps
        except OSError:
            return []

    def _detect_frameworks(self, dependencies: dict[str, list[str]]) -> list[str]:
        """Detect frameworks from dependencies."""
        all_deps = set()
        for deps in dependencies.values():
            all_deps.update(dep.lower() for dep in deps)

        detected = []
        for framework, patterns in self.FRAMEWORK_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in all_deps:
                    detected.append(framework)
                    break

        return detected

    async def _analyze_health(self, root: Path) -> dict[str, Any]:
        """Analyze code health signals."""
        signals: dict[str, Any] = {}

        # Check for important files
        signals["has_readme"] = (root / "README.md").exists() or (root / "readme.md").exists()
        signals["has_gitignore"] = (root / ".gitignore").exists()
        signals["has_tests"] = (
            (root / "tests").is_dir() or
            (root / "test").is_dir() or
            (root / "__tests__").is_dir() or
            (root / "spec").is_dir()
        )
        signals["has_ci"] = (
            (root / ".github" / "workflows").is_dir() or
            (root / ".gitlab-ci.yml").exists() or
            (root / "Jenkinsfile").exists() or
            (root / ".circleci").is_dir()
        )
        signals["has_docker"] = (root / "Dockerfile").exists()
        signals["has_license"] = (root / "LICENSE").exists() or (root / "LICENSE.md").exists()

        return signals

    async def _analyze_git(self, root: Path) -> GitSignals:
        """Analyze git repository signals."""
        signals = GitSignals()
        git_dir = root / ".git"

        if not git_dir.exists():
            return signals

        signals.is_git_repo = True

        try:
            # Total commits
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                signals.total_commits = int(result.stdout.strip())

            # Recent commits (last 30 days)
            result = subprocess.run(
                ["git", "rev-list", "--count", "--since=30.days", "HEAD"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                signals.recent_commits = int(result.stdout.strip())

            # Contributors
            result = subprocess.run(
                ["git", "log", "--format=%aN", "--since=90.days"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                contributors = set(result.stdout.strip().split("\n"))
                signals.contributors = list(contributors)[:10]

            # Active branches
            result = subprocess.run(
                ["git", "branch", "-r", "--sort=-committerdate"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                branches = [b.strip() for b in result.stdout.strip().split("\n") if b.strip()]
                signals.active_branches = branches[:5]

            # Last commit date
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ci"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                signals.last_commit_date = result.stdout.strip()[:10]

            # Determine commit frequency
            if signals.recent_commits >= 20:
                signals.commit_frequency = "daily"
            elif signals.recent_commits >= 5:
                signals.commit_frequency = "weekly"
            elif signals.recent_commits >= 1:
                signals.commit_frequency = "monthly"
            else:
                signals.commit_frequency = "sporadic"

            # Get recent commit messages (last 10)
            result = subprocess.run(
                ["git", "log", "--oneline", "-10", "--format=%s"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                messages = [m.strip() for m in result.stdout.strip().split("\n") if m.strip()]
                signals.recent_commit_messages = messages[:10]

            # Get recently changed files (last 7 days)
            result = subprocess.run(
                ["git", "log", "--name-only", "--since=7.days", "--format="],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                files = set(f.strip() for f in result.stdout.strip().split("\n") if f.strip())
                signals.recent_changed_files = list(files)[:20]

            # Infer current focus areas from commit messages
            signals.current_focus_areas = self._infer_focus_areas(
                signals.recent_commit_messages,
                signals.recent_changed_files,
            )

        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass

        return signals

    def _infer_focus_areas(
        self,
        commit_messages: list[str],
        changed_files: list[str],
    ) -> list[str]:
        """Infer what the developer is currently working on from git activity."""
        focus_areas: set[str] = set()

        # Keywords to detect in commit messages
        focus_keywords = {
            "auth": ["auth", "login", "logout", "session", "jwt", "oauth", "password"],
            "api": ["api", "endpoint", "route", "rest", "graphql", "request", "response"],
            "database": ["database", "db", "migration", "schema", "query", "sql", "model"],
            "ui": ["ui", "frontend", "component", "css", "style", "layout", "design"],
            "testing": ["test", "spec", "mock", "fixture", "coverage", "pytest", "jest"],
            "docs": ["doc", "readme", "comment", "documentation"],
            "security": ["security", "vulnerability", "auth", "encrypt", "sanitize"],
            "performance": ["performance", "optimize", "cache", "speed", "slow", "fast"],
            "deployment": ["deploy", "docker", "ci", "cd", "pipeline", "build", "release"],
            "refactor": ["refactor", "cleanup", "reorganize", "restructure", "simplify"],
            "bug": ["fix", "bug", "issue", "error", "crash", "broken"],
            "feature": ["add", "new", "feature", "implement", "create"],
            "config": ["config", "env", "setting", "option", "parameter"],
            "integration": ["integrate", "webhook", "api", "stripe", "supabase", "third-party"],
        }

        # Check commit messages
        all_text = " ".join(commit_messages).lower()
        for area, keywords in focus_keywords.items():
            if any(kw in all_text for kw in keywords):
                focus_areas.add(area)

        # Check file paths for additional signals
        all_paths = " ".join(changed_files).lower()
        path_signals = {
            "auth": ["auth", "login", "session"],
            "api": ["api", "routes", "endpoints", "handlers"],
            "database": ["models", "migrations", "schema", "db"],
            "ui": ["components", "views", "pages", "styles", "css"],
            "testing": ["test", "spec", "__tests__"],
            "docs": ["docs", "readme"],
            "config": ["config", ".env", "settings"],
        }

        for area, patterns in path_signals.items():
            if any(p in all_paths for p in patterns):
                focus_areas.add(area)

        return list(focus_areas)[:5]  # Return top 5 focus areas

    async def _extract_code_issues(self, root: Path) -> CodeIssues:
        """Extract TODOs, FIXMEs, and HACKs from the codebase."""
        return await self._extract_code_issues_from_files(self._walk_files(root))

    async def _extract_code_issues_from_files(self, files: list[Path]) -> CodeIssues:
        """Extract issues from a specific list of files."""
        issues = CodeIssues()
        todo_pattern = re.compile(r"TODO[:\s]+(.*)|//\s*TODO\s*(.*)", re.IGNORECASE)
        fixme_pattern = re.compile(r"FIXME[:\s]+(.*)|//\s*FIXME\s*(.*)", re.IGNORECASE)
        hack_pattern = re.compile(r"HACK[:\s]+(.*)|//\s*HACK\s*(.*)", re.IGNORECASE)

        for file_path in files[:500]:  # Safety cap for issue extraction
            if file_path.suffix not in self.CODE_EXTENSIONS:
                continue
                
            try:
                content = file_path.read_text(encoding="utf-8")
                rel_path = str(file_path)
                
                for line_num, line in enumerate(content.splitlines(), 1):
                    # TODOs
                    match = todo_pattern.search(line)
                    if match:
                        text = match.group(1) or match.group(2) or ""
                        issues.todos.append({
                            "file": rel_path,
                            "line": line_num,
                            "text": text.strip()[:100],
                        })

                    # FIXMEs
                    match = fixme_pattern.search(line)
                    if match:
                        text = match.group(1) or match.group(2) or ""
                        issues.fixmes.append({
                            "file": rel_path,
                            "line": line_num,
                            "text": text.strip()[:100],
                        })

                    # HACKs
                    match = hack_pattern.search(line)
                    if match:
                        text = match.group(1) or match.group(2) or ""
                        issues.hacks.append({
                            "file": rel_path,
                            "line": line_num,
                            "text": text.strip()[:100],
                        })

            except (OSError, UnicodeDecodeError):
                continue

        issues.total_issues = len(issues.todos) + len(issues.fixmes) + len(issues.hacks)
        return issues


    async def _parse_cursor_rules(self, root: Path) -> dict[str, Any] | None:
        """Parse .cursorrules or cursor rules file."""
        rules_paths = [
            root / ".cursorrules",
            root / ".cursor" / "rules",
        ]

        for path in rules_paths:
            if path.exists():
                try:
                    content = path.read_text(encoding="utf-8")

                    # Extract key themes from rules
                    themes = []
                    content_lower = content.lower()

                    if "security" in content_lower:
                        themes.append("Security-focused")
                    if "type" in content_lower and ("strict" in content_lower or "safe" in content_lower):
                        themes.append("Type Safety")
                    if "test" in content_lower:
                        themes.append("Testing")
                    if "performance" in content_lower:
                        themes.append("Performance")
                    if "error" in content_lower and "handl" in content_lower:
                        themes.append("Error Handling")
                    if "document" in content_lower or "docstring" in content_lower:
                        themes.append("Documentation")
                    if "clean" in content_lower or "refactor" in content_lower:
                        themes.append("Code Quality")

                    return {
                        "path": str(path.relative_to(root)),
                        "themes": themes,
                        "length": len(content),
                    }
                except (OSError, UnicodeDecodeError):
                    continue

        return None

    def _walk_files(self, root: Path) -> list[Path]:
        """
        Walk files, skipping ignored directories.
        
        [Hyper-Ralph] Scenario 3 Fix: Added symlink loop prevention and 
        depth limiting to prevent hangs in 10GB monoliths.
        """
        files = []
        visited = set()
        max_depth = 20 # Protect against deep recursion

        def should_skip(path: Path) -> bool:
            return any(part in self.SKIP_DIRS for part in path.parts)

        def walk(current_path: Path, depth: int):
            if depth > max_depth:
                return
            
            try:
                # Realpath check to prevent symlink loops
                real_path = current_path.resolve()
                if real_path in visited:
                    return
                visited.add(real_path)

                for path in current_path.iterdir():
                    if should_skip(path):
                        continue
                    
                    if path.is_file():
                        files.append(path)
                    elif path.is_dir():
                        walk(path, depth + 1)
            except (PermissionError, OSError):
                pass

        walk(root, 0)
        return files
