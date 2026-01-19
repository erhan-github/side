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
        stored_count = 0
        
        with self.db._connection() as conn:
            for finding in findings:
                # Generate deterministic ID based on content
                finding_id = self._generate_finding_id(project_id, finding)
                
                # Check if finding already exists and is unresolved
                existing = conn.execute(
                    "SELECT id FROM findings WHERE id = ? AND resolved_at IS NULL",
                    (finding_id,)
                ).fetchone()
                
                if not existing:
                    conn.execute("""
                        INSERT OR REPLACE INTO findings 
                        (id, project_id, type, severity, file, line, message, action, metadata, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        finding_id,
                        project_id,
                        finding.type,
                        finding.severity,
                        finding.file,
                        finding.line,
                        finding.message,
                        finding.action,
                        json.dumps(finding.metadata),
                        datetime.now(timezone.utc).isoformat()
                    ))
                    stored_count += 1
            
            conn.commit()
        
        return stored_count

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
            return cursor.rowcount > 0

    def get_strategic_iq(self, project_id: str) -> int:
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
        
        # Create hash from key attributes
        content = f"{project_id}:{finding.type}:{finding.file}:{finding.line}:{finding.message}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
