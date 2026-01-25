"""
Strategy Probe - Context-aware strategic alignment audit.

Checks if current work aligns with active tasks and roadmap.
"""

import subprocess
from typing import List, Set
from pathlib import Path
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier

class StrategyProbe:
    """Forensic-level strategic alignment probe."""
    
    id = "forensic.strategy"
    name = "Strategic Alignment"
    tier = Tier.FAST
    dimension = "Strategy"
    
    async def run(self, context: ProbeContext) -> List[AuditResult]:
        return [
            self._check_stray_code(context),
            self._check_priority_misalignment(context),
            self._check_recurring_failures(context),
            self._check_missing_strategy_docs(context),
        ]

    def _check_missing_strategy_docs(self, context: ProbeContext) -> AuditResult:
        """
        Check for existence of key strategic documents.
        """
        root = Path(context.project_root)
        missing_docs = []
        
        # Core Strategic Documents
        required_docs = {
            "VISION.md": "Defines the long-term North Star.",
            "ROADMAP.md": "Defines the execution path.",
            "ARCHITECTURE.md": "Defines the system design boundaries."
        }
        
        evidence = []
        
        for doc, purpose in required_docs.items():
            # Check root and docs/ folder
            if not (root / doc).exists() and not (root / "docs" / doc).exists():
                evidence.append(AuditEvidence(
                    description=f"Missing Strategic Document: {doc}",
                    file_path=doc,
                    context=purpose,
                    suggested_fix=f"Create {doc} to define project intent."
                ))
        
        return AuditResult(
            check_id="STRAT-004",
            check_name="Missing Strategic Context",
            dimension=self.dimension,
            status=AuditStatus.WARN if evidence else AuditStatus.PASS,
            severity=Severity.HIGH,
            evidence=evidence,
            recommendation="Create missing strategic documents to guide the AI."
        )

    def _get_changed_files(self, project_root: str) -> Set[str]:
        """Get list of changed files (staged + unstaged) using git."""
        changed_files = set()
        try:
            # Staged files
            cmd_staged = ['git', 'diff', '--name-only', '--cached']
            result_staged = subprocess.run(
                cmd_staged, cwd=project_root, capture_output=True, text=True
            )
            if result_staged.returncode == 0:
                changed_files.update(result_staged.stdout.splitlines())
            
            # Unstaged files
            cmd_unstaged = ['git', 'diff', '--name-only']
            result_unstaged = subprocess.run(
                cmd_unstaged, cwd=project_root, capture_output=True, text=True
            )
            if result_unstaged.returncode == 0:
                changed_files.update(result_unstaged.stdout.splitlines())
                
             # Untracked files (new files)
            cmd_untracked = ['git', 'ls-files', '--others', '--exclude-standard']
            result_untracked = subprocess.run(
                cmd_untracked, cwd=project_root, capture_output=True, text=True
            )
            if result_untracked.returncode == 0:
                changed_files.update(result_untracked.stdout.splitlines())
                
        except Exception as e:
            # If git fails, we can't do this check properly
            pass
            
        return {f for f in changed_files if f.strip()}

    def _check_stray_code(self, context: ProbeContext) -> AuditResult:
        """
        Check if modified files align with active tasks.
        (Stray Code / Scope Creep Detection)
        """
        active_tasks = context.strategic_context.get('active_tasks', [])
        
        # If no active tasks detected, we can't judge alignment
        if not active_tasks:
            return AuditResult(
                check_id="STRAT-001",
                check_name="Stray Code Detection",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.MEDIUM,
                notes="No active tasks found in task.md"
            )
            
        changed_files = self._get_changed_files(context.project_root)
        
        if not changed_files:
             return AuditResult(
                check_id="STRAT-001",
                check_name="Stray Code Detection",
                dimension=self.dimension,
                status=AuditStatus.PASS,
                severity=Severity.LOW,
                notes="No file changes detected"
            )

        evidence = []
        
        # Simple Keyword Heuristic
        # For each changed file, does it match any keyword in any active task?
        
        # Build keywords from active tasks
        # e.g., "Fix Backend Auth" -> {'backend', 'auth', 'fix'}
        task_keywords = set()
        for task in active_tasks:
            words = task.lower().split()
            # Filter stop words roughly
            useful_words = [w for w in words if len(w) > 3 and w not in ['update', 'implement', 'create', 'verify']]
            task_keywords.update(useful_words)
            
        # Check files
        for file_path in changed_files:
            file_name_parts = Path(file_path).stem.lower().split('_')
            path_parts = str(Path(file_path)).lower().split('/')
            
            # Combine all parts of the file path for matching
            file_tokens = set(file_name_parts + path_parts)
            
            # Check for intersection
            match = False
            for token in file_tokens:
                # substring match
                if any(k in token for k in task_keywords):
                    match = True
                    break
            
            if not match:
                evidence.append(AuditEvidence(
                    description="File modification may not align with active tasks",
                    file_path=file_path,
                    context=f"Active Tasks: {'; '.join(active_tasks[:2])}...",
                    suggested_fix="Verify if this change is in scope"
                ))

        return AuditResult(
            check_id="STRAT-001",
            check_name="Stray Code Detection",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            evidence=evidence[:5],
            notes=f"Found {len(evidence)} potentially stray files" if evidence else "All changes align with active tasks",
            recommendation="Keep changes focused on the active task list"
        )

    def _check_priority_misalignment(self, context: ProbeContext) -> AuditResult:
        """
        Check if we are working on low-value areas while critical tasks exist.
        """
        active_tasks = context.strategic_context.get('active_tasks', [])
        changed_files = self._get_changed_files(context.project_root)
        
        if not active_tasks or not changed_files:
            return AuditResult(
                check_id="STRAT-002",
                check_name="Priority Alignment",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.LOW,
                notes="Insufficient context"
            )
            
        evidence = []
        
        # Heuristic 1: If "docs" or "test" modified but Active Task is "CRITICAL" or "Fix"
        has_critical_task = any('critical' in t.lower() or 'fix' in t.lower() or 'bug' in t.lower() for t in active_tasks)
        
        if has_critical_task:
            for f in changed_files:
                p = Path(f)
                # If editing docs/readme/renovate.json while critical bug exists
                if 'doc' in str(p).lower() or p.name.lower() == 'readme.md' or '.github' in str(p).lower():
                     evidence.append(AuditEvidence(
                        description="Editing docs/config while Critical/Bug task is active",
                        file_path=f,
                         suggested_fix="Focus on the critical fix first"
                    ))

        return AuditResult(
            check_id="STRAT-002",
            check_name="Priority Alignment",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.INFO,
            severity=Severity.LOW,
            evidence=evidence[:5],
            recommendation="Prioritize critical fixes over documentation/config"
        )

    def _check_recurring_failures(self, context: ProbeContext) -> AuditResult:
        """
        Check for files that repeatedly fail audits (using Monolith history).
        """
        if not context.intelligence_store:
            return AuditResult(
                check_id="STRAT-003",
                check_name="Recurring Failures",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.MEDIUM,
                notes="Monolith not connected"
            )
            
        evidence = []
        try:
            # We need to access the DB directly or via store to count recurring issues
            # Using the `findings` table where resolved_at IS NULL
            # But specific "Recurring" means fetching history.
            # Simplified approach: Check active finding count per file.
            
            project_id = context.intelligence_store.db.get_project_id(context.project_root)
            active_findings = context.intelligence_store.get_active_findings(project_id)
            
            from collections import Counter
            file_counts = Counter(f['file'] for f in active_findings)
            
            for file_path, count in file_counts.items():
                if count >= 3:
                     evidence.append(AuditEvidence(
                        description=f"File has {count} active findings (High Technical Debt)",
                        file_path=file_path,
                        suggested_fix="Refactor file to address accumulated debt temps"
                    ))
                    
        except Exception:
            pass

        return AuditResult(
            check_id="STRAT-003",
            check_name="Recurring Failure Detection",
            dimension=self.dimension,
            status=AuditStatus.PASS if not evidence else AuditStatus.WARN,
            severity=Severity.HIGH,
            evidence=evidence[:5],
            recommendation="Refactor files with multiple recurring issues"
        )
