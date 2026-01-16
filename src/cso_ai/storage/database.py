"""
CSO.ai Database - SQLite storage layer.

Provides persistent storage for all CSO.ai data.
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Generator

from cso_ai.intel.market import Article


class Database:
    """
    SQLite-based storage for CSO.ai.

    Stores:
    - Intelligence profiles
    - Articles
    - Insights
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        """
        Initialize database.

        Args:
            db_path: Path to SQLite database. Defaults to ~/.cso-ai/data.db
        """
        if db_path is None:
            db_dir = Path.home() / ".cso-ai"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "data.db"

        self.db_path = Path(db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        with self._connection() as conn:
            conn.executescript("""
                -- Intelligence profiles
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    technical TEXT NOT NULL,
                    business TEXT NOT NULL,
                    market TEXT,
                    financial TEXT,
                    confidence REAL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                -- Articles from sources
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    source TEXT NOT NULL,
                    description TEXT,
                    author TEXT,
                    score INTEGER,
                    published_at TEXT,
                    fetched_at TEXT NOT NULL,
                    tags TEXT,
                    relevance_score REAL,
                    relevance_reason TEXT
                );

                -- Insights generated
                CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_path TEXT,
                    type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    reasoning TEXT,
                    actions TEXT,
                    confidence REAL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT
                );

                -- Indexes
                CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);
                CREATE INDEX IF NOT EXISTS idx_articles_relevance ON articles(relevance_score DESC);
                CREATE INDEX IF NOT EXISTS idx_insights_profile ON insights(profile_path);
            """)

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # Profile Operations
    # -------------------------------------------------------------------------

    def save_profile(
        self,
        path: str,
        technical: dict[str, Any],
        business: dict[str, Any],
        market: dict[str, Any] | None = None,
        financial: dict[str, Any] | None = None,
        confidence: float = 0,
    ) -> None:
        """Save or update an intelligence profile."""
        now = datetime.utcnow().isoformat()

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO profiles (path, technical, business, market, financial, confidence, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    technical = excluded.technical,
                    business = excluded.business,
                    market = excluded.market,
                    financial = excluded.financial,
                    confidence = excluded.confidence,
                    updated_at = excluded.updated_at
                """,
                (
                    path,
                    json.dumps(technical),
                    json.dumps(business),
                    json.dumps(market) if market else None,
                    json.dumps(financial) if financial else None,
                    confidence,
                    now,
                    now,
                ),
            )

    def get_profile(self, path: str) -> dict[str, Any] | None:
        """Get a profile by path."""
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM profiles WHERE path = ?",
                (path,),
            ).fetchone()

            if row is None:
                return None

            return {
                "path": row["path"],
                "technical": json.loads(row["technical"]),
                "business": json.loads(row["business"]),
                "market": json.loads(row["market"]) if row["market"] else None,
                "financial": json.loads(row["financial"]) if row["financial"] else None,
                "confidence": row["confidence"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }

    def get_latest_profile(self) -> dict[str, Any] | None:
        """Get most recently updated profile."""
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM profiles ORDER BY updated_at DESC LIMIT 1",
            ).fetchone()

            if row is None:
                return None

            return {
                "path": row["path"],
                "technical": json.loads(row["technical"]),
                "business": json.loads(row["business"]),
                "market": json.loads(row["market"]) if row["market"] else None,
                "financial": json.loads(row["financial"]) if row["financial"] else None,
                "confidence": row["confidence"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }

    # -------------------------------------------------------------------------
    # Article Operations
    # -------------------------------------------------------------------------

    def save_article(self, article: Article) -> None:
        """Save or update an article."""
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO articles (id, title, url, source, description, author, score, published_at, fetched_at, tags, relevance_score, relevance_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    score = excluded.score,
                    relevance_score = excluded.relevance_score,
                    relevance_reason = excluded.relevance_reason
                """,
                (
                    article.id,
                    article.title,
                    article.url,
                    article.source,
                    article.description,
                    article.author,
                    article.score,
                    article.published_at.isoformat() if article.published_at else None,
                    article.fetched_at.isoformat(),
                    json.dumps(article.tags),
                    article.relevance_score,
                    article.relevance_reason,
                ),
            )

    def save_articles(self, articles: list[Article]) -> None:
        """Save multiple articles."""
        for article in articles:
            self.save_article(article)

    def get_articles(
        self,
        days: int = 7,
        source: str | None = None,
        limit: int = 50,
    ) -> list[Article]:
        """Get articles with optional filters."""
        from datetime import timedelta

        query = "SELECT * FROM articles WHERE 1=1"
        params: list[Any] = []

        if days > 0:
            cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
            query += " AND fetched_at >= ?"
            params.append(cutoff)

        if source:
            query += " AND source = ?"
            params.append(source)

        query += " ORDER BY relevance_score DESC NULLS LAST LIMIT ?"
        params.append(limit)

        articles = []
        with self._connection() as conn:
            rows = conn.execute(query, params).fetchall()

            for row in rows:
                articles.append(
                    Article(
                        id=row["id"],
                        title=row["title"],
                        url=row["url"],
                        source=row["source"],
                        description=row["description"],
                        author=row["author"],
                        score=row["score"],
                        published_at=(
                            datetime.fromisoformat(row["published_at"])
                            if row["published_at"]
                            else None
                        ),
                        fetched_at=datetime.fromisoformat(row["fetched_at"]),
                        tags=json.loads(row["tags"]) if row["tags"] else [],
                        relevance_score=row["relevance_score"],
                        relevance_reason=row["relevance_reason"],
                    )
                )

        return articles
