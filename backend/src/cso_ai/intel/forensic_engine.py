"""
ForensicEngine - The Single Source of Truth for Code Intelligence

This is the DRY consolidation of all forensic detection logic.
Zero business logic. Pure detection.
"""

import os
import ast
import subprocess
from typing import List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Finding:
    """Structured finding from forensic analysis."""
    type: str          # 'SECURITY_PURITY', 'ARCH_PURITY', 'STALE_DOCS', etc.
    severity: str      # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    file: str          # Relative path from project root
    line: Optional[int]  # Line number if applicable
    message: str       # Human-readable description
    action: str        # Recommended fix
    metadata: dict     # Extensible data for context

    def to_dict(self) -> dict:
        return asdict(self)


class ForensicEngine:
    """
    Palantir-tier forensic scanner.
    Detects architectural violations, security gaps, and strategic drift.
    """

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.findings: List[Finding] = []

    def scan(self) -> List[Finding]:
        """Execute full forensic scan."""
        self.findings = []
        
        # 1. Documentation Drift Detection
        self._detect_stale_docs()
        
        # 2. Code Quality Scan
        self._scan_codebase()
        
        # 3. Dependency Analysis
        self._analyze_dependencies()
        
        return self.findings

    def _detect_stale_docs(self):
        """Detect when code evolves faster than documentation."""
        vision_path = self.project_root / 'VISION.md'
        if not vision_path.exists():
            return

        try:
            # Get last commit time for VISION.md
            doc_timestamp = self._get_last_commit_time(str(vision_path))
            
            # Get last commit time for the repo
            repo_timestamp = self._get_last_commit_time()
            
            if doc_timestamp and repo_timestamp:
                days_stale = (repo_timestamp - doc_timestamp).days
                
                if days_stale > 7:
                    self.findings.append(Finding(
                        type='STALE_DOCS',
                        severity='MEDIUM' if days_stale < 30 else 'HIGH',
                        file='VISION.md',
                        line=None,
                        message=f'Documentation is {days_stale} days behind code evolution.',
                        action='Update VISION.md to reflect current architecture.',
                        metadata={'days_stale': days_stale}
                    ))
        except Exception:
            pass  # Not a git repo or git not available

    def _get_last_commit_time(self, file_path: Optional[str] = None) -> Optional[datetime]:
        """Get last commit timestamp for a file or entire repo."""
        try:
            cmd = ['git', 'log', '-1', '--format=%ct']
            if file_path:
                cmd.append(file_path)
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                timestamp = int(result.stdout.strip())
                return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except Exception:
            pass
        
        return None

    def _scan_codebase(self):
        """Scan all code files for violations."""
        for root, dirs, files in os.walk(self.project_root):
            # Skip noise directories
            dirs[:] = [d for d in dirs if d not in {'.git', '.venv', 'node_modules', '__pycache__', '.next', 'dist', 'build'}]
            
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.project_root)
                
                if file.endswith('.py'):
                    self._analyze_python_file(file_path, str(rel_path))
                elif file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                    self._analyze_typescript_file(file_path, str(rel_path))
                elif file.endswith('.sql'):
                    self._analyze_sql_file(file_path, str(rel_path))

    def _analyze_python_file(self, file_path: Path, rel_path: str):
        """AST-based analysis of Python files."""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            # File size check
            if len(lines) > 300:
                self.findings.append(Finding(
                    type='COMPLEXITY',
                    severity='HIGH',
                    file=rel_path,
                    line=None,
                    message=f'File has {len(lines)} lines (threshold: 300).',
                    action='Refactor into smaller modules.',
                    metadata={'line_count': len(lines)}
                ))
            
            # AST-based analysis
            try:
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        func_lines = node.end_lineno - node.lineno + 1
                        if func_lines > 60:
                            self.findings.append(Finding(
                                type='MONOLITH',
                                severity='MEDIUM',
                                file=rel_path,
                                line=node.lineno,
                                message=f'Function `{node.name}` has {func_lines} lines (threshold: 60).',
                                action='Extract into smaller functions.',
                                metadata={'function_name': node.name, 'line_count': func_lines}
                            ))
            except SyntaxError:
                pass  # Ignore syntax errors in parsing
                
        except Exception:
            pass  # Skip files that can't be read

    def _analyze_typescript_file(self, file_path: Path, rel_path: str):
        """Text-based analysis of TypeScript files."""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            # File size check
            if len(lines) > 300:
                self.findings.append(Finding(
                    type='COMPLEXITY',
                    severity='HIGH',
                    file=rel_path,
                    line=None,
                    message=f'File has {len(lines)} lines (threshold: 300).',
                    action='Refactor into smaller components.',
                    metadata={'line_count': len(lines)}
                ))
            
            # Console.log spam detection
            console_count = content.count('console.log')
            if console_count > 3:
                self.findings.append(Finding(
                    type='NOISE',
                    severity='LOW',
                    file=rel_path,
                    line=None,
                    message=f'Found {console_count} console.log statements.',
                    action='Remove debug logs before production.',
                    metadata={'console_count': console_count}
                ))
                
        except Exception:
            pass

    def _analyze_sql_file(self, file_path: Path, rel_path: str):
        """Analyze SQL migration files for security issues."""
        try:
            content = file_path.read_text(encoding='utf-8').lower()
            
            # Check for missing RLS
            if 'create table' in content and 'enable row level security' not in content:
                self.findings.append(Finding(
                    type='SECURITY_PURITY',
                    severity='CRITICAL',
                    file=rel_path,
                    line=None,
                    message='Table creation without Row Level Security (RLS).',
                    action="Add 'ALTER TABLE ... ENABLE ROW LEVEL SECURITY;'",
                    metadata={}
                ))
                
        except Exception:
            pass

    def _analyze_dependencies(self):
        """Analyze package.json for architectural bloat."""
        package_json = self.project_root / 'package.json'
        if not package_json.exists():
            return
            
        try:
            import json
            content = package_json.read_text()
            data = json.loads(content)
            
            # Check for Redux in small projects
            deps = str(data.get('dependencies', {})) + str(data.get('devDependencies', {}))
            if 'redux' in deps.lower():
                # Count TypeScript/React files
                tsx_count = sum(1 for _ in self.project_root.rglob('*.tsx'))
                
                if tsx_count < 20:
                    self.findings.append(Finding(
                        type='ARCH_PURITY',
                        severity='HIGH',
                        file='package.json',
                        line=None,
                        message=f'Redux detected in small project ({tsx_count} components).',
                        action='Consider Zustand or React Context for better velocity.',
                        metadata={'component_count': tsx_count}
                    ))
                    
        except Exception:
            pass
