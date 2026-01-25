"""
Database Probe - Comprehensive database audit.

Forensic-level database checks covering:
- Schema design
- Query patterns
- Index usage
- Data integrity
- Backup strategy
"""

import re
from pathlib import Path
from typing import List
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier


class DatabaseProbe:
    """Forensic-level database audit probe."""
    
    id = "forensic.database"
    name = "Database Audit"
    tier = Tier.FAST
    dimension = "Database"
    
    async def run(self, context: ProbeContext) -> List[AuditResult]:
        """Run all database checks."""
        return [
            self._check_primary_keys(context),
            self._check_indexes(context),
            self._check_timestamps(context),
            self._check_constraints(context),
            self._check_rls(context),
            self._check_migrations(context),
            self._check_backup_strategy(context),
        ]
    
    def _check_primary_keys(self, context: ProbeContext) -> AuditResult:
        """Check for primary key definitions."""
        tables_found = 0
        tables_with_pk = 0
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                # Check for CREATE TABLE
                tables = re.findall(r'CREATE\s+TABLE\s+(\w+)', content, re.IGNORECASE)
                tables_found += len(tables)
                
                # Check for PRIMARY KEY
                pks = re.findall(r'PRIMARY\s+KEY', content, re.IGNORECASE)
                tables_with_pk += len(pks)
            except Exception:
                continue
        
        if tables_found == 0:
            return AuditResult(
                check_id="DB-001",
                check_name="Primary Keys Defined",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.HIGH,
                notes="No table definitions found"
            )
        
        return AuditResult(
            check_id="DB-001",
            check_name="Primary Keys Defined",
            dimension=self.dimension,
            status=AuditStatus.PASS if tables_with_pk >= tables_found else AuditStatus.WARN,
            severity=Severity.HIGH,
            notes=f"Found {tables_with_pk}/{tables_found} tables with primary keys",
            recommendation="All tables should have a primary key"
        )
    
    def _check_indexes(self, context: ProbeContext) -> AuditResult:
        """Check for index definitions."""
        has_indexes = False
        index_count = 0
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                indexes = re.findall(r'CREATE\s+INDEX', content, re.IGNORECASE)
                index_count += len(indexes)
                if indexes:
                    has_indexes = True
            except Exception:
                continue
        
        return AuditResult(
            check_id="DB-002",
            check_name="Database Indexes",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_indexes else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            notes=f"Found {index_count} index definitions",
            recommendation="Add indexes on frequently queried columns"
        )
    
    def _check_timestamps(self, context: ProbeContext) -> AuditResult:
        """Check for timestamp columns."""
        tables_found = 0
        tables_with_timestamps = 0
        
        timestamp_patterns = ['created_at', 'updated_at', 'timestamp', 'created', 'modified']
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                tables = re.findall(r'CREATE\s+TABLE', content, re.IGNORECASE)
                tables_found += len(tables)
                
                for tp in timestamp_patterns:
                    if tp in content.lower():
                        tables_with_timestamps += 1
                        break
            except Exception:
                continue
        
        return AuditResult(
            check_id="DB-003",
            check_name="Timestamp Columns",
            dimension=self.dimension,
            status=AuditStatus.PASS if tables_with_timestamps > 0 else AuditStatus.WARN,
            severity=Severity.LOW,
            notes=f"Found timestamp columns in {tables_with_timestamps} files",
            recommendation="Add created_at and updated_at to all tables"
        )
    
    def _check_rls(self, context: ProbeContext) -> AuditResult:
        """Check for Row Level Security (RLS) usage."""
        tables_found = 0
        rls_enabled_count = 0
        
        for file_path in context.files:
            if not any(file_path.endswith(ext) for ext in ['.py', '.sql']):
                continue
            
            try:
                content = Path(file_path).read_text()
                # Simple check for table creation
                tables = re.findall(r'CREATE\s+TABLE\s+(\w+)', content, re.IGNORECASE)
                tables_found += len(tables)
                
                # Check for ENABLE ROW LEVEL SECURITY
                rls = re.findall(r'ALTER\s+TABLE\s+\w+\s+ENABLE\s+ROW\s+LEVEL\s+SECURITY', content, re.IGNORECASE)
                rls_enabled_count += len(rls)
            except Exception:
                continue
        
        if tables_found == 0:
            return AuditResult(
                check_id="DB-007",
                check_name="Row Level Security",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.HIGH,
                notes="No table definitions found to check RLS"
            )
            
        return AuditResult(
            check_id="DB-007",
            check_name="Row Level Security",
            dimension=self.dimension,
            status=AuditStatus.PASS if rls_enabled_count >= tables_found else AuditStatus.WARN,
            severity=Severity.HIGH,
            notes=f"Found {rls_enabled_count}/{tables_found} tables with RLS enabled",
            recommendation="Enable RLS on all tables containing sensitive user data"
        )

    def _check_constraints(self, context: ProbeContext) -> AuditResult:
        """Check for constraint definitions."""
        constraints_found = 0
        
        constraint_patterns = ['FOREIGN KEY', 'UNIQUE', 'CHECK', 'NOT NULL']
        
        for file_path in context.files:
            if not file_path.endswith('.py'):
                continue
            
            try:
                content = Path(file_path).read_text()
                for cp in constraint_patterns:
                    constraints_found += len(re.findall(cp, content, re.IGNORECASE))
            except Exception:
                continue
        
        return AuditResult(
            check_id="DB-004",
            check_name="Database Constraints",
            dimension=self.dimension,
            status=AuditStatus.PASS if constraints_found > 0 else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            notes=f"Found {constraints_found} constraint definitions",
            recommendation="Use constraints to enforce data integrity"
        )
    
    def _check_migrations(self, context: ProbeContext) -> AuditResult:
        """Check for migration strategy."""
        has_migrations = False
        has_version = False
        
        for file_path in context.files:
            if 'migration' in file_path.lower() or 'alembic' in file_path.lower():
                has_migrations = True
            
            try:
                content = Path(file_path).read_text()
                if 'schema_version' in content.lower() or '_run_migrations' in content:
                    has_version = True
            except Exception:
                continue
        
        return AuditResult(
            check_id="DB-005",
            check_name="Migration Strategy",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_migrations or has_version else AuditStatus.WARN,
            severity=Severity.MEDIUM,
            notes="Migration strategy found" if (has_migrations or has_version) else "No migration strategy detected",
            recommendation="Use Alembic or manual migrations with version tracking"
        )
    
    def _check_backup_strategy(self, context: ProbeContext) -> AuditResult:
        """Check for backup strategy."""
        has_backup = False
        
        backup_patterns = ['backup', 'dump', 'export', '.bak']
        
        for file_path in context.files:
            try:
                content = Path(file_path).read_text()
                if any(bp in content.lower() for bp in backup_patterns):
                    has_backup = True
                    break
            except Exception:
                continue
        
        return AuditResult(
            check_id="DB-006",
            check_name="Backup Strategy",
            dimension=self.dimension,
            status=AuditStatus.PASS if has_backup else AuditStatus.WARN,
            severity=Severity.HIGH,
            notes="Backup patterns found" if has_backup else "No backup strategy detected",
            recommendation="Implement automated backups with retention policy"
        )
