"""
System Identity Store - Profile & Economy Management.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from side.models.core import Identity
from side.utils.helpers import safe_get
from .base import ContextEngine, InsufficientTokensError

logger = logging.getLogger(__name__)

class IdentityService:
    def __init__(self, engine: ContextEngine):
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
                tier TEXT DEFAULT 'hobby',
                token_balance INTEGER DEFAULT 500,
                tokens_monthly INTEGER DEFAULT 500,
                tokens_used INTEGER DEFAULT 0,
                premium_count INTEGER DEFAULT 0, -- Count of strategic actions
                cycle_ended_at TIMESTAMP,
                design_pattern TEXT DEFAULT 'declarative',
                is_airgapped INTEGER DEFAULT 0,
                access_token TEXT, -- [SYSTEM LOCKDOWN]: The trackable sk- key
                email TEXT, -- [NEW]: User email from authentication
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # [MIGRATION]: Add Token-Level Granularity [User Request]
        try:
            conn.execute("ALTER TABLE profile ADD COLUMN premium_count INTEGER DEFAULT 0")
            conn.execute("ALTER TABLE profile ADD COLUMN cycle_started_at TIMESTAMP")
            conn.execute("ALTER TABLE profile ADD COLUMN cycle_ends_at TIMESTAMP")
            conn.execute("ALTER TABLE profile ADD COLUMN access_token TEXT")
            conn.execute("ALTER TABLE profile ADD COLUMN email TEXT")
            logger.info("MIGRATION: Added access_token, email and billing columns to profile")
        except Exception as e:
            logger.debug(f"ℹ️ [MIGRATION]: Token-level columns already exist or migration skipped: {e}")
        
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
        # ECONOMY TABLE: SU_VALUATION - Cost of System [Software 2.0]
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
        # Seed default values from Single Source of Truth
        from side.models.pricing import ActionCost
        
        defaults = [
            ('LOGIC_MUTATION', ActionCost.LOGIC_MUTATION, 'Architectural refactor'),
            ('IDENTITY_RECONFIG', ActionCost.IDENTITY_RECONFIG, 'Identity Rotation/Migration'),
            ('AUDIT_PULSE', ActionCost.AUDIT_PULSE, 'Security audit static analysis'),
            ('SIGNAL_CAPTURE', ActionCost.SIGNAL_CAPTURE, 'Passive terminal friction capture'),
            ('HUB_EVOLVE', ActionCost.HUB_EVOLVE, 'Strategy Center update (plan/check)'),
            ('CONTEXT_BOOST', ActionCost.CONTEXT_BOOST, 'Context Densification (Pattern Index)'),
            ('STRATEGIC_ALIGN', ActionCost.STRATEGIC_ALIGN, 'Strategic goal alignment'),
            ('WELCOME', ActionCost.WELCOME, 'Administrative Bootstrap')
        ]
        conn.executemany(
            "INSERT OR REPLACE INTO su_valuation (action_key, su_cost, description) VALUES (?, ?, ?)",
            defaults
        )

        # ─────────────────────────────────────────────────────────────
        # MIGRATIONS: Architecture Versioning [KAR-3]
        # ─────────────────────────────────────────────────────────────
        try:
            conn.execute("ALTER TABLE profile ADD COLUMN design_pattern TEXT DEFAULT 'declarative'")
            conn.execute("ALTER TABLE profile ADD COLUMN is_airgapped INTEGER DEFAULT 0")
            logger.info("MIGRATION: Added architectural signals to profile")
        except Exception as e:
            logger.debug(f"ℹ️ [MIGRATION]: Architectural signals already exist or migration skipped: {e}")


    def update_profile(self, project_id: str, profile_data: dict[str, Any] | Identity) -> None:
        """Update the High-Integrity Identity Profile."""
        if isinstance(profile_data, Identity):
            identity = profile_data
        else:
            # Backwards compatibility
            tech_stack = safe_get(profile_data, "tech_stack")
            if not tech_stack:
                tech_stack = {
                    "languages": safe_get(profile_data, "languages", {}),
                    "frameworks": safe_get(profile_data, "frameworks", []),
                    "recent_commits": safe_get(profile_data, "recent_commits", 0),
                    "focus_areas": safe_get(profile_data, "focus_areas", [])
                }
            identity = Identity(
                id=project_id,
                name=profile_data.get("name"),
                company=profile_data.get("company"),
                domain=profile_data.get("domain"),
                stage=profile_data.get("stage"),
                business_model=profile_data.get("business_model"),
                target_raise=profile_data.get("target_raise"),
                tech_stack=tech_stack,
                tier=profile_data.get("tier", "hobby"),
                token_balance=profile_data.get("token_balance", 500),
                tokens_monthly=profile_data.get("tokens_monthly", 500),
                tokens_used=profile_data.get("tokens_used", 0),
                design_pattern=profile_data.get("design_pattern", "declarative"),
                is_airgapped=bool(profile_data.get("is_airgapped")),
                access_token=profile_data.get("access_token"),
                email=profile_data.get("email")
            )

        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO profile (
                    id, name, company, domain, stage, business_model, 
                    target_raise, tech_stack, tier, token_balance, tokens_monthly, tokens_used,
                    design_pattern, is_airgapped, access_token, email, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    access_token = COALESCE(excluded.access_token, access_token),
                    email = COALESCE(excluded.email, email),
                    updated_at = excluded.updated_at
                """,
                (
                    identity.id,
                    identity.name,
                    identity.company,
                    identity.domain,
                    identity.stage,
                    identity.business_model,
                    identity.target_raise,
                    identity.model_dump_json(include={'tech_stack'}),
                    identity.tier,
                    identity.token_balance,
                    identity.tokens_monthly,
                    identity.tokens_used,
                    identity.design_pattern,
                    1 if identity.is_airgapped else 0,
                    identity.access_token,
                    identity.email,
                    datetime.now(timezone.utc).isoformat()
                )
            )

    def get_user_profile(self, project_id: str) -> Identity | None:
        """Get the unified profile."""
        with self.engine.connection() as conn:
            row = conn.execute(
                "SELECT * FROM profile WHERE id = ?", (project_id,)
            ).fetchone()
            
            if row:
                return Identity.from_row(row)
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
                    masked_id = f"{project_id[:4]}...{project_id[-4:]}" if len(project_id) > 8 else project_id
                    raise InsufficientTokensError(f"Insufficient SUs for project {masked_id}. Have {current}, need {abs(amount)}.")
            else:
                conn.execute(
                    "UPDATE profile SET token_balance = token_balance + ?, tokens_used = tokens_used + ? WHERE id = ?",
                    (amount, abs(amount) if amount < 0 else 0, project_id)
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

    def charge_action(self, project_id: str, action_key: str) -> bool:
        """
        [ECONOMY]: Deducts SUs for a specific Action.
        Returns True if successful, False if insufficient funds.
        """
        with self.engine.connection() as conn:
            # 1. Get Cost
            cost_row = conn.execute(
                "SELECT su_cost FROM su_valuation WHERE action_key = ?", 
                (action_key,)
            ).fetchone()
            cost = cost_row["su_cost"] if cost_row else 0 # Use column name access from RowFactory
            
            if cost == 0: return True # Free action
            
            # 2. Check Balance
            row = conn.execute("SELECT token_balance FROM profile WHERE id = ?", (project_id,)).fetchone()
            if not row: return False # No profile
            
            balance = row["token_balance"]
            if balance < cost:
                return False # Insufficient Funds
                
            # 3. Deduct
            new_balance = balance - cost
            conn.execute("UPDATE profile SET token_balance = ? WHERE id = ?", (new_balance, project_id))
            
            return True

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

    def get_cursor_usage_summary(self, project_id: str) -> dict[str, Any]:
        """Provides a Cursor-like usage breakdown."""
        with self.engine.connection() as conn:
            row = conn.execute(
                "SELECT tier, token_balance, tokens_monthly, tokens_used, premium_count, cycle_started_at, cycle_ends_at FROM profile WHERE id = ?",
                (project_id,)
            ).fetchone()
            
            if not row:
                return {"error": "Profile not found"}
            
            # [RESET CHECK]: Transparently ensure cycle is current
            self.check_and_reset_cycle(project_id)
            
            # Re-fetch after possible reset
            row = conn.execute(
                "SELECT tier, token_balance, tokens_monthly, tokens_used, premium_count, cycle_started_at, cycle_ends_at FROM profile WHERE id = ?",
                (project_id,)
            ).fetchone()

            from side.models.pricing import PricingModel, Tier
            tier = Tier(row["tier"])
            
            return {
                "tier_label": PricingModel.LABELS[tier],
                "tokens_remaining": row["token_balance"],
                "tokens_monthly": row["tokens_monthly"],
                "tokens_used": row["tokens_used"],
                "premium_requests": row["premium_count"],
                "premium_limit": PricingModel.LIMITS[tier],
                "cycle_ends_at": row["cycle_ends_at"],
                "is_exhausted": row["token_balance"] <= 0
            }

    def check_and_reset_cycle(self, project_id: str):
        """Resets monthly usage if the cycle has expired."""
        with self.engine.connection() as conn:
            row = conn.execute("SELECT cycle_ends_at, tier FROM profile WHERE id = ?", (project_id,)).fetchone()
            if not row or not row["cycle_ends_at"]:
                # Initialize new cycle if missing
                self._initialize_cycle(project_id)
                return

            end_date = datetime.fromisoformat(row["cycle_ends_at"])
            if datetime.now(timezone.utc) > end_date:
                logger.info(f"🔄 [BILLING]: Resetting cycle for {project_id}")
                from side.models.pricing import PricingModel, Tier
                tier = Tier(row["tier"])
                new_limit = PricingModel.get_limit(tier)
                
                new_start = datetime.now(timezone.utc).isoformat()
                from datetime import timedelta
                new_end = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
                
                conn.execute(
                    """
                    UPDATE profile SET 
                        tokens_used = 0, 
                        premium_count = 0,
                        token_balance = ?, 
                        tokens_monthly = ?,
                        cycle_started_at = ?, 
                        cycle_ends_at = ? 
                    WHERE id = ?
                    """,
                    (new_limit, new_limit, new_start, new_end, project_id)
                )

    def _initialize_cycle(self, project_id: str):
        """Initializes a 30-day billing cycle for a new profile."""
        with self.engine.connection() as conn:
            from datetime import timedelta
            now = datetime.now(timezone.utc).isoformat()
            future = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
            conn.execute(
                "UPDATE profile SET cycle_started_at = ?, cycle_ends_at = ? WHERE id = ?",
                (now, future, project_id)
            )

    def increment_premium_count(self, project_id: str):
        """Explicitly tracks high-value premium actions."""
        with self.engine.connection() as conn:
            conn.execute("UPDATE profile SET premium_count = premium_count + 1 WHERE id = ?", (project_id,))
