"""
IntelligenceStore - Persistence layer for forensic findings.

Extends SimplifiedDatabase with forensic-specific operations.
Single source of truth for all strategic intelligence.
"""

from typing import List, Optional
from datetime import datetime, timezone
import json

from side.storage.simple_db import SimplifiedDatabase
from side.intel.forensic_engine import Finding
from side.forensic_audit.core import AuditSummary, AuditStatus


class IntelligenceStore:
    """
    Manages persistence and querying of forensic findings.
    """

    def __init__(self, db: SimplifiedDatabase):
        self.db = db
        self._ensure_schema()

    def _ensure_schema(self):
        """Create findings table if it doesn't exist."""
        with self.db._connection() as conn:
            # Note: project_id is a hash-based identifier for data isolation,
            # not a foreign key reference to another table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS findings (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    file TEXT NOT NULL,
                    line INTEGER,
                    message TEXT NOT NULL,
                    action TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    resolved_at TEXT
                )
            """)
            
            # Index for common queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_findings_project_severity 
                ON findings(project_id, severity, resolved_at)
            """)
            
            conn.commit()

    def store_findings(self, project_id: str, findings: List[Finding]) -> int:
        """
        Store findings for a project.
        Returns number of new findings stored.
        """
        if not findings:
            return 0
            
        stored_count = 0
        now_iso = datetime.now(timezone.utc).isoformat()
        
        with self.db._connection() as conn:
            # 1. Fetch all unresolved finding IDs for this project to check existence in bulk
            rows = conn.execute(
                "SELECT id FROM findings WHERE project_id = ? AND resolved_at IS NULL",
                (project_id,)
            ).fetchall()
            existing_ids = {row['id'] for row in rows}
            
            # 2. Filter out findings that already exist and are unresolved
            new_findings_data = []
            for finding in findings:
                finding_id = self._generate_finding_id(project_id, finding)
                if finding_id not in existing_ids:
                    new_findings_data.append((
                        finding_id,
                        project_id,
                        finding.type,
                        finding.severity,
                        finding.file,
                        finding.line,
                        finding.message,
                        finding.action,
                        json.dumps(finding.metadata),
                        now_iso
                    ))
            
            # 3. Batch insert new findings
            if new_findings_data:
                conn.executemany("""
                    INSERT OR REPLACE INTO findings 
                    (id, project_id, type, severity, file, line, message, action, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, new_findings_data)
                stored_count = len(new_findings_data)
            
            conn.commit()
        
        return stored_count

    def store_audit_summary(self, project_id: str, summary: AuditSummary) -> int:
        """
        Store results from ForensicAuditRunner summary.
        Maps AuditResult -> Finding.
        """
        from side.utils.soul import StrategicSoul
        findings = []
        for dim_results in summary.results_by_dimension.values():
            for res in dim_results:
                if res.status in [AuditStatus.FAIL, AuditStatus.WARN]:
                    why, action, friendly, fusion = StrategicSoul.format_combined(res)
                    # Map AuditResult -> Finding
                    finding = Finding(
                        type=res.check_name,
                        severity=res.severity.value.upper(), # Normalize to UPPERCASE
                        file=res.evidence[0].file_path if res.evidence and res.evidence[0].file_path else "Project",
                        line=res.evidence[0].line_number if res.evidence and res.evidence[0].line_number else 0,
                        message=fusion,
                        action=action, # Keep raw action for other integrations
                        metadata={
                            'check_id': res.check_id,
                            'dimension': res.dimension,
                            'status': res.status.value,
                            'fix_risk': res.fix_risk.value,
                            'friendly': friendly,
                            'why_clean': why,
                            'evidence': [e.description for e in res.evidence] if res.evidence else []
                        }
                    )
                    findings.append(finding)
        
        # 1. Store NEW findings
        count = self.store_findings(project_id, findings)
        
        # 2. PURGE Logic: Resolve findings that are NOT in the current summary
        # If a finding was in the DB but is not in the clean 'findings' list, it means:
        # a) It was fixed
        # b) It was filtered out by SmartExclusion
        # In either case, it should be marked resolved/removed from active view.
        
        current_finding_ids = {self._generate_finding_id(project_id, f) for f in findings}
        
        with self.db._connection() as conn:
            # Get all currently active findings in DB
            rows = conn.execute(
                "SELECT id FROM findings WHERE project_id = ? AND resolved_at IS NULL",
                (project_id,)
            ).fetchall()
            db_active_ids = {row['id'] for row in rows}
            
            # Identify IDs to purge (In DB but not in Current Run)
            ids_to_resolve = db_active_ids - current_finding_ids
            
            if ids_to_resolve:
                now_iso = datetime.now(timezone.utc).isoformat()
                # Bulk resolve
                # SQLite doesn't support list parameters well for IN clause with many items, loop is safer for small sets
                # or construct dynamic query. Let's do dynamic for efficiency.
                id_list = list(ids_to_resolve)
                placeholders = ','.join('?' * len(id_list))
                conn.execute(
                    f"UPDATE findings SET resolved_at = ? WHERE id IN ({placeholders})",
                    [now_iso] + id_list
                )
                conn.commit()
                print(f"DEBUG: Purged {len(id_list)} stale findings.")
        
        return count

    def get_active_findings(self, project_id: str, severity: Optional[str] = None) -> List[dict]:
        """Get all unresolved findings for a project."""
        with self.db._connection() as conn:
            query = """
                SELECT id, type, severity, file, line, message, action, metadata, created_at
                FROM findings
                WHERE project_id = ? AND resolved_at IS NULL
            """
            params = [project_id]
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            query += " ORDER BY CASE severity WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END, created_at DESC"
            
            rows = conn.execute(query, params).fetchall()
            
            return [
                {
                    'id': row['id'],
                    'type': row['type'],
                    'severity': row['severity'],
                    'file': row['file'],
                    'line': row['line'],
                    'message': row['message'],
                    'action': row['action'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                    'created_at': row['created_at']
                }
                for row in rows
            ]

    def resolve_finding(self, finding_id: str) -> bool:
        """Mark a finding as resolved."""
        with self.db._connection() as conn:
            cursor = conn.execute(
                "UPDATE findings SET resolved_at = ? WHERE id = ? AND resolved_at IS NULL",
                (datetime.now(timezone.utc).isoformat(), finding_id)
            )
            conn.commit()
            conn.commit()
            return cursor.rowcount > 0

    def promote_finding_to_plan(self, project_id: str, finding_id: str, plan_type: str = "task") -> str | None:
        """
        [Strategic Learning] Promote a Finding into a Plan.
        
        This closes the loop: Forensics -> Strategy.
        returns: The new Plan ID.
        """
        import uuid
        
        with self.db._connection() as conn:
            # 1. Get Finding
            row = conn.execute(
                "SELECT * FROM findings WHERE id = ? AND project_id = ?", 
                (finding_id, project_id)
            ).fetchone()
            
            if not row:
                return None
                
            # 2. Create Plan
            new_plan_id = f"plan_{uuid.uuid4().hex[:8]}"
            title = f"Fix: {row['type']}"
            description = f"Originated from Forensic Finding {finding_id}.\n\nMessage: {row['message']}\nFile: {row['file']}:{row['line']}\n\nAction: {row['action']}"
            
            conn.execute(
                """
                INSERT INTO plans (id, project_id, title, description, type, status, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_plan_id, 
                    project_id, 
                    title, 
                    description, 
                    plan_type, 
                    "active", 
                    10 if row['severity'] == 'CRITICAL' else 5
                )
            )
            
            # 3. Link Finding to Plan (Update Metadata)
            # We append the plan_id to the finding's metadata so we know it's being addressed
            try:
                meta = json.loads(row['metadata']) if row['metadata'] else {}
                meta['linked_plan_id'] = new_plan_id
                conn.execute(
                    "UPDATE findings SET metadata = ? WHERE id = ?",
                    (json.dumps(meta), finding_id)
                )
            except Exception:
                pass # Non-critical
                
            conn.commit()
            return new_plan_id
        """
        Calculate Strategic Health Score (0-100 scale).
        
        Grade System:
        - 90-100: A (Production-ready, enterprise-grade)
        - 80-89:  B (Clean, ready to ship)
        - 70-79:  C (Healthy, some tech debt)
        - 60-69:  D (Significant issues, needs attention)
        - 0-59:   F (Critical, stop and fix)
        
        Uses diminishing returns so many small issues don't
        destroy the score, but critical issues still hurt.
        """
        import math
        
        with self.db._connection() as conn:
            # Count active findings by severity
            counts = conn.execute("""
                SELECT severity, COUNT(*) as count
                FROM findings
                WHERE project_id = ? AND resolved_at IS NULL
                GROUP BY severity
            """, (project_id,)).fetchall()
            
            # Build severity map
            severity_counts = {row['severity']: row['count'] for row in counts}
            critical = severity_counts.get('CRITICAL', 0)
            high = severity_counts.get('HIGH', 0)
            medium = severity_counts.get('MEDIUM', 0)
            low = severity_counts.get('LOW', 0)
            
            # Start at 100 (perfect score)
            score = 100.0
            
            # Penalties with DIMINISHING RETURNS
            # Formula: max_penalty * (1 - e^(-count/decay_rate))
            # Each severity has a max penalty cap to prevent over-penalization
            
            # CRITICAL: Max -35 penalty, very steep (decay rate 1.5)
            if critical > 0:
                score -= 35 * (1 - math.exp(-critical / 1.5))
            
            # HIGH: Max -25 penalty, steep (decay rate 3)
            if high > 0:
                score -= 25 * (1 - math.exp(-high / 3))
            
            # MEDIUM: Max -15 penalty, moderate (decay rate 10)
            if medium > 0:
                score -= 15 * (1 - math.exp(-medium / 10))
            
            # LOW: Max -5 penalty, gentle (decay rate 15)
            if low > 0:
                score -= 5 * (1 - math.exp(-low / 15))
            
            # BONUS: Add up to +10 for clean categories
            if critical == 0:
                score = min(100, score + 5)  # No criticals bonus
            if critical == 0 and high == 0:
                score = min(100, score + 5)  # Zero critical+high bonus
            
            return max(0, min(100, int(round(score))))

    def get_finding_stats(self, project_id: str) -> dict:
        """Get statistics about findings."""
        with self.db._connection() as conn:
            stats = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN severity = 'CRITICAL' THEN 1 ELSE 0 END) as critical,
                    SUM(CASE WHEN severity = 'HIGH' THEN 1 ELSE 0 END) as high,
                    SUM(CASE WHEN severity = 'MEDIUM' THEN 1 ELSE 0 END) as medium,
                    SUM(CASE WHEN severity = 'LOW' THEN 1 ELSE 0 END) as low
                FROM findings
                WHERE project_id = ? AND resolved_at IS NULL
            """, (project_id,)).fetchone()
            
            return {
                'total': stats['total'] or 0,
                'critical': stats['critical'] or 0,
                'high': stats['high'] or 0,
                'medium': stats['medium'] or 0,
                'low': stats['low'] or 0
            }

    def _generate_finding_id(self, project_id: str, finding: Finding) -> str:
        """Generate deterministic ID for a finding."""
        import hashlib
        
        # Use check_id from metadata if available, otherwise use finding.type
        # check_id is the most stable identifier across runs
        check_id = finding.metadata.get('check_id', finding.type) if finding.metadata else finding.type
        
        # Create stable hash from key structural attributes
        # We exclude 'message' to prevent duplicate findings when AI descriptions change slightly
        content = f"{project_id}:{check_id}:{finding.file}:{finding.line}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
