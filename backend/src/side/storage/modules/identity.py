"""
Sovereign Identity Store - Profile & Economy Management.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from side.utils.helpers import safe_get
from .base import SovereignEngine, InsufficientTokensError

logger = logging.getLogger(__name__)

class IdentityStore:
    def __init__(self, engine: SovereignEngine):
        self.engine = engine
        with self.engine.connection() as conn:
            self.init_schema(conn)

    def init_schema(self, conn):
        """Initialize identity tables."""
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
                tier TEXT DEFAULT 'trial',
                token_balance INTEGER DEFAULT 500,
                tokens_monthly INTEGER DEFAULT 0,
                tokens_used INTEGER DEFAULT 0,
                design_pattern TEXT DEFAULT 'declarative', -- [KAR-3]: Declarative vs Imperative
                is_airgapped INTEGER DEFAULT 0,            -- [PAL-3]: 1 = Local Only, 0 = Mesh Allowed
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ─────────────────────────────────────────────────────────────
        # PRIVACY TABLE: CONSENTS - User Opt-Ins
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
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # ─────────────────────────────────────────────────────────────
        # ECONOMY TABLE: SU_VALUATION - Cost of Sovereignty [Software 2.0]
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS su_valuation (
                action_key TEXT PRIMARY KEY,
                su_cost INTEGER NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Seed default values
        defaults = [
            ('CORE_REFACT', 50, 'Architectural refactor'),
            ('AUTH_SHIFT', 30, 'Authentication logic change'),
            ('FORENSIC_AUDIT', 10, 'Deep forensic analysis'),
            ('SHELL_COMMAND', 1, 'Real-time terminal ingestion'),
            ('RED_TEST_GEN', 25, 'Generative QA reproduction script'),
            ('GHOST_REFACTOR', 100, 'Background worktree refactor experiment'),
            ('SEMANTIC_BOOST', 15, 'High-fidelity architectural audit'),
            ('STRATEGIC_PIVOT', 50, 'Strategic goal drift detection')
        ]
        conn.executemany(
            "INSERT OR IGNORE INTO su_valuation (action_key, su_cost, description) VALUES (?, ?, ?)",
            defaults
        )

        # ─────────────────────────────────────────────────────────────
        # MIGRATIONS: Architecture Versioning [KAR-3]
        # ─────────────────────────────────────────────────────────────
        try:
            conn.execute("ALTER TABLE profile ADD COLUMN design_pattern TEXT DEFAULT 'declarative'")
            conn.execute("ALTER TABLE profile ADD COLUMN is_airgapped INTEGER DEFAULT 0")
            logger.info("MIGRATION: Added architectural signals to profile")
        except: pass


    def update_profile(self, project_id: str, profile_data: dict[str, Any]) -> None:
        """Update the Sovereign Identity Profile."""
        tech_stack = safe_get(profile_data, "tech_stack")
        if not tech_stack:
            tech_stack = {
                "languages": safe_get(profile_data, "languages", {}),
                "frameworks": safe_get(profile_data, "frameworks", []),
                "recent_commits": safe_get(profile_data, "recent_commits", 0),
                "recent_files": safe_get(profile_data, "recent_files", []),
                "focus_areas": safe_get(profile_data, "focus_areas", [])
            }

        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO profile (
                    id, name, company, domain, stage, business_model, 
                    target_raise, tech_stack, tier, token_balance, tokens_monthly, tokens_used,
                    design_pattern, is_airgapped, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = COALESCE(excluded.name, name),
                    company = COALESCE(excluded.company, company),
                    domain = COALESCE(excluded.domain, domain),
                    stage = COALESCE(excluded.stage, stage),
                    business_model = COALESCE(excluded.business_model, business_model),
                    target_raise = COALESCE(excluded.target_raise, target_raise),
                    tech_stack = COALESCE(excluded.tech_stack, tech_stack),
                    tier = COALESCE(excluded.tier, tier),
                    token_balance = COALESCE(excluded.token_balance, token_balance),
                    tokens_monthly = COALESCE(excluded.tokens_monthly, tokens_monthly),
                    tokens_used = COALESCE(excluded.tokens_used, tokens_used),
                    design_pattern = COALESCE(excluded.design_pattern, design_pattern),
                    is_airgapped = COALESCE(excluded.is_airgapped, is_airgapped),
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
                    profile_data.get("token_balance"),
                    profile_data.get("tokens_monthly"),
                    profile_data.get("tokens_used"),
                    profile_data.get("design_pattern", "declarative"),
                    1 if profile_data.get("is_airgapped") else 0,
                    datetime.now(timezone.utc).isoformat()
                )
            )

    def get_profile(self, project_id: str) -> dict[str, Any] | None:
        """Get the unified profile."""
        with self.engine.connection() as conn:
            row = conn.execute(
                "SELECT * FROM profile WHERE id = ?", (project_id,)
            ).fetchone()
            
            if row:
                tech_stack = json.loads(row["tech_stack"]) if row["tech_stack"] else {}
                return {
                    "id": row["id"],
                    "name": row["name"],
                    "tier": row["tier"],
                    "tokens_monthly": row["tokens_monthly"],
                    "tokens_used": row["tokens_used"],
                    "token_balance": row["token_balance"],
                    "languages": tech_stack.get("languages", {}),
                    "frameworks": tech_stack.get("frameworks", []),
                    "recent_commits": tech_stack.get("recent_commits", 0),
                    "focus_areas": tech_stack.get("focus_areas", []),
                    "tech_stack": tech_stack,
                    "design_pattern": row["design_pattern"],
                    "is_airgapped": bool(row["is_airgapped"]),
                    "updated_at": row["updated_at"]
                }
            return None

    def get_token_balance(self, project_id: str) -> dict[str, Any]:
        """Get current SUs and Tier."""
        with self.engine.connection() as conn:
            row = conn.execute(
                "SELECT token_balance, tier FROM profile WHERE id = ?", (project_id,)
            ).fetchone()
            if row:
                return {"balance": row["token_balance"], "tier": row["tier"]}
            return {"balance": 0, "tier": "free"}

    def update_token_balance(self, project_id: str, amount: int) -> int:
        """Update token balance atomically."""
        with self.engine.connection() as conn:
            if amount < 0:
                cursor = conn.execute(
                    """
                    UPDATE profile 
                    SET token_balance = token_balance + ? 
                    WHERE id = ? AND token_balance >= ?
                    """,
                    (amount, project_id, abs(amount))
                )
                if cursor.rowcount == 0:
                    row = conn.execute("SELECT token_balance FROM profile WHERE id = ?", (project_id,)).fetchone()
                    if not row:
                        raise InsufficientTokensError("Profile not found.")
                    current = row["token_balance"]
                    raise InsufficientTokensError(f"Insufficient SUs. Have {current}, need {abs(amount)}.")
            else:
                conn.execute(
                    "UPDATE profile SET token_balance = token_balance + ? WHERE id = ?",
                    (amount, project_id)
                )
            
            row = conn.execute("SELECT token_balance FROM profile WHERE id = ?", (project_id,)).fetchone()
            return row["token_balance"] if row else 0

    def set_token_balance(self, balance: int) -> None:
        """Manually set token balance."""
        with self.engine.connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO profile (id, token_balance) VALUES ('main', ?)",
                (balance,)
            )

    def get_profile_count(self) -> int:
        """Get total profile count."""
        with self.engine.connection() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM profile").fetchone()
            return row["count"] if row else 0

    def get_su_cost(self, action_key: str) -> int:
        """Get the SU cost for a specific action."""
        with self.engine.connection() as conn:
            row = conn.execute(
                "SELECT su_cost FROM su_valuation WHERE action_key = ?", 
                (action_key,)
            ).fetchone()
            return row["su_cost"] if row else 5 # Default cost
            
    def set_su_cost(self, action_key: str, cost: int, description: str | None = None) -> None:
        """Update or set the SU cost for an action."""
        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO su_valuation (action_key, su_cost, description) 
                VALUES (?, ?, ?)
                ON CONFLICT(action_key) DO UPDATE SET 
                    su_cost = excluded.su_cost,
                    description = COALESCE(excluded.description, description),
                    updated_at = CURRENT_TIMESTAMP
                """,
                (action_key, cost, description)
            )
