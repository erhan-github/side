"""
Code Quality Probe - Comprehensive code quality audit.

Forensic-level code quality checks covering:
- Error handling patterns
- Function complexity
- Documentation coverage
- Type annotations
- Code organization
"""

import re
import ast
from pathlib import Path
from typing import List
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier, AuditFixRisk


class CodeQualityProbe:
    """Forensic-level code quality audit probe."""
    
    id = "forensic.code_quality"
    name = "Code Quality Audit"
    tier = Tier.FAST
    dimension = "Code Quality"
    
    def run(self, context: ProbeContext) -> List[AuditResult]:
        """Run all code quality checks."""
        return [
            self._check_bare_except(context),
            self._check_try_except_coverage(context),
            self._check_function_length(context),
            self._check_file_length(context),
            self._check_docstring_coverage(context),
            self._check_type_annotations(context),
            self._check_complexity(context),
            self._check_dead_code(context),
            # Architecture Intelligence
            self._check_pattern_duplication(context),
            self._check_folder_structure(context),
            self._check_file_split_opportunities(context),
            self._check_helper_extraction(context),
        ]
    
    def _check_bare_except(self, context: ProbeContext) -> AuditResult:
        """Check for bare except clauses."""
        evidence = []
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                for line_idx, line in enumerate(content.splitlines(), 1):
                    stripped = line.strip()
                    if stripped == 'except:' or stripped.startswith('except: '):
                        evidence.append(AuditEvidence(
                            description="Bare except clause",
                            file_path=file_path,
                            line_number=line_idx,
                            context=line.strip(),
                            suggested_fix="except Exception as e:"
                        ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="CQ-001",
            check_name="No Bare Except Clauses",
            dimension=self.dimension,
            status=AuditStatus.FAIL if evidence else AuditStatus.PASS,
            severity=Severity.MEDIUM,
            evidence=evidence,
            notes=f"Found {len(evidence)} bare except clauses",
            recommendation="Use 'except Exception as e:' to capture and log errors",
            effort_hours=1
        )
    
    def _check_try_except_coverage(self, context: ProbeContext) -> AuditResult:
        """Check for adequate error handling coverage."""
        total_functions = 0
        functions_with_try = 0
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        total_functions += 1
                        # Check if function has try/except
                        for child in ast.walk(node):
                            if isinstance(child, ast.Try):
                                functions_with_try += 1
                                break
            except Exception:
                continue
        
        coverage = (functions_with_try / total_functions * 100) if total_functions > 0 else 0
        
        return AuditResult(
            check_id="CQ-002",
            check_name="Error Handling Coverage",
            dimension=self.dimension,
            status=AuditStatus.PASS if coverage >= 30 else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            notes=f"{coverage:.1f}% of functions have try/except ({functions_with_try}/{total_functions})",
            recommendation="Add error handling to critical paths (>30% coverage target)"
        )
    
    def _check_function_length(self, context: ProbeContext) -> AuditResult:
        """Check for overly long functions."""
        evidence = []
        max_lines = 100
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                            length = node.end_lineno - node.lineno
                            if length > max_lines:
                                evidence.append(AuditEvidence(
                                    description=f"Function '{node.name}' is {length} lines (max: {max_lines})",
                                    file_path=file_path,
                                    line_number=node.lineno,
                                    suggested_fix="Break into smaller, focused functions"
                                ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="CQ-003",
            check_name="Function Length Limits",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.LOW,
            evidence=evidence[:10],
            recommendation=f"Keep functions under {max_lines} lines"
        )
    
    def _check_file_length(self, context: ProbeContext) -> AuditResult:
        """Check for overly long files."""
        evidence = []
        max_lines = 500
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                lines = len(content.splitlines())
                if lines > max_lines:
                    evidence.append(AuditEvidence(
                        description=f"File is {lines} lines (max: {max_lines})",
                        file_path=file_path,
                        suggested_fix="Split into multiple modules"
                    ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="CQ-004",
            check_name="File Length Limits",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.LOW,
            evidence=evidence[:10],
            recommendation=f"Keep files under {max_lines} lines"
        )
    
    def _check_docstring_coverage(self, context: ProbeContext) -> AuditResult:
        """Check for docstring coverage."""
        total_functions = 0
        documented_functions = 0
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            if 'test' in file_path.lower():
                continue
            
            try:
                content = Path(file_path).read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if node.name.startswith('_'):
                            continue  # Skip private functions
                        total_functions += 1
                        if ast.get_docstring(node):
                            documented_functions += 1
            except Exception:
                continue
        
        coverage = (documented_functions / total_functions * 100) if total_functions > 0 else 0
        
        return AuditResult(
            check_id="CQ-005",
            check_name="Docstring Coverage",
            dimension=self.dimension,
            status=AuditStatus.PASS if coverage >= 50 else AuditStatus.WARN,
            severity=Severity.LOW,
            notes=f"{coverage:.1f}% of public functions have docstrings ({documented_functions}/{total_functions})",
            recommendation="Add docstrings to all public functions (>50% target)"
        )
    
    def _check_type_annotations(self, context: ProbeContext) -> AuditResult:
        """Check for type annotation usage."""
        total_functions = 0
        annotated_functions = 0
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        total_functions += 1
                        # Check return annotation or arg annotations
                        if node.returns or any(a.annotation for a in node.args.args):
                            annotated_functions += 1
            except Exception:
                continue
        
        coverage = (annotated_functions / total_functions * 100) if total_functions > 0 else 0
        
        return AuditResult(
            check_id="CQ-006",
            check_name="Type Annotation Coverage",
            dimension=self.dimension,
            status=AuditStatus.PASS if coverage >= 50 else AuditStatus.WARN,
            severity=Severity.LOW,
            notes=f"{coverage:.1f}% of functions have type annotations ({annotated_functions}/{total_functions})",
            recommendation="Add type annotations for better IDE support and documentation"
        )
    
    def _check_complexity(self, context: ProbeContext) -> AuditResult:
        """Check for high cyclomatic complexity."""
        evidence = []
        max_complexity = 15  # McCabe threshold
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Simple complexity: count decision points
                        complexity = 1
                        for child in ast.walk(node):
                            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                                complexity += 1
                            elif isinstance(child, ast.BoolOp):
                                complexity += len(child.values) - 1
                        
                        if complexity > max_complexity:
                            evidence.append(AuditEvidence(
                                description=f"Function '{node.name}' has complexity {complexity} (max: {max_complexity})",
                                file_path=file_path,
                                line_number=node.lineno,
                                suggested_fix="Break into smaller functions"
                            ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="CQ-007",
            check_name="Cyclomatic Complexity",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence[:10],
            recommendation=f"Keep cyclomatic complexity under {max_complexity}"
        )
    
    def _check_dead_code(self, context: ProbeContext) -> AuditResult:
        """Check for obvious dead code patterns."""
        evidence = []
        
        patterns = [
            (r'^\s*#.*TODO.*remove', "TODO remove comment"),
            (r'^\s*#.*FIXME.*delete', "FIXME delete comment"),
            (r'^\s*pass\s*#.*temp', "Temporary pass statement"),
            (r'if\s+False\s*:', "if False: dead code"),
            (r'return\s*\n\s+[^\s#]', "Code after return"),
        ]
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                for line_idx, line in enumerate(content.splitlines(), 1):
                    for pattern, desc in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            evidence.append(AuditEvidence(
                                description=desc,
                                file_path=file_path,
                                line_number=line_idx
                            ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="CQ-008",
            check_name="No Dead Code",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.LOW,
            evidence=evidence[:10],
            recommendation="Remove dead code and TODO-remove comments"
        )

    # =========================================================================
    # ARCHITECTURE INTELLIGENCE CHECKS
    # =========================================================================
    
    def _check_pattern_duplication(self, context: ProbeContext) -> AuditResult:
        """Detect semantically similar code patterns (e.g., repeated if/elif chains)."""
        from collections import defaultdict
        import hashlib
        
        # Pattern cache: {pattern_hash: [(file, line, pattern_repr)]}
        conditional_patterns = defaultdict(list)
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.If):
                        # Hash the if/elif chain structure
                        pattern_repr = self._extract_conditional_pattern(node)
                        if pattern_repr and len(pattern_repr) >= 3:  # At least 3 branches
                            pattern_hash = hashlib.md5(pattern_repr.encode()).hexdigest()[:8]
                            
                            # Also capture code snippet for LLM analysis
                            snippet = self._extract_code_snippet(content, node.lineno, 10)
                            
                            conditional_patterns[pattern_hash].append({
                                'file': file_path,
                                'line': node.lineno,
                                'preview': pattern_repr[:100],
                                'snippet': snippet
                            })
            except Exception:
                continue
        
        # Find patterns that appear 3+ times
        duplicates = {k: v for k, v in conditional_patterns.items() if len(v) >= 3}
        evidence = []
        
        # LLM Enhancement: Get intelligent suggestions for top duplicates
        llm_suggestion = None
        if duplicates:
            try:
                from ..architecture_advisor import get_architecture_advisor
                advisor = get_architecture_advisor()
                
                # Analyze the most common duplicate
                top_pattern = list(duplicates.values())[0]
                llm_suggestion = advisor.analyze_duplicate_patterns(top_pattern)
            except Exception:
                pass  # LLM is optional
        
        for pattern_hash, occurrences in list(duplicates.items())[:3]:  # Top 3
            files = [f"{Path(o['file']).name}:{o['line']}" for o in occurrences]
            
            # Use LLM suggestion if available
            suggested_fix = llm_suggestion if llm_suggestion else "Extract to a shared helper function"
            
            evidence.append(AuditEvidence(
                description=f"Similar conditional pattern found {len(occurrences)} times",
                context=f"Files: {', '.join(files[:4])}",
                suggested_fix=suggested_fix
            ))
        
        return AuditResult(
            check_id="CQ-010",
            check_name="Code Pattern Duplication",
            dimension=self.dimension,
            status=AuditStatus.PASS if not duplicates else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence,
            notes=f"Found {len(duplicates)} duplicate code patterns" if duplicates else "No major duplications detected",
            recommendation="Extract repeated patterns into reusable helper functions"
        )
    
    def _extract_code_snippet(self, content: str, start_line: int, num_lines: int = 10) -> str:
        """Extract a code snippet around a given line."""
        lines = content.splitlines()
        start = max(0, start_line - 1)
        end = min(len(lines), start + num_lines)
        return "\n".join(lines[start:end])
    
    def _extract_conditional_pattern(self, if_node: ast.If) -> str:
        """Extract a hashable representation of an if/elif chain."""
        branches = []
        current = if_node
        
        while current:
            # Capture the structure of the condition
            try:
                if isinstance(current.test, ast.Compare):
                    # e.g., x >= 90
                    ops = [type(op).__name__ for op in current.test.ops]
                    branches.append(f"CMP:{','.join(ops)}")
                elif isinstance(current.test, ast.BoolOp):
                    branches.append(f"BOOL:{type(current.test.op).__name__}")
                else:
                    branches.append(f"OTHER:{type(current.test).__name__}")
            except Exception:
                branches.append("UNKNOWN")
            
            # Move to elif
            if current.orelse and len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                current = current.orelse[0]
            else:
                if current.orelse:
                    branches.append("ELSE")
                break
        
        return "|".join(branches)
    
    def _check_folder_structure(self, context: ProbeContext) -> AuditResult:
        """Analyze folder organization for bloat and chaos."""
        from collections import defaultdict
        
        folders = defaultdict(list)
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            folder = str(Path(file_path).parent)
            folders[folder].append(Path(file_path).name)
        
        evidence = []
        
        for folder, files in folders.items():
            # Flag folders with > 15 Python files
            if len(files) > 15:
                relative = folder.replace(context.project_root, '').lstrip('/')
                evidence.append(AuditEvidence(
                    description=f"Folder has {len(files)} files (suggesting subfolders)",
                    file_path=folder,
                    context=f"Files: {', '.join(files[:5])}...",
                    suggested_fix=f"Consider splitting into subfolders"
                ))
        
        return AuditResult(
            check_id="CQ-011",
            check_name="Folder Structure Organization",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.LOW,
            evidence=evidence[:5],
            notes=f"Found {len(evidence)} folders with many files" if evidence else "Folder structure is well organized",
            recommendation="Split large folders into logical subfolders"
        )
    
    def _check_file_split_opportunities(self, context: ProbeContext) -> AuditResult:
        """Suggest how to split large files based on function groupings."""
        from collections import defaultdict
        
        evidence = []
        max_lines = 400
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                lines = len(content.splitlines())
                
                if lines <= max_lines:
                    continue
                
                tree = ast.parse(content)
                
                # Group functions by prefix
                function_groups = defaultdict(list)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        name = node.name
                        if name.startswith('_'):
                            parts = name[1:].split('_')
                        else:
                            parts = name.split('_')
                        
                        prefix = parts[0] if parts else 'misc'
                        function_groups[prefix].append(name)
                
                # Find groups with 4+ functions (good split candidates)
                suggestions = []
                for prefix, funcs in function_groups.items():
                    if len(funcs) >= 4:
                        suggestions.append(f"{prefix}_*.py: {', '.join(funcs[:3])}")
                
                if suggestions:
                    evidence.append(AuditEvidence(
                        description=f"File is {lines} lines with splittable groups",
                        file_path=file_path,
                        context=f"Suggested splits: {'; '.join(suggestions[:3])}",
                        suggested_fix="Extract function groups into separate modules"
                    ))
            except Exception:
                continue
        
        return AuditResult(
            check_id="CQ-012",
            check_name="File Split Opportunities",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.INFO,
            severity=Severity.LOW,
            evidence=evidence[:5],
            notes=f"Found {len(evidence)} files that could be split" if evidence else "No obvious split opportunities",
            recommendation="Split large files into focused modules"
        )
    
    def _check_helper_extraction(self, context: ProbeContext) -> AuditResult:
        """Find repeated inline patterns that should be extracted to helpers."""
        from collections import defaultdict
        
        # Track common patterns
        patterns_found = defaultdict(list)
        
        # Regex patterns to look for repeated inline logic
        helper_patterns = [
            (r'if\s+\w+\s*>=?\s*\d+.*elif\s+\w+\s*>=?\s*\d+', 'threshold_check'),
            (r're\.search\([\'"][^\'"]+[\'"]\s*,', 'regex_pattern'),
            (r'\.get\([\'"][^\'"]+[\'"]\s*,\s*[\'"]?[^\)]+[\'"]?\)', 'dict_get_default'),
            (r'datetime\.(now|utcnow)\(\)', 'timestamp_creation'),
            (r'Path\([^\)]+\)\.(read_text|read_bytes)\(\)', 'file_reading'),
        ]
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                for line_idx, line in enumerate(content.splitlines(), 1):
                    for pattern, name in helper_patterns:
                        if re.search(pattern, line):
                            patterns_found[name].append({
                                'file': file_path,
                                'line': line_idx,
                                'snippet': line.strip()[:60]
                            })
            except Exception:
                continue
        
        # Find patterns used 5+ times
        candidates = {k: v for k, v in patterns_found.items() if len(v) >= 5}
        
        evidence = []
        for pattern_name, occurrences in candidates.items():
            files = list(set(Path(o['file']).name for o in occurrences))
            evidence.append(AuditEvidence(
                description=f"'{pattern_name}' pattern found {len(occurrences)} times",
                context=f"Files: {', '.join(files[:4])}",
                suggested_fix=f"Consider extracting to utils/{pattern_name}_helper()"
            ))
        
        return AuditResult(
            check_id="CQ-013",
            check_name="Helper Extraction Opportunities",
            dimension=self.dimension,
            status=AuditStatus.PASS if not candidates else AuditStatus.INFO,
            severity=Severity.LOW,
            evidence=evidence[:5],
            notes=f"Found {len(candidates)} patterns that could be helpers" if candidates else "Code is well-factored",
            recommendation="Extract repeated patterns into utility functions"
        )
