"""
Side Simplified Database - Fast, focused storage with auto-cleanup.

Simplified from 5 tables to 4 tables5: 1. profile - Lightweight auto-detected profiles
2. articles - Articles with embedded score cache
3. work_context - What user is working on (7-day retention)
4. query_cache - Pre-computed results (1-hour retention)

Philosophy: Keep it simple, keep it fast, auto-cleanup old data.
"""

import hashlib
import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Generator


from side.utils.helpers import safe_get

# Module-level logger for early initialization code
logger = logging.getLogger(__name__)


class InsufficientTokensError(Exception):
    """Raised when the user has run out of Strategic Units (SU)."""
    pass



class SimplifiedDatabase:
    """
    Privacy-first SQLite storage for Side.
    
    PRIVACY PRINCIPLES:
    - Local-only: All data in ~/.side/local.db
    - Project isolation: Each project has its own namespace
    - Zero telemetry: Nothing leaves the machine
    - User control: Export/purge anytime
    
    Design goals:
    - Forensic-level schema (6 core tables)
    - Project-scoped data isolation
    - Fast queries with proper indexes
    - Auto-cleanup for temporary data
    """

    def __init__(self, db_path: str | Path | None = None):
        """
        Initialize database.

        Args:
            db_path: Path to SQLite database. Defaults to ~/.side/local.db
        """
        if db_path is None:
            db_path = Path.home() / ".side" / "local.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._atomic_backup() # [Grand Strategy] Black Swan Protection
        self._init_schema()
        self._run_migrations()
        self._harden_permissions()

    def _atomic_backup(self) -> None:
        """[Forensic 4] Maintain a rotational .db.bak for disaster recovery."""
        bak_path = self.db_path.with_suffix(".db.bak")
        if self.db_path.exists():
            try:
                import shutil
                # Only backup if current DB is healthy
                if self.check_integrity():
                    shutil.copy2(self.db_path, bak_path)
                    logger.debug("Disaster Recovery: Atomic backup created.")
            except Exception as e:
                logger.warning(f"Disaster Recovery: Backup failed: {e}")

    def _harden_permissions(self) -> None:
        """[Audit 4] Ensure local.db is only readable by the user (mode 600)."""
        if self.db_path.exists():
            import os
            try:
                os.chmod(self.db_path, 0o600)
            except Exception:
                pass

    def check_integrity(self) -> bool:
        """[Audit 2] Run a forensic SQLite integrity check."""
        try:
            with self._connection() as conn:
                result = conn.execute("PRAGMA integrity_check;").fetchone()
                return result[0] == "ok"
        except Exception as e:
            logger.error(f"Integrity check failed: {e}")
            return False

    @staticmethod
    def get_project_id(project_path: str | Path | None = None) -> str:
        """
        Get project ID for data isolation.
        
        [Hyper-Ralph] Scenario 19 Fix: Persists project ID in a hidden file 
        to ensure stability even if the folder is renamed.
        """
        if project_path is None:
            project_path = Path.cwd()
        else:
            project_path = Path(project_path)
            
        project_path = project_path.resolve()
        id_file = project_path / ".side-id"
        
        # Check if ID already exists
        if id_file.exists():
            try:
                return id_file.read_text().strip()
            except Exception:
                pass
        
        # Generate new ID
        import hashlib
        path_hash = hashlib.sha256(str(project_path).encode()).hexdigest()[:16]
        
        # Persist it
        try:
            id_file.write_text(path_hash)
        except Exception:
            pass # Fallback to path-based ID if no write permissions
            
        return path_hash

    def _init_schema(self) -> None:
        """
        Initialize Forensic-level database schema.
        
        6 Core Tables:
        1. plans - Strategic roadmap (objectives, milestones, goals, tasks)
        2. decisions - Strategic choices with reasoning
        3. learnings - Insights and discoveries
        4. check_ins - Progress tracking
        5. profile - User identity and context
        6. context - Current work (auto-detected)
        
        Plus: articles, query_cache, meta (operational)
        """
        with self._connection() as conn:
            # ─────────────────────────────────────────────────────────────
            # META TABLE - Database versioning for migrations
            # ─────────────────────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            # Initialize version if not exists
            conn.execute("""
                INSERT OR IGNORE INTO meta (key, value) VALUES ('version', '1.0')
            """)
            # ─────────────────────────────────────────────────────────────
            # CORE TABLE 1: PLANS - Your Strategic Roadmap
            # Privacy: Isolated by project_id
            # ─────────────────────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS plans (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL DEFAULT 'default',
                    title TEXT NOT NULL,
                    description TEXT,
                    type TEXT NOT NULL DEFAULT 'goal',
                    status TEXT DEFAULT 'active',
                    parent_id TEXT,
                    due_date DATE,
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (parent_id) REFERENCES plans(id)
                )
            """)
            # Types: objective (5yr), milestone (1yr), goal (month), task (week)
            # Status: active, done, dropped, blocked
            
            # Migrate: add project_id if missing
            try:
                conn.execute("ALTER TABLE plans ADD COLUMN project_id TEXT DEFAULT 'default'")
            except Exception:
                pass
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_plans_project ON plans(project_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_plans_type ON plans(type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_plans_status ON plans(status, due_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_plans_parent ON plans(parent_id)")

            # ─────────────────────────────────────────────────────────────
            # CORE TABLE 2: DECISIONS - Strategic Choices
            # Privacy: Isolated by project_id
            # ─────────────────────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL DEFAULT 'default',
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    reasoning TEXT,
                    category TEXT,
                    plan_id TEXT,
                    confidence INTEGER DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plan_id) REFERENCES plans(id)
                )
            """)
            # Category: tech, business, product, team, funding
            
            try:
                conn.execute("ALTER TABLE decisions ADD COLUMN project_id TEXT DEFAULT 'default'")
            except Exception:
                pass
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_decisions_project ON decisions(project_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_decisions_category ON decisions(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_decisions_plan ON decisions(plan_id)")

            # ─────────────────────────────────────────────────────────────
            # CORE TABLE 3: LEARNINGS - Insights & Discoveries
            # Privacy: Isolated by project_id
            # ─────────────────────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learnings (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL DEFAULT 'default',
                    insight TEXT NOT NULL,
                    source TEXT,
                    impact TEXT DEFAULT 'medium',
                    plan_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plan_id) REFERENCES plans(id)
                )
            """)
            # Source: user_feedback, market_research, code_analysis, competitor
            # Impact: high, medium, low
            
            try:
                conn.execute("ALTER TABLE learnings ADD COLUMN project_id TEXT DEFAULT 'default'")
            except Exception:
                pass
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_learnings_project ON learnings(project_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_learnings_impact ON learnings(impact)")

            # ─────────────────────────────────────────────────────────────
            # CORE TABLE 4: CHECK_INS - Progress Tracking
            # Privacy: Isolated by project_id
            # ─────────────────────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS check_ins (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL DEFAULT 'default',
                    plan_id TEXT NOT NULL,
                    status TEXT,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plan_id) REFERENCES plans(id)
                )
            """)
            # Status: on_track, blocked, done, skipped
            
            try:
                conn.execute("ALTER TABLE check_ins ADD COLUMN project_id TEXT DEFAULT 'default'")
            except Exception:
                pass
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_check_ins_project ON check_ins(project_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_check_ins_plan ON check_ins(plan_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_check_ins_date ON check_ins(created_at DESC)")

            # ─────────────────────────────────────────────────────────────
            # CORE TABLE 5: PROFILE - User Identity
            # ─────────────────────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS profile (
                    id TEXT PRIMARY KEY DEFAULT 'main',
                    name TEXT,
                    company TEXT,
                    domain TEXT,
                    stage TEXT,
                    business_model TEXT,
                    target_raise TEXT,
                    tech_stack JSON,
                    tier TEXT DEFAULT 'free',
                    token_balance INTEGER DEFAULT 50,
                    tokens_monthly INTEGER DEFAULT 50,
                    tokens_used INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Migrate: add columns if missing
            try:
                conn.execute("ALTER TABLE profile ADD COLUMN tier TEXT DEFAULT 'hobby'")
            except: pass
            try:
                conn.execute("ALTER TABLE profile ADD COLUMN token_balance INTEGER DEFAULT 50")
            except: pass
            try:
                conn.execute("ALTER TABLE profile ADD COLUMN tokens_monthly INTEGER DEFAULT 50")
            except: pass
            try:
                conn.execute("ALTER TABLE profile ADD COLUMN tokens_used INTEGER DEFAULT 0")
            except: pass
            # Stage: idea, mvp, growth, scale
            # Domain: edtech, fintech, saas, etc.

            # ─────────────────────────────────────────────────────────────
            # CORE TABLE 6: CONTEXT - Current Work (Auto-Detected)
            # ─────────────────────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT NOT NULL,
                    focus_area TEXT,
                    recent_files JSON,
                    recent_commits JSON,
                    current_branch TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    confidence FLOAT DEFAULT 0.0
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_context_path ON context(project_path)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_context_expires ON context(expires_at)")
            
            # ─────────────────────────────────────────────────────────────
            # OPERATIONAL TABLE: WORK_CONTEXT - Active work tracking
            # ─────────────────────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS work_context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT NOT NULL,
                    focus_area TEXT,
                    recent_files JSON,
                    recent_commits JSON,
                    current_branch TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    confidence FLOAT DEFAULT 0.0
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_work_context_path ON work_context(project_path)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_work_context_expires ON work_context(expires_at)")

            # ─────────────────────────────────────────────────────────────
            # PRIVACY TABLE: CONSENTS - User Opt-Ins
            # Default: All OFF (safe by default)
            # ─────────────────────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS consents (
                    id TEXT PRIMARY KEY DEFAULT 'main',
                    proactive_prompts INTEGER DEFAULT 1,
                    cloud_sync INTEGER DEFAULT 0,
                    analytics INTEGER DEFAULT 0,
                    external_apis INTEGER DEFAULT 0,
                    git_monitoring INTEGER DEFAULT 1,
                    first_run_complete INTEGER DEFAULT 0,
                    gamification_enabled INTEGER DEFAULT 1,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Defaults:
            # - proactive_prompts: ON (core feature)
            # - cloud_sync: OFF (requires opt-in)
            # - analytics: OFF (requires opt-in)
            # - external_apis: OFF (requires opt-in for LLM calls)
            # - git_monitoring: ON (local only, safe)
            # - first_run_complete: OFF (show welcome on first use)
            # - gamification_enabled: ON (fun by default, opt-out available)
            
            # Migrate: add gamification_enabled if missing
            try:
                conn.execute("ALTER TABLE consents ADD COLUMN gamification_enabled INTEGER DEFAULT 1")
            except Exception:
                pass

            # ─────────────────────────────────────────────────────────────
            # OPERATIONAL TABLES (Keep existing for compatibility)
            # ─────────────────────────────────────────────────────────────
            
            # Articles table (news/content cache)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    source TEXT NOT NULL,
                    description TEXT,
                    author TEXT,
                    score INTEGER,
                    published_at TIMESTAMP,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags JSON,
                    scores JSON
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_fetched ON articles(fetched_at DESC)")

            # Query cache (operational)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS query_cache (
                    query_hash TEXT PRIMARY KEY,
                    query_type TEXT NOT NULL,
                    result JSON NOT NULL,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_query_cache_expires ON query_cache(expires_at)")

            # ─────────────────────────────────────────────────────────────
            # STRATEGIC INTELLIGENCE SIGNALS (Top 10 Curation)
            # ─────────────────────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS intelligence_signals (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE,
                    source TEXT NOT NULL,
                    domain TEXT,
                    score INTEGER,
                    keywords JSON,
                    summary TEXT,
                    published_at TIMESTAMP,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_signals_score ON intelligence_signals(score DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_signals_domain ON intelligence_signals(domain)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_signals_expires ON intelligence_signals(expires_at)")

            # ─────────────────────────────────────────────────────────────
            # OPERATIONAL TABLE 3: AUDITS - Forensic Audit History
            # ─────────────────────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    audit_type TEXT NOT NULL,
                    severity TEXT CHECK(severity IN ('INFO', 'WARNING', 'CRITICAL')),
                    finding TEXT NOT NULL,
                    recommendation TEXT,
                    is_fixed INTEGER DEFAULT 0,
                    run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audits_project ON audits(project_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audits_type ON audits(audit_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audits_run_at ON audits(run_at DESC)")

            # ─────────────────────────────────────────────────────────────
            # OPERATIONAL TABLE 4: ACTIVITIES - Transparency Log
            # ─────────────────────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    tool TEXT NOT NULL,
                    action TEXT NOT NULL,
                    cost_tokens INTEGER DEFAULT 0,
                    tier TEXT DEFAULT 'free',
                    payload JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_project ON activities(project_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_tool ON activities(tool)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_created ON activities(created_at DESC)")

            # ─────────────────────────────────────────────────────────────
            # GAMIFICATION LAYER (Serious Fun)
            # ─────────────────────────────────────────────────────────────
            
            # 1. User Stats (The "Character Sheet")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_stats (
                    project_id TEXT PRIMARY KEY,
                    total_xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    last_action_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 2. Achievements (The "Trophy Case")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    badge_id TEXT NOT NULL,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSON,
                    UNIQUE(project_id, badge_id)
                )
            """)
            # 3. XP Ledger (The "Score Log")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS xp_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT,
                    action_type TEXT,
                    xp_amount INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 4. Outcomes Ledger (Instrumentation)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS outcomes_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT,
                    outcome_type TEXT,
                    leverage_value REAL DEFAULT 1.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_xp_project ON xp_ledger(project_id)")

            # NOTE: Legacy 'profiles' table removed - use 'profile' table instead

            # NOTE: Legacy 'goals' table removed - use 'plans' table instead

            conn.commit()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Create a thread-safe SQLite connection with timeout and optimized pragmas.
        
        [Hyper-Ralph] Scenario 14 Fix: Added explicit handling for 
        'database or disk is full' errors.
        """
        try:
            conn = sqlite3.connect(
                self.db_path, 
                timeout=30.0,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row
            
            # Optimize for speed and resilience
            conn.execute("PRAGMA journal_mode=WAL") 
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA foreign_keys=ON")
            
            try:
                yield conn
                conn.commit()
            except sqlite3.OperationalError as e:
                if "database or disk is full" in str(e).lower():
                    logger.critical(f"FATAL: Database or disk is full at {self.db_path}. Intelligence persistence disabled.")
                conn.rollback()
                raise
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
        except sqlite3.OperationalError as e:
            if "database or disk is full" in str(e).lower():
                logger.critical(f"FATAL: Could not open database. Disk full at {self.db_path}.")
            raise

    # =========================================================================
    # Migrations & CTO Hardening
    # =========================================================================

    def _get_version(self) -> float:
        """Get current database version."""
        try:
            with self._connection() as conn:
                cursor = conn.execute("SELECT value FROM meta WHERE key = 'version'")
                row = cursor.fetchone()
                return float(row["value"]) if row else 1.0
        except sqlite3.OperationalError:
            # Table doesn't exist yet - return default version
            return 1.0

    def _run_migrations(self) -> None:
        """
        Run schema migrations.
        
        This is the CTO-level 'Operation: Resilience'.
        """
        version = self._get_version()
        logger = logging.getLogger("side.storage.simple_db")

        if version < 1.1:
            # Example: Add 'status' to decisions if we need it in future
            # with self._connection() as conn:
            #     try:
            #         conn.execute("ALTER TABLE decisions ADD COLUMN status TEXT DEFAULT 'final'")
            #         conn.execute("UPDATE meta SET value = '1.1' WHERE key = 'version'")
            #         logger.info("Migrated SimpleDB to v1.1")
            #     except Exception as e:
            #         logger.debug(f"Migration 1.1 already applied or failed: {e}")
            pass

        logger.info(f"SimpleDB schema version: {version}")
    # =========================================================================

    # =========================================================================
    # Profile Operations
    # =========================================================================

    # =========================================================================
    # Profile Operations (Consolidated)
    # =========================================================================

    def update_profile(self, project_id: str, profile_data: dict[str, Any]) -> None:
        """
        Update the Sovereign Identity Profile.
        
        Writes to the unified 'profile' table.
        AUTO-MIGRATION: logic handles storing tech details in 'tech_stack' JSON.
        """
        # Prepare tech_stack JSON from flat data if needed
        tech_stack = safe_get(profile_data, "tech_stack")
        if not tech_stack:
            tech_stack = {
                "languages": safe_get(profile_data, "languages", {}),
                "frameworks": safe_get(profile_data, "frameworks", []),
                "recent_commits": safe_get(profile_data, "recent_commits", 0),
                "recent_files": safe_get(profile_data, "recent_files", []),
                "focus_areas": safe_get(profile_data, "focus_areas", [])
            }

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO profile (
                    id, name, company, domain, stage, business_model, 
                    target_raise, tech_stack, tier, tokens_monthly, tokens_used, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    tech_stack = COALESCE(excluded.tech_stack, tech_stack),
                    tier = COALESCE(excluded.tier, tier),
                    tokens_monthly = COALESCE(excluded.tokens_monthly, tokens_monthly),
                    tokens_used = COALESCE(excluded.tokens_used, tokens_used),
                    updated_at = excluded.updated_at
                """,
                (
                    project_id,
                    profile_data.get("name"),
                    profile_data.get("company"),
                    profile_data.get("domain"),
                    profile_data.get("stage"),
                    profile_data.get("business_model"),
                    profile_data.get("target_raise"),
                    json.dumps(tech_stack) if tech_stack else None,
                    profile_data.get("tier"),
                    profile_data.get("tokens_monthly"),
                    profile_data.get("tokens_used"),
                    datetime.now(timezone.utc).isoformat()
                )
            )
            
            # Update 'project_docs' etc in legacy 'profiles' table for now if needed?
            # NO. The plan is to KILL legacy table usage.
            # But we might want to store project_docs somewhere? 
            # The 'profile' table doesn't have project_docs.
            # Let's add it dynamically to meta or context if missing, 
            # OR just assume we only need tech_stack for Monolith for now.
            # Actually AutoIntelligence reads/writes project_docs.
            # Let's verify schema. 
            pass

    def get_profile(self, project_id: str) -> dict[str, Any] | None:
        """
        Get the unified profile (with tech stack flattened for convenience).
        """
        with self._connection() as conn:
            # Try new table first
            row = conn.execute(
                "SELECT * FROM profile WHERE id = ?", (project_id,)
            ).fetchone()
            
            if row:
                # Unpack JSON
                tech_stack = json.loads(row["tech_stack"]) if row["tech_stack"] else {}
                
                # Construct clean object
                return {
                    "id": row["id"],
                    "name": row["name"],
                    "tier": row["tier"],
                    "tokens_monthly": row["tokens_monthly"],
                    "tokens_used": row["tokens_used"],
                    "token_balance": row["token_balance"],
                    # Flattened technicals for easy consumption
                    "languages": tech_stack.get("languages", {}),
                    "frameworks": tech_stack.get("frameworks", []),
                    "recent_commits": tech_stack.get("recent_commits", 0),
                    "focus_areas": tech_stack.get("focus_areas", []),
                    "tech_stack": tech_stack,
                    "updated_at": row["updated_at"]
                }
            
            # Fallback: Check legacy 'profiles' table using project_id as path (imperfect but useful for transition)
            # Actually, let's just return None to force re-analysis if new profile is missing.
            return None
    
    def get_token_balance(self, project_id: str) -> dict[str, Any]:
        """Get current SUs and Tier."""
        with self._connection() as conn:
            row = conn.execute(
                "SELECT token_balance, tier FROM profile WHERE id = ?", (project_id,)
            ).fetchone()
            if row:
                return {
                    "balance": row["token_balance"],
                    "tier": row["tier"]
                }
            return {"balance": 0, "tier": "free"}

    def update_token_balance(self, project_id: str, amount: int) -> int:
        """
        Update token balance atomically with strict constraints.
        
        Rule #2: Enforce everything server side (in the DB transaction).
        
        Args:
            project_id: Project ID
            amount: Amount to add (positive) or deduct (negative)
        
        Returns:
            New balance
            
        Raises:
            InsufficientTokensError: If balance would drop below zero
        """
        with self._connection() as conn:
            if amount < 0:
                # Deduction: Atomic check AND update
                cursor = conn.execute(
                    """
                    UPDATE profile 
                    SET token_balance = token_balance + ? 
                    WHERE id = ? AND token_balance >= ?
                    """,
                    (amount, project_id, abs(amount))
                )
                if cursor.rowcount == 0:
                    # Check if it was ID missing or funds missing
                    row = conn.execute("SELECT token_balance FROM profile WHERE id = ?", (project_id,)).fetchone()
                    if not row:
                        # Should initiate profile? For now, fail.
                        raise InsufficientTokensError("Profile not found.")
                    current = row["token_balance"]
                    raise InsufficientTokensError(f"Insufficient SUs. Have {current}, need {abs(amount)}.")
            else:
                # Addition: Always allowed
                conn.execute(
                    "UPDATE profile SET token_balance = token_balance + ? WHERE id = ?",
                    (amount, project_id)
                )
            
            # Return new balance
            row = conn.execute("SELECT token_balance FROM profile WHERE id = ?", (project_id,)).fetchone()
            return row["token_balance"] if row else 0

    def log_activity(self, project_id: str, tool: str, action: str, cost: int, tier: str = "free", payload: dict = None) -> None:
        """Log a system activity/cost."""
        try:
            with self._connection() as conn:
                conn.execute(
                    """
                    INSERT INTO activities (
                        project_id, tool, action, cost_tokens, tier, payload
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (project_id, tool, action, cost, tier, json.dumps(payload) if payload else None)
                )
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")

    # Legacy method deprecated - removed save_profile
    # =========================================================================
    # Article Operations (with score caching)
    # =========================================================================

    def save_article(self, article: Any) -> None:
        """Save or update an article."""
        with self._connection() as conn:
            # Get existing scores if article exists
            existing = conn.execute(
                "SELECT scores FROM articles WHERE id = ?",
                (article.id,),
            ).fetchone()

            existing_scores = {}
            if existing and existing["scores"]:
                existing_scores = json.loads(existing["scores"])

            # Embed domain in tags for persistence
            tags = article.tags.copy()
            if hasattr(article, "domain") and article.domain and f"domain:{article.domain}" not in tags:
                tags.append(f"domain:{article.domain}")

            conn.execute(
                """
                INSERT INTO articles (
                    id, title, url, source, description, author,
                    score, published_at, fetched_at, tags, scores
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    description = excluded.description,
                    fetched_at = excluded.fetched_at,
                    scores = excluded.scores,
                    tags = excluded.tags
                """,
                (
                    article.id,
                    article.title,
                    article.url,
                    getattr(article, "source", getattr(article, "source_name", "unknown")), # Handle alias
                    article.description,
                    article.author,
                    getattr(article, "score", 0), # IntelligenceItem doesn't have score (source score), it has relevance_score
                    article.published_at.isoformat() if article.published_at else None,
                    article.fetched_at.isoformat(),
                    json.dumps(tags),
                    json.dumps(existing_scores),
                ),
            )
            conn.commit()

    def get_cached_articles(self, max_age_hours: int = 1, limit: int = 100) -> list[Any]:
        """
        Get cached articles if fresh enough.

        Args:
            max_age_hours: Maximum age in hours (default 1 hour)
            limit: Maximum number of articles to return

        Returns:
            List of cached articles, or empty list if cache is stale
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM articles 
                WHERE fetched_at > ?
                ORDER BY fetched_at DESC
                LIMIT ?
                """,
                (cutoff.isoformat(), limit),
            ).fetchall()

            articles = []
            articles = []
            for row in rows:
                tags = json.loads(row["tags"]) if row["tags"] else []
                
                # Extract domain from tags
                domain = "tech" # Default
                for tag in tags:
                    if tag.startswith("domain:"):
                        domain = tag.split(":", 1)[1]
                        break
                
                # Create IntelligenceItem (aliased as Article)
                # Note: IntelligenceItem uses 'source_name' instead of 'source'
                # We need to adapt arguments based on inspection or just pass arguments that match base class
                # But Article is IntelligenceItem now.
                
                article = Article(
                    id=row["id"],
                    title=row["title"],
                    url=row["url"],
                    source=row["source"], 
                    domain=domain,             # Extracted domain
                    description=row["description"],
                    author=row["author"],
                    # score=row["score"], # IntelligenceItem doesn't have 'score' in base, it has relevance_score. 
                    # But we might have mixed usage. 
                    # If Article is IntelligenceItem, it has no 'score' field in dataclass!
                    # We should check if we need to subclass or if we can drop 'score' (source specifics).
                    # Actually IntelligenceItem base definition I wrote didn't have 'score'. 
                    # MarketAnalyzer legacy sources might assume it.
                    # I will ignore 'score' (HN points) for now or add it to meta.
                    published_at=datetime.fromisoformat(row["published_at"]) if row["published_at"] else None,
                    fetched_at=datetime.fromisoformat(row["fetched_at"]),
                    tags=tags,
                )
                # Manually set legacy score if needed to meta
                article.meta["source_score"] = row["score"]
                
                articles.append(article)

            return articles

    def save_article_score(
        self,
        article_id: str,
        profile_hash: str,
        score: float,
        reason: str,
    ) -> None:
        """
        Cache article score for a specific profile.

        Args:
            article_id: Article ID
            profile_hash: Hash of the profile (for cache key)
            score: Relevance score (0-100)
            reason: Reasoning for the score
        """
        with self._connection() as conn:
            # Get existing scores
            row = conn.execute(
                "SELECT scores FROM articles WHERE id = ?",
                (article_id,),
            ).fetchone()

            scores = {}
            if row and row["scores"]:
                scores = json.loads(row["scores"])

            # Add new score
            scores[profile_hash] = {
                "score": score,
                "reason": reason,
                "cached_at": datetime.now(timezone.utc).isoformat(),
            }

            # Update article
            conn.execute(
                "UPDATE articles SET scores = ? WHERE id = ?",
                (json.dumps(scores), article_id),
            )
            conn.commit()

    # =========================================================================
    # Activity & Transparency Log
    # =========================================================================

    def log_activity(
        self,
        project_id: str,
        tool: str,
        action: str,
        cost_tokens: int = 0,
        tier: str = 'free',
        payload: dict[str, Any] | None = None
    ) -> None:
        """
        Log an activity for transparency and debit the token wallet.
        
        [Unicorn Strategy] This is the core 'Log-Centric' transparency engine.
        """
        with self._connection() as conn:
            # 0. Check for sufficient tokens (The "Hard Stop")
            # We skip check for free actions (cost_tokens == 0)
            if cost_tokens > 0:
                row = conn.execute("SELECT token_balance FROM profile WHERE id = 'main'").fetchone()
                balance = row['token_balance'] if row else 0
                if balance < cost_tokens:
                    logger.warning(f"🚫 Hard Stop: Insufficient tokens ({balance} available, {cost_tokens} needed)")
                    raise InsufficientTokensError(f"Insufficient tokens. {balance} remaining.")

            # 1. Insert activity log
            conn.execute(
                """
                INSERT INTO activities (
                    project_id, tool, action, cost_tokens, tier, payload
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    tool,
                    action,
                    cost_tokens,
                    tier,
                    json.dumps(payload or {})
                )
            )
            
            # 2. Debit Token Wallet (Local-first)
            # We assume 'main' profile for local work context
            conn.execute(
                "UPDATE profile SET token_balance = token_balance - ? WHERE id = 'main'",
                (cost_tokens,)
            )
            
            conn.commit()


    def set_token_balance(self, balance: int) -> None:
        """Manually set the token balance (for testing and administrative overrides)."""
        with self._connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO profile (id, token_balance) VALUES ('main', ?)",
                (balance,)
            )
            conn.commit()

    def get_recent_activities(self, project_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Get recent activities for a project."""
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM activities 
                WHERE project_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
                """,
                (project_id, limit)
            ).fetchall()
            
            return [dict(row) for row in rows]

    def get_recent_audits(self, project_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent audit findings for a project."""
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM audits 
                WHERE project_id = ? 
                ORDER BY run_at DESC 
                LIMIT ?
                """,
                (project_id, limit)
            ).fetchall()
            return [dict(row) for row in rows]

    def get_audit_summary(self, project_id: str) -> dict[str, int]:
        """Get summary of audit finding severities."""
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT severity, count(*) as count 
                FROM audits 
                WHERE project_id = ? 
                GROUP BY severity
                """,
                (project_id,)
            ).fetchall()
            return {row['severity']: row['count'] for row in rows}

    def get_article_score(
        self,
        article_id: str,
        profile_hash: str,
    ) -> dict[str, Any] | None:
        """Get cached score for article + profile combo."""
        with self._connection() as conn:
            row = conn.execute(
                "SELECT scores FROM articles WHERE id = ?",
                (article_id,),
            ).fetchone()

            if not row or not row["scores"]:
                return None

            scores = json.loads(row["scores"])
            return scores.get(profile_hash)

    def get_article_count(self) -> int:
        """Get total article count."""
        with self._connection() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM articles").fetchone()
            return row["count"] if row else 0

    def get_profile_count(self) -> int:
        """Get total profile count."""
        with self._connection() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM profiles").fetchone()
            return row["count"] if row else 0

    # =========================================================================
    # Work Context Operations (7-day retention)
    # =========================================================================

    def save_work_context(
        self,
        project_path: str,
        focus_area: str,
        recent_files: list[str],
        recent_commits: list[dict[str, Any]],
        current_branch: str | None = None,
        confidence: float = 0.8,
    ) -> None:
        """
        Save current work context.

        Args:
            project_path: Path to project
            focus_area: Detected focus area (e.g., "authentication", "api")
            recent_files: Recently edited files
            recent_commits: Recent commits
            current_branch: Current git branch
            confidence: Confidence in focus area detection (0-1)
        """
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO work_context (
                    project_path, focus_area, recent_files, recent_commits,
                    current_branch, expires_at, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_path,
                    focus_area,
                    json.dumps(recent_files),
                    json.dumps(recent_commits),
                    current_branch,
                    expires_at.isoformat(),
                    confidence,
                ),
            )
            conn.commit()

    def get_latest_work_context(self, project_path: str) -> dict[str, Any] | None:
        """Get most recent work context for project."""
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM work_context 
                WHERE project_path = ? AND expires_at > ?
                ORDER BY detected_at DESC 
                LIMIT 1
                """,
                (project_path, datetime.now(timezone.utc).isoformat()),
            ).fetchone()

            if row is None:
                return None

            return {
                "focus_area": row["focus_area"],
                "recent_files": json.loads(row["recent_files"]) if row["recent_files"] else [],
                "recent_commits": json.loads(row["recent_commits"]) if row["recent_commits"] else [],
                "current_branch": row["current_branch"],
                "detected_at": row["detected_at"],
                "confidence": row["confidence"],
            }

    # =========================================================================
    # Query Cache Operations (1-hour retention)
    # =========================================================================

    def save_query_cache(
        self,
        query_type: str,
        query_params: dict[str, Any],
        result: Any,
        ttl_hours: int = 1,
    ) -> None:
        """
        Cache query result.

        Args:
            query_type: Type of query (e.g., "read", "analyze_url")
            query_params: Query parameters (for hash)
            result: Result to cache
            ttl_hours: Time to live in hours
        """
        # Generate hash from query type + params
        query_str = f"{query_type}:{json.dumps(query_params, sort_keys=True)}"
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()[:16]

        expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO query_cache (query_hash, query_type, result, expires_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(query_hash) DO UPDATE SET
                    result = excluded.result,
                    cached_at = CURRENT_TIMESTAMP,
                    expires_at = excluded.expires_at
                """,
                (query_hash, query_type, json.dumps(result), expires_at.isoformat()),
            )
            conn.commit()

    def get_query_cache(
        self,
        query_type: str,
        query_params: dict[str, Any],
    ) -> Any | None:
        """
        Get cached query result.

        Args:
            query_type: Type of query
            query_params: Query parameters

        Returns:
            Cached result or None if not found/expired
        """
        # Generate hash
        query_str = f"{query_type}:{json.dumps(query_params, sort_keys=True)}"
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()[:16]

        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT result FROM query_cache 
                WHERE query_hash = ? AND expires_at > ?
                """,
                (query_hash, datetime.now(timezone.utc).isoformat()),
            ).fetchone()

            if row is None:
                return None

            return json.loads(row["result"])

    def invalidate_query_cache(self, query_type: str | None = None) -> int:
        """
        Invalidate query cache.

        Args:
            query_type: Specific query type to invalidate, or None for all

        Returns:
            Number of entries deleted
        """
        with self._connection() as conn:
            if query_type:
                cursor = conn.execute(
                    "DELETE FROM query_cache WHERE query_type = ?",
                    (query_type,),
                )
            else:
                cursor = conn.execute("DELETE FROM query_cache")

            conn.commit()
            return cursor.rowcount

    # =========================================================================
    # CORE TABLE OPERATIONS: Plans, Decisions, Learnings, Check-ins
    # =========================================================================

    # ─── PLANS ───────────────────────────────────────────────────────────────

    def save_plan(
        self,
        project_id: str,
        plan_id: str,
        title: str,
        plan_type: str = "goal",
        description: str | None = None,
        due_date: str | None = None,
        parent_id: str | None = None,
        priority: int = 0,
    ) -> None:
        """
        Save a strategic plan item.
        
        Args:
            project_id: Project identifier for isolation
            plan_type: objective (5yr), milestone (1yr), goal (month), task (week)
        """
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO plans (id, project_id, title, type, description, due_date, parent_id, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    project_id = excluded.project_id,
                    title = excluded.title,
                    type = excluded.type,
                    description = excluded.description,
                    due_date = excluded.due_date,
                    priority = excluded.priority
                """,
                (plan_id, project_id, title, plan_type, description, due_date, parent_id, priority),
            )
            conn.commit()

    def get_plan(self, plan_id: str) -> dict[str, Any] | None:
        """Get a plan by ID."""
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
            return dict(row) if row else None

    def list_plans(self, project_id: str | None = None, plan_type: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        """List plans, optionally filtered by project, type or status."""
        with self._connection() as conn:
            query = "SELECT * FROM plans WHERE 1=1"
            params = []
            if project_id:
                query += " AND project_id = ?"
                params.append(project_id)
            if plan_type:
                query += " AND type = ?"
                params.append(plan_type)
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY priority DESC, due_date"
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def update_plan_status(self, plan_id: str, status: str) -> bool:
        """Update plan status (active, done, dropped, blocked)."""
        with self._connection() as conn:
            completed_at = datetime.now(timezone.utc).isoformat() if status == "done" else None
            cursor = conn.execute(
                "UPDATE plans SET status = ?, completed_at = ? WHERE id = ?",
                (status, completed_at, plan_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    # ─── DECISIONS ───────────────────────────────────────────────────────────

    def save_decision(
        self,
        decision_id: str,
        question: str,
        answer: str,
        reasoning: str | None = None,
        category: str | None = None,
        plan_id: str | None = None,
        confidence: int = 5,
    ) -> None:
        """Save a strategic decision."""
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO decisions (id, question, answer, reasoning, category, plan_id, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    answer = excluded.answer,
                    reasoning = excluded.reasoning,
                    confidence = excluded.confidence
                """,
                (decision_id, question, answer, reasoning, category, plan_id, confidence),
            )
            conn.commit()

    def list_decisions(self, category: str | None = None) -> list[dict[str, Any]]:
        """List decisions, optionally filtered by category."""
        with self._connection() as conn:
            if category:
                rows = conn.execute(
                    "SELECT * FROM decisions WHERE category = ? ORDER BY created_at DESC",
                    (category,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM decisions ORDER BY created_at DESC").fetchall()
            return [dict(row) for row in rows]

    # ─── LEARNINGS ───────────────────────────────────────────────────────────

    def save_learning(
        self,
        learning_id: str,
        insight: str,
        source: str | None = None,
        impact: str = "medium",
        plan_id: str | None = None,
    ) -> None:
        """Save a learning/insight."""
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO learnings (id, insight, source, impact, plan_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (learning_id, insight, source, impact, plan_id),
            )
            conn.commit()

    def list_learnings(self, impact: str | None = None) -> list[dict[str, Any]]:
        """List learnings, optionally filtered by impact."""
        with self._connection() as conn:
            if impact:
                rows = conn.execute(
                    "SELECT * FROM learnings WHERE impact = ? ORDER BY created_at DESC",
                    (impact,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM learnings ORDER BY created_at DESC").fetchall()
            return [dict(row) for row in rows]

    # ─── CHECK-INS ───────────────────────────────────────────────────────────

    def save_check_in(
        self,
        check_in_id: str,
        plan_id: str,
        status: str,
        note: str | None = None,
    ) -> None:
        """Save a progress check-in."""
        with self._connection() as conn:
            conn.execute(
                "INSERT INTO check_ins (id, plan_id, status, note) VALUES (?, ?, ?, ?)",
                (check_in_id, plan_id, status, note),
            )
            conn.commit()

    def list_check_ins(self, plan_id: str) -> list[dict[str, Any]]:
        """List check-ins for a plan."""
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM check_ins WHERE plan_id = ? ORDER BY created_at DESC",
                (plan_id,)
            ).fetchall()
            return [dict(row) for row in rows]

    # =========================================================================
    # LEGACY: Goal Operations (for backwards compatibility)
    # =========================================================================

    def save_goal(
        self,
        goal_id: str,
        title: str,
        description: str | None = None,
        due_date: str | None = None,
        parent_id: str | None = None,
        priority: int = 0,
        goal_type: str = "goal",
    ) -> None:
        """
        Save a new goal.
        
        Args:
            goal_type: One of 'dream', 'milestone', 'goal', 'task'
        """
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO goals (id, title, description, due_date, parent_id, priority, goal_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    description = excluded.description,
                    due_date = excluded.due_date,
                    priority = excluded.priority,
                    goal_type = excluded.goal_type
                """,
                (goal_id, title, description, due_date, parent_id, priority, goal_type),
            )
            conn.commit()

    def get_goal(self, goal_id: str) -> dict[str, Any] | None:
        """Get a goal (plan with type=goal) by ID."""
        return self.get_plan(goal_id)

    def list_goals(self, status: str | None = None) -> list[dict[str, Any]]:
        """List all goals (plans with type=goal), optionally filtered by status."""
        return self.list_plans(plan_type="goal", status=status)

    def update_goal_status(self, goal_id: str, status: str) -> bool:
        """Update goal/plan status."""
        return self.update_plan_status(goal_id, status)

    def get_overdue_goals(self) -> list[dict[str, Any]]:
        """Get all overdue goals (past due_date and not done)."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM plans 
                WHERE type = 'goal' AND status NOT IN ('done', 'completed') AND due_date < ?
                ORDER BY due_date
                """,
                (today,)
            ).fetchall()
            return [dict(row) for row in rows]

    def delete_goal(self, goal_id: str) -> bool:
        """Delete a goal/plan."""
        return self.delete_plan(goal_id)

    def get_stalled_goals(self, days: int = 3) -> list[dict[str, Any]]:
        """
        Get goals with no activity for X days.
        """
        from datetime import timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM plans 
                WHERE type = 'goal' AND status NOT IN ('done', 'completed') AND created_at < ?
                ORDER BY created_at
                """,
                (cutoff,)
            ).fetchall()
            return [dict(row) for row in rows]
        with self._connection() as conn:
            # Goals that are pending and created more than X days ago
            # In future: track last_activity timestamp
            rows = conn.execute(
                """
                SELECT * FROM goals 
                WHERE status = 'pending' 
                AND created_at < ?
                ORDER BY created_at
                """,
                (cutoff,)
            ).fetchall()
            return [dict(row) for row in rows]

    def update_goal_activity(self, goal_id: str) -> bool:
        """Update goal's last activity timestamp (for proactive tracking)."""
        # For now, we just touch the created_at as a proxy
        # In future: add last_activity column
        with self._connection() as conn:
            cursor = conn.execute(
                "UPDATE goals SET created_at = ? WHERE id = ?",
                (datetime.now(timezone.utc).isoformat(), goal_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    # =========================================================================
    # Checkpoint Operations (Scheduled Check-ins)
    # =========================================================================

    def save_checkpoint(
        self,
        checkpoint_id: str,
        goal_id: str,
        prompt: str,
        frequency: str = "daily",
    ) -> None:
        """Save a checkpoint for a goal."""
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO checkpoints (id, goal_id, prompt, frequency)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    prompt = excluded.prompt,
                    frequency = excluded.frequency
                """,
                (checkpoint_id, goal_id, prompt, frequency),
            )
            conn.commit()

    def get_due_checkpoints(self) -> list[dict[str, Any]]:
        """Get checkpoints that are due (based on frequency and last_asked)."""
        # now = datetime.now(timezone.utc) # Unused
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT c.*, g.title as goal_title FROM checkpoints c
                JOIN goals g ON c.goal_id = g.id
                WHERE c.enabled = 1 
                AND g.status = 'pending'
                AND (c.last_asked IS NULL OR 
                     (c.frequency = 'daily' AND c.last_asked < date('now', '-1 day')) OR
                     (c.frequency = 'weekly' AND c.last_asked < date('now', '-7 days')))
                """
            ).fetchall()
            return [dict(row) for row in rows]

    def update_checkpoint_response(self, checkpoint_id: str, response: str) -> bool:
        """Update checkpoint with user's response."""
        with self._connection() as conn:
            cursor = conn.execute(
                "UPDATE checkpoints SET last_asked = ?, last_response = ? WHERE id = ?",
                (datetime.now(timezone.utc).isoformat(), response, checkpoint_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def list_goals_by_type(self, goal_type: str) -> list[dict[str, Any]]:
        """List goals filtered by type (dream/milestone/goal/task)."""
        with self._connection() as conn:
            rows = conn.execute(
                "SELECT * FROM goals WHERE goal_type = ? ORDER BY created_at",
                (goal_type,)
            ).fetchall()
            return [dict(row) for row in rows]

    # =========================================================================
    # Auto-Cleanup Operations
    # =========================================================================

    def cleanup_expired_data(self) -> dict[str, int]:
        """
        Clean up expired data (7-day retention for context, 1-hour for cache).

        Returns:
            Dict with counts of deleted records per table
        """
        # now = datetime.now(timezone.utc).isoformat() # Unused
        deleted = {}

        with self._connection() as conn:
            # Clean up expired work context
            cursor = conn.execute(
                "DELETE FROM work_context WHERE expires_at < ?",
                (now,),
            )
            deleted["work_context"] = cursor.rowcount

            # Clean up expired query cache
            cursor = conn.execute(
                "DELETE FROM query_cache WHERE expires_at < ?",
                (now,),
            )
            deleted["query_cache"] = cursor.rowcount

            # Clean up old articles (> 7 days)
            cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            cursor = conn.execute(
                "DELETE FROM articles WHERE fetched_at < ?",
                (cutoff,),
            )
            deleted["articles"] = cursor.rowcount

            # Clean up expired intelligence signals (30-day retention)
            cursor = conn.execute(
                "DELETE FROM intelligence_signals WHERE expires_at < ?",
                (now,),
            )
            deleted["intelligence_signals"] = cursor.rowcount

            conn.commit()

        return deleted

    def get_database_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        with self._connection() as conn:
            stats = {}

            # Table counts
            for table in ["profiles", "articles", "work_context", "query_cache"]:
                row = conn.execute("SELECT COUNT(*) as count FROM {}".format(table)).fetchone()
                stats[f"{table}_count"] = row["count"] if row else 0

            # Database size
            stats["db_size_bytes"] = self.db_path.stat().st_size if self.db_path.exists() else 0
            stats["db_size_mb"] = stats["db_size_bytes"] / (1024 * 1024)

            return stats

    # =========================================================================
    # PRIVACY CONTROLS - User data ownership
    # =========================================================================

    def get_data_summary(self, project_id: str | None = None) -> dict[str, Any]:
        """
        Get summary of all stored data for transparency.
        
        Shows exactly what Side knows about you.
        """
        if project_id is None:
            project_id = self.get_project_id()
        
        with self._connection() as conn:
            summary = {
                "project_id": project_id,
                "data_stored": {},
            }
            
            # Count plans by type
            for table in ["plans", "decisions", "learnings", "check_ins"]:
                try:
                    row = conn.execute(
                        f"SELECT COUNT(*) as count FROM {table} WHERE project_id = ?",
                        (project_id,)
                    ).fetchone()
                    summary["data_stored"][table] = row["count"] if row else 0
                except Exception:
                    summary["data_stored"][table] = 0
            
            summary["db_path"] = str(self.db_path)
            return summary

    def export_project_data(self, project_id: str | None = None) -> dict[str, Any]:
        """
        Export all data for a project.
        
        Returns complete JSON-serializable export for user ownership.
        """
        if project_id is None:
            project_id = self.get_project_id()
        
        with self._connection() as conn:
            export = {
                "project_id": project_id,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "data": {},
            }
            
            for table in ["plans", "decisions", "learnings", "check_ins"]:
                try:
                    rows = conn.execute(
                        f"SELECT * FROM {table} WHERE project_id = ?",
                        (project_id,)
                    ).fetchall()
                    export["data"][table] = [dict(row) for row in rows]
                except Exception:
                    export["data"][table] = []
            
            return export

    def purge_project_data(self, project_id: str | None = None, confirm: bool = False) -> dict[str, int]:
        """
        Completely delete all data for a project.
        
        Requires confirm=True to prevent accidental deletion.
        """
        if not confirm:
            raise ValueError("Must set confirm=True to purge data")
        
        if project_id is None:
            project_id = self.get_project_id()
        
        deleted = {}
        
        with self._connection() as conn:
            for table in ["plans", "decisions", "learnings", "check_ins"]:
                try:
                    cursor = conn.execute(
                        f"DELETE FROM {table} WHERE project_id = ?",
                        (project_id,)
                    )
                    deleted[table] = cursor.rowcount
                except Exception:
                    deleted[table] = 0
            
            conn.commit()
        
        return deleted

    # =========================================================================
    # CONSENT MANAGEMENT - Safe by default, explicit opt-in
    # =========================================================================

    def get_consents(self) -> dict[str, bool]:
        """
        Get current consent settings.
        
        Defaults: proactive_prompts=ON, git_monitoring=ON, everything else OFF.
        """
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM consents WHERE id = 'main'").fetchone()
            
            if row is None:
                # First run - create defaults
                conn.execute("INSERT OR IGNORE INTO consents (id) VALUES ('main')")
                conn.commit()
                return {
                    "proactive_prompts": True,
                    "cloud_sync": False,
                    "analytics": False,
                    "external_apis": False,
                    "git_monitoring": True,
                    "first_run_complete": False,
                }
            
            return {
                "proactive_prompts": bool(row["proactive_prompts"]),
                "cloud_sync": bool(row["cloud_sync"]),
                "analytics": bool(row["analytics"]),
                "external_apis": bool(row["external_apis"]),
                "git_monitoring": bool(row["git_monitoring"]),
                "first_run_complete": bool(row["first_run_complete"]),
            }

    def set_consent(self, feature: str, enabled: bool) -> bool:
        """
        Set consent for a specific feature.
        
        Args:
            feature: proactive_prompts, cloud_sync, analytics, external_apis, git_monitoring
            enabled: True to opt-in, False to opt-out
        """
        valid_features = ["proactive_prompts", "cloud_sync", "analytics", "external_apis", "git_monitoring", "first_run_complete"]
        if feature not in valid_features:
            raise ValueError(f"Invalid feature: {feature}")
        
        with self._connection() as conn:
            conn.execute("INSERT OR IGNORE INTO consents (id) VALUES ('main')")
            conn.execute(
                f"UPDATE consents SET {feature} = ?, updated_at = ? WHERE id = 'main'",
                (1 if enabled else 0, datetime.now(timezone.utc).isoformat())
            )
            conn.commit()
            return True

    def has_consent(self, feature: str) -> bool:
        """Quick check if user has consented to a feature."""
        return self.get_consents().get(feature, False)

    def is_first_run(self) -> bool:
        """Check if this is the first run (for welcome flow)."""
        return not self.has_consent("first_run_complete")

    def complete_first_run(self) -> None:
        """Mark first run as complete."""
        self.set_consent("first_run_complete", True)

    def purge_project_data(self, project_id: str) -> bool:
        """
        [Hyper-Ralph] Scenario 92 Fix: Complete 'Kill Switch' for project data.
        Removes all local records for the given project.
        """
        try:
            with self._connection() as conn:
                conn.execute("DELETE FROM plans WHERE project_id = ?", (project_id,))
                conn.execute("DELETE FROM decisions WHERE project_id = ?", (project_id,))
                conn.execute("DELETE FROM learnings WHERE project_id = ?", (project_id,))
                conn.execute("DELETE FROM check_ins WHERE project_id = ?", (project_id,))
                conn.execute("DELETE FROM profiles WHERE project_id = ?", (project_id,))
                conn.execute("DELETE FROM context WHERE project_id = ?", (project_id,))
                # articles table doesn't have project_id (global cache), 
                # but we could clear old ones if needed.
            return True
        except Exception as e:
            logger.error(f"Purge failed: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════════
    # INTELLIGENCE SIGNALS (Strategic Curation - MVP)
    # ═══════════════════════════════════════════════════════════════════
    
    def save_intelligence_signal(
        self,
        signal_id: str,
        title: str,
        url: str,
        source: str,
        category: str,
        keywords: list[str],
        one_liner: str,
        score: int = 50,
        published_at: str = None,
        retention_days: int = 30
    ) -> None:
        """
        Save a strategic intelligence signal (Top 10 only).
        
        Args:
            signal_id: Unique identifier
            title: Article/paper title
            url: Source URL
            source: 'arxiv', 'hn', 'github', etc.
            category: 'competition', 'open_source', 'llm_research', etc.
            keywords: Extracted keywords
            one_liner: One-line summary
            score: Relevance score (0-100)
            published_at: Publication timestamp
            retention_days: Days to keep (default 30)
        """
        import json
        from datetime import timedelta
        
        expires_at = (datetime.now(timezone.utc) + timedelta(days=retention_days)).isoformat()
        
        with self._connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO intelligence_signals 
                (id, title, url, source, domain, score, keywords, summary, published_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (signal_id, title, url, source, category, score, json.dumps(keywords), 
                 one_liner, published_at, expires_at)
            )
    
    def get_top_signals(
        self,
        category: str = None,
        keywords: list[str] = None,
        min_score: int = 50,
        limit: int = 10,
        days: int = 7
    ) -> list[dict[str, Any]]:
        """
        Retrieve top intelligence signals for RAG context.
        
        Args:
            category: Filter by category ('competition', 'open_source', etc.)
            keywords: Filter by keywords
            min_score: Minimum relevance score
            limit: Max results
            days: Only signals from last N days
        
        Returns:
            List of signal dicts
        """
        import json
        from datetime import timedelta
        
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        query = """
            SELECT id, title, url, source, domain, score, keywords, summary, published_at
            FROM intelligence_signals
            WHERE fetched_at >= ? AND score >= ?
        """
        params = [cutoff, min_score]
        
        if category:
            query += " AND domain = ?"
            params.append(category)
        
        query += " ORDER BY score DESC, published_at DESC LIMIT ?"
        params.append(limit)
        
        with self._connection() as conn:
            rows = conn.execute(query, params).fetchall()
            
            signals = []
            for row in rows:
                signal = {
                    "id": row[0],
                    "title": row[1],
                    "url": row[2],
                    "source": row[3],
                    "category": row[4],
                    "score": row[5],
                    "keywords": json.loads(row[6]) if row[6] else [],
                    "one_liner": row[7],
                    "published_at": row[8],
                }
                
                # Filter by keywords if provided
                if keywords:
                    signal_keywords_str = ' '.join(signal['keywords']).lower()
                    if any(kw.lower() in signal_keywords_str for kw in keywords):
                        signals.append(signal)
                else:
                    signals.append(signal)
            
            return signals[:limit]
    
    def get_signal_stats(self) -> dict[str, Any]:
        """Get intelligence signal statistics."""
        with self._connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM intelligence_signals").fetchone()[0]
            
            by_source = {}
            rows = conn.execute(
                "SELECT source, COUNT(*) FROM intelligence_signals GROUP BY source"
            ).fetchall()
            for source, count in rows:
                by_source[source] = count
            
            by_category = {}
            rows = conn.execute(
                "SELECT domain, COUNT(*) FROM intelligence_signals GROUP BY domain"
            ).fetchall()
            for category, count in rows:
                by_category[category] = count
            
            avg_score = conn.execute(
                "SELECT AVG(score) FROM intelligence_signals"
            ).fetchone()[0] or 0
            
            return {
                "total_signals": total,
                "by_source": by_source,
                "by_category": by_category,
                "avg_score": round(avg_score, 1)
            }