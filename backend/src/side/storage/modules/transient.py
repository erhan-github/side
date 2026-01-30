"""
Sovereign Operational Store - Cache, Metadata, & System Stats.
"""

import json
import logging
import hashlib
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base import SovereignEngine

logger = logging.getLogger(__name__)

class OperationalStore:
    def __init__(self, engine: SovereignEngine):
        self.engine = engine
        with self.engine.connection() as conn:
            self.init_schema(conn)

    def init_schema(self, conn):
        """Initialize operational tables."""
        # ─────────────────────────────────────────────────────────────
        # META TABLE - Database versioning
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        conn.execute("INSERT OR IGNORE INTO meta (key, value) VALUES ('version', '1.0')")

        # ─────────────────────────────────────────────────────────────
        # OPERATIONAL TABLE: MESH_NODES (THE UNIVERSAL MESH)
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mesh_nodes (
                project_id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                name TEXT,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dna_summary TEXT,
                dna_hash INTEGER -- Sparse Semantic Hash (SimHash)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_mesh_last_seen ON mesh_nodes(last_seen)")

        # Migration: Add dna_hash if missing
        try:
            conn.execute("ALTER TABLE mesh_nodes ADD COLUMN dna_hash INTEGER")
        except sqlite3.OperationalError:
            pass # Already exists

        # ─────────────────────────────────────────────────────────────
        # OPERATIONAL TABLE: QUERY_CACHE
        # ─────────────────────────────────────────────────────────────
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
        # OPERATIONAL TABLE: TELEMETRY_ALERTS (THE PROACTIVE OBSERVER)
        # ─────────────────────────────────────────────────────────────
        conn.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                file_path TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_status ON telemetry_alerts(status)")


    def get_version(self) -> float:
        """Get current database version."""
        try:
            with self.engine.connection() as conn:
                row = conn.execute("SELECT value FROM meta WHERE key = 'version'").fetchone()
                return float(row["value"]) if row else 1.0
        except sqlite3.OperationalError:
            return 1.0

    def set_version(self, version: float) -> None:
        """Set database version."""
        with self.engine.connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES ('version', ?)",
                (str(version),)
            )

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        """Get a global system setting."""
        with self.engine.connection() as conn:
            row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        """Set a global system setting."""
        with self.engine.connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
                (key, str(value))
            )

    def save_query_cache(self, query_type: str, query_params: dict[str, Any], 
                         result: Any, ttl_hours: int = 1) -> None:
        """Cache query result."""
        query_str = f"{query_type}:{json.dumps(query_params, sort_keys=True)}"
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()[:16]
        expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)

        with self.engine.connection() as conn:
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

    def get_query_cache(self, query_type: str, query_params: dict[str, Any]) -> Any | None:
        """Get cached query result."""
        query_str = f"{query_type}:{json.dumps(query_params, sort_keys=True)}"
        query_hash = hashlib.sha256(query_str.encode()).hexdigest()[:16]

        with self.engine.connection() as conn:
            row = conn.execute(
                "SELECT result FROM query_cache WHERE query_hash = ? AND expires_at > ?",
                (query_hash, datetime.now(timezone.utc).isoformat()),
            ).fetchone()
            return json.loads(row["result"]) if row else None

    def invalidate_query_cache(self, query_type: str | None = None) -> int:
        """Invalidate query cache."""
        with self.engine.connection() as conn:
            if query_type:
                cursor = conn.execute("DELETE FROM query_cache WHERE query_type = ?", (query_type,))
            else:
                cursor = conn.execute("DELETE FROM query_cache")
            return cursor.rowcount

    def get_database_stats(self, db_path: Path) -> dict[str, Any]:
        """Get database statistics."""
        with self.engine.connection() as conn:
            stats = {}
            tables = ["profile", "plans", "decisions", "learnings", "work_context", "query_cache", "activities", "audits"]
            for table in tables:
                try:
                    row = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()
                    stats[f"{table}_count"] = row["count"] if row else 0
                except sqlite3.OperationalError:
                    stats[f"{table}_count"] = 0

            stats["db_size_bytes"] = db_path.stat().st_size if db_path.exists() else 0
            stats["db_size_mb"] = stats["db_size_bytes"] / (1024 * 1024)
            return stats

    def register_mesh_node(self, project_id: str, path: Path, dna_summary: str | None = None, **kwargs) -> None:
        """Adds or updates a single project in the Local Universal Mesh."""
        self.register_mesh_nodes_batch([{
            'project_id': project_id,
            'path': path,
            'dna_summary': dna_summary,
            'dna_hash': kwargs.get("dna_hash")
        }])

    def register_mesh_nodes_batch(self, nodes: List[Dict[str, Any]]) -> None:
        """Adds or updates multiple projects in a single transaction."""
        with self.engine.connection() as conn:
            for node in nodes:
                path_str = str(node['path'])
                name = Path(path_str).name
                conn.execute(
                    """
                    INSERT INTO mesh_nodes (project_id, path, name, dna_summary, dna_hash, last_seen)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(project_id) DO UPDATE SET
                        path = excluded.path,
                        name = excluded.name,
                        dna_summary = COALESCE(excluded.dna_summary, dna_summary),
                        dna_hash = COALESCE(excluded.dna_hash, dna_hash),
                        last_seen = CURRENT_TIMESTAMP
                    """,
                    (node['project_id'], path_str, name, node.get('dna_summary'), node.get('dna_hash')),
                )

    def list_mesh_nodes(self) -> List[Dict[str, Any]]:
        """Returns all discovered Sidelith projects on this machine."""
        with self.engine.connection() as conn:
            rows = conn.execute("SELECT * FROM mesh_nodes ORDER BY last_seen DESC").fetchall()
            return [dict(row) for row in rows]

    def search_mesh_wisdom(self, query: str) -> List[Dict[str, Any]]:
        """
        Multi-node deep search across all local project brains.
        Searches decisions, learnings, and rejections.
        """
        nodes = self.discover_sovereign_nodes()
        results = []
        
        for node_path in nodes:
            try:
                with sqlite3.connect(node_path) as conn:
                    conn.row_factory = sqlite3.Row
                    q = f"%{query}%"
                    
                    # Resilient Table Search
                    all_rows = []
                    
                    # 1. Decisions
                    try:
                        all_rows.extend(conn.execute("""
                            SELECT 'DECISION' as type, question as title, answer as detail, category 
                            FROM decisions WHERE question LIKE ? OR answer LIKE ?
                        """, (q, q)).fetchall())
                    except sqlite3.OperationalError: pass
                    
                    # 2. Learnings
                    try:
                        all_rows.extend(conn.execute("""
                            SELECT 'LEARNING' as type, insight as title, impact as detail, 'wisdom' 
                            FROM learnings WHERE insight LIKE ?
                        """, (q,)).fetchall())
                    except sqlite3.OperationalError: pass
                    
                    # 3. Rejections
                    try:
                        all_rows.extend(conn.execute("""
                            SELECT 'REJECTION' as type, rejection_reason as title, file_path as detail, 'guardrail' 
                            FROM rejections WHERE rejection_reason LIKE ?
                        """, (q,)).fetchall())
                    except sqlite3.OperationalError: pass
                    
                    for row in all_rows:
                        res = dict(row)
                        res["node"] = node_path.name
                        results.append(res)
            except Exception as e:
                logger.debug(f"Mesh search skipped node {node_path}: {e}")
                continue
                
        return results

    def search_mesh_by_hash(self, target_hash: int, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Bit-level similarity search across all discovered project brains.
        Uses Sparse Semantic Hashes to identify matching architectural patterns.
        """
        nodes = self.discover_sovereign_nodes()
        results = []
        from side.utils.hashing import sparse_hasher

        for node_path in nodes:
            try:
                with sqlite3.connect(node_path) as conn:
                    conn.row_factory = sqlite3.Row
                    
                    # 1. Search Rejections & Public Wisdom by Hash
                    # We fetch all with ANY hash and then distance-filter in Python (Software 2.0 approach)
                    query = """
                        SELECT 'REJECTION' as type, rejection_reason as title, file_path as detail, signal_hash 
                        FROM rejections WHERE signal_hash IS NOT NULL
                        UNION ALL
                        SELECT 'WISDOM' as type, wisdom_text as title, category as detail, signal_hash 
                        FROM public_wisdom WHERE signal_hash IS NOT NULL
                    """
                    
                    rows = conn.execute(query).fetchall()
                    for row in rows:
                        row_hash = row["signal_hash"]
                        if row_hash is not None:
                            similarity = sparse_hasher.similarity(target_hash, row_hash)
                            if similarity >= threshold:
                                res = dict(row)
                                res["similarity"] = round(similarity, 3)
                                res["node"] = node_path.name
                                results.append(res)
            except Exception as e:
                logger.debug(f"Hash search skipped node {node_path}: {e}")
        
        return results

    def save_telemetry_alert(self, project_id: str, alert_type: str, severity: str, 
                             message: str, file_path: str | None = None) -> None:
        """Log a proactive strategic warning."""
        with self.engine.connection() as conn:
            conn.execute(
                """
                INSERT INTO telemetry_alerts (project_id, type, severity, message, file_path)
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, alert_type, severity, message, file_path),
            )

    def get_active_telemetry_alerts(self, project_id: str | None = None) -> List[Dict[str, Any]]:
        """Retrieve active strategic warnings."""
        with self.engine.connection() as conn:
            if project_id:
                rows = conn.execute(
                    "SELECT * FROM telemetry_alerts WHERE project_id = ? AND status = 'active' ORDER BY timestamp DESC",
                    (project_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM telemetry_alerts WHERE status = 'active' ORDER BY timestamp DESC"
                ).fetchall()
            return [dict(row) for row in rows]

    def resolve_telemetry_alert(self, alert_id: int) -> None:
        """Mark a telemetry alert as resolved."""
        with self.engine.connection() as conn:
            conn.execute(
                "UPDATE telemetry_alerts SET status = 'resolved' WHERE id = ?",
                (alert_id,)
            )

    def discover_sovereign_nodes(self) -> List[Path]:
        """Find all Sovereign nodes globally using the Mesh Registry."""
        nodes = []
        # 1. Local Defaults
        side_root = Path.home() / ".side"
        nodes.extend(list(side_root.glob("*.db")))
        
        # 2. Registered Mesh Nodes
        with self.engine.connection() as conn:
            rows = conn.execute("SELECT path FROM mesh_nodes").fetchall()
            for row in rows:
                p = Path(row['path']) / ".side" / "local.db"
                if p.exists() and p not in nodes:
                    nodes.append(p)
                    
        return list(set(nodes))

    def get_semantic_clusters(self, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Groups all wisdom and rejections across the mesh into semantic clusters.
        """
        from side.utils.hashing import sparse_hasher
        nodes = self.discover_sovereign_nodes()
        all_fragments = []
        
        for node_path in nodes:
            try:
                with sqlite3.connect(node_path) as conn:
                    conn.row_factory = sqlite3.Row
                    query = """
                        SELECT 'REJECTION' as type, rejection_reason as title, file_path as detail, signal_hash 
                        FROM rejections WHERE signal_hash IS NOT NULL
                        UNION ALL
                        SELECT 'WISDOM' as type, wisdom_text as title, category as detail, signal_hash 
                        FROM public_wisdom WHERE signal_hash IS NOT NULL
                    """
                    rows = conn.execute(query).fetchall()
                    for r in rows:
                        all_fragments.append({**dict(r), "node": node_path.name})
            except: continue

        clusters = []
        visited = set()

        for i, frag in enumerate(all_fragments):
            if i in visited: continue
            
            # Start a new cluster
            current_cluster = [frag]
            visited.add(i)
            
            for j, other in enumerate(all_fragments):
                if j in visited: continue
                
                similarity = sparse_hasher.similarity(frag['signal_hash'], other['signal_hash'])
                if similarity >= threshold:
                    current_cluster.append(other)
                    visited.add(j)
            
            if len(current_cluster) > 0:
                # Heuristic for cluster name: Use the shortest title as the label
                label = min(current_cluster, key=lambda x: len(x['title']))['title'][:40]
                clusters.append({
                    "label": f"[{label}]",
                    "size": len(current_cluster),
                    "fragments": current_cluster
                })
        
        return sorted(clusters, key=lambda x: x['size'], reverse=True)

    def get_global_stats(self) -> Dict[str, Any]:
        """Aggregate stats across all discovered nodes."""
        nodes = self.discover_sovereign_nodes()
        total_size = 0
        total_profiles = 0
        node_details = []
        
        for node in nodes:
            try:
                size = node.stat().st_size
                total_size += size
                with sqlite3.connect(node) as conn:
                    # FIX: Use 'profile' instead of 'profiles'
                    count = conn.execute("SELECT COUNT(*) FROM profile").fetchone()[0]
                    total_profiles += count
                    node_details.append({
                        "name": node.name,
                        "size_mb": size / (1024 * 1024),
                        "profiles": count
                    })
            except Exception:
                continue
                
        return {
            "total_nodes": len(nodes),
            "total_size_mb": total_size / (1024 * 1024),
            "total_profiles": total_profiles,
            "nodes": node_details
        }
