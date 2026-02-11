import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)

class RuleStore:
    """
    [SUBSTORE]: The Legislative Branch.
    Manages the "Constitution" (Rules) in SQLite.
    Replaces: rules.json
    """
    def __init__(self, engine):
        self.engine = engine

    def init_schema(self, conn: sqlite3.Connection) -> None:
        """
        Table: rules
        - category: security | architecture | style
        - key: banned_libraries
        - value_json: ["requests"]
        - source: auto_legislator | manual_override
        - is_active: 1
        """
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                rule_key TEXT NOT NULL,
                value_json TEXT NOT NULL,
                source TEXT DEFAULT 'auto_legislator',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, rule_key)
            )
        """)
        
    def set_rule(self, category: str, key: str, value: Any, source: str = "auto_legislator") -> str:
        """Upsert a rule."""
        rule_id = str(uuid.uuid4())
        val_str = json.dumps(value)
        now = datetime.now(timezone.utc)
        
        with self.engine.connection() as conn:
            # Check if exists to preserve ID or just upsert
            conn.execute("""
                INSERT INTO rules (id, category, rule_key, value_json, source, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(category, rule_key) DO UPDATE SET
                    value_json = excluded.value_json,
                    source = excluded.source,
                    updated_at = excluded.updated_at
            """, (rule_id, category, key, val_str, source, now))
            
        return rule_id

    def get_all_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns the full constitution as a nested dict.
        Format: { "security": { "no_secrets": true }, ... }
        """
        tree = {}
        with self.engine.connection() as conn:
            rows = conn.execute("SELECT category, rule_key, value_json FROM rules WHERE is_active = 1").fetchall()
            
            for r in rows:
                cat = r["category"]
                key = r["rule_key"]
                val = json.loads(r["value_json"])
                
                if cat not in tree:
                    tree[cat] = {}
                tree[cat][key] = val
                
        return tree

    def get_rule(self, category: str, key: str) -> Optional[Any]:
        with self.engine.connection() as conn:
            row = conn.execute(
                "SELECT value_json FROM rules WHERE category = ? AND rule_key = ?",
                (category, key)
            ).fetchone()
            if row:
                return json.loads(row["value_json"])
        return None
