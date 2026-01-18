"""
IntelligenceStore - Persistence layer for forensic findings.

Extends SimplifiedDatabase with forensic-specific operations.
Single source of truth for all strategic intelligence.
"""

from typing import List, Optional
from datetime import datetime, timezone
import json

from cso_ai.storage.simple_db import SimplifiedDatabase
from cso_ai.intel.forensic_engine import Finding


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
                    resolved_at TEXT,
                    FOREIGN KEY (project_id) REFERENCES profiles(id)
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
        Calculate Strategic IQ based on findings and project health.
        
        Formula:
        - Base: 100
        - Critical findings: -20 each
        - High findings: -10 each
        - Medium findings: -5 each
        - Low findings: -2 each
        - Minimum: 0, Maximum: 160
        """
        with self.db._connection() as conn:
            # Count active findings by severity
            counts = conn.execute("""
                SELECT severity, COUNT(*) as count
                FROM findings
                WHERE project_id = ? AND resolved_at IS NULL
                GROUP BY severity
            """, (project_id,)).fetchall()
            
            score = 100
            
            for row in counts:
                severity = row['severity']
                count = row['count']
                
                if severity == 'CRITICAL':
                    score -= count * 20
                elif severity == 'HIGH':
                    score -= count * 10
                elif severity == 'MEDIUM':
                    score -= count * 5
                elif severity == 'LOW':
                    score -= count * 2
            
            # Bonus for zero critical/high findings
            critical_high_count = sum(
                row['count'] for row in counts 
                if row['severity'] in ('CRITICAL', 'HIGH')
            )
            
            if critical_high_count == 0:
                score += 20
            
            return max(0, min(160, score))

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
