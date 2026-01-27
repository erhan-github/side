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
                tier TEXT DEFAULT 'free',
                token_balance INTEGER DEFAULT 50,
                tokens_monthly INTEGER DEFAULT 50,
                tokens_used INTEGER DEFAULT 0,
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
                    target_raise, tech_stack, tier, token_balance, tokens_monthly, tokens_used, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
