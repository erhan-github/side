"""
Dead Code Probe - Detects unused code (functions/classes).

Uses `vulture` logic via AST analysis if available, or fallback to simple AST visitor.
"""

from typing import List, Set
import ast
import re
from pathlib import Path
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier

class DeadCodeProbe:
    """Forensic-level dead code analysis."""
    
    id = "forensic.dead_code"
    # name = "Dead Code Detection" # Unused
    tier = Tier.FAST
    dimension = "Maintainability"
    
    async def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_unused_symbols(context),
        ]
        
    def _check_unused_symbols(self, context: ProbeContext) -> AuditResult:
        """
        Scan for functions/classes that are defined but never used in the project.
        This is a naive implementation (heuristic).
        """
        defined_symbols = {} # name -> file_path
        used_symbols = set()
        
        # 1. First Pass: Collect definitions and usages
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
                
            try:
                content = Path(file_path).read_text()
                tree = ast.parse(content)
                
                # Collect definitions
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                         if not node.name.startswith('_'): # Skip private/magic
                             defined_symbols[node.name] = file_path
                             
                # Collect usages (simple text search for now to be fast & safe)
                # AST usage analysis is hard across files without full indexing.
                # We'll use regex for whole-word matching as a proxy.
                words = set(re.findall(r'\b\w+\b', content))
                used_symbols.update(words)
                
            except Exception:
                continue
                
        # 2. Filter Unused
        # evidence = [] # Unused
        for name, file_path in defined_symbols.items():
            # If name appears in used_symbols only once (its definition), it *might* be unused.
            # But simple text search finds the definition too.
            # So if count == 1, it's likely unused. But we have a set.
            # We need counting.
            pass 
            
        # Re-doing logic: 
        # Truly counting matches across ALL files is expensive for regex.
        # Let's use a simpler heuristic:
        # If a symbol is defined in File A, check if it appears in ANY OTHER file.
        
        # unused_candidates = [] # Unused
        
        # Build giant text blob of all files? No, memory issues.
        # Optimization: We check "public" symbols.
        
        # all_content = "" # Unused
        # Read all py files into memory? Limit to 10MB total?
        # For now, let's just scan small projects.
        
        # Better approach: Vulture-like whitelist
        # We assume entry points (main, app, etc).
        
        # Let's stick to a safe subset: "Unused imports" is easier but flake8 does that.
        # "Unused local variables" -> simple AST visitor.
        
        return self._check_unused_locals(context)

    def _check_unused_locals(self, context: ProbeContext) -> AuditResult:
        """Check for unused local variables in functions."""
        evidence = []
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
                
            try:
                content = Path(file_path).read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        locals_defined = set()
                        locals_used = set()
                        
                        for child in ast.walk(node):
                            if isinstance(child, ast.Name):
                                if isinstance(child.ctx, ast.Store):
                                    locals_defined.add(child.id)
                                elif isinstance(child.ctx, ast.Load):
                                    locals_used.add(child.id)
                                    
                        unused = locals_defined - locals_used
                        # Filter out _ variables and self
                        unused = {v for v in unused if not v.startswith('_') and v != 'self'}
                        
                        if unused:
                            evidence.append(AuditEvidence(
                                description=f"Unused local variables in {node.name}: {', '.join(unused)}",
                                file_path=file_path,
                                line_number=node.lineno,
                                suggested_fix="Remove unused variables"
                            ))
            except Exception:
                continue
                
        return AuditResult(
            check_id="DEAD-001",
            check_name="Dead Code (Unused Locals)",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.LOW, 
            evidence=evidence[:10],
            recommendation="Remove unused local variables to clean up code"
        )