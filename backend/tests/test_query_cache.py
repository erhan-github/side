"""
Tests for query cache integration in tools.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path

from side.storage.simple_db import SimplifiedDatabase


@pytest.fixture
def db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test.db"
    return SimplifiedDatabase(db_path)


class TestQueryCache:
    """Tests for query cache functionality."""

    def test_save_and_get_query_cache(self, db):
        """Test saving and retrieving cached query results."""
        result = {"articles": ["article1", "article2"], "count": 2}
        
        db.save_query_cache(
            query_type="read",
            query_params={"refresh": False},
            result=result,
            ttl_hours=1,
        )

        cached = db.get_query_cache(
            query_type="read",
            query_params={"refresh": False},
        )

        assert cached is not None
        assert cached["count"] == 2
        assert len(cached["articles"]) == 2

    def test_query_cache_different_params(self, db):
        """Test that different params create different cache entries."""
        db.save_query_cache(
            query_type="read",
            query_params={"refresh": False},
            result={"result": "cached"},
        )

        db.save_query_cache(
            query_type="read",
            query_params={"refresh": True},
            result={"result": "fresh"},
        )

        cached = db.get_query_cache("read", {"refresh": False})
        fresh = db.get_query_cache("read", {"refresh": True})

        assert cached["result"] == "cached"
        assert fresh["result"] == "fresh"

    def test_query_cache_expiration(self, db):
        """Test that expired cache entries are not returned."""
        import time

        db.save_query_cache(
            query_type="read",
            query_params={},
            result={"data": "test"},
            ttl_hours=0.0001,  # Very short TTL
        )

        # Should be cached immediately
        cached = db.get_query_cache("read", {})
        assert cached is not None

        # Wait for expiration
        time.sleep(0.5)

        # Should be expired
        cached = db.get_query_cache("read", {})
        assert cached is None

    def test_invalidate_query_cache(self, db):
        """Test cache invalidation."""
        db.save_query_cache("read", {}, {"data": "1"})
        db.save_query_cache("analyze", {}, {"data": "2"})

        # Invalidate specific type
        deleted = db.invalidate_query_cache("read")
        assert deleted == 1

        # read should be gone
        assert db.get_query_cache("read", {}) is None
        # analyze should still exist
        assert db.get_query_cache("analyze", {}) is not None

    def test_invalidate_all_query_cache(self, db):
        """Test invalidating all cache entries."""
        db.save_query_cache("read", {}, {"data": "1"})
        db.save_query_cache("analyze", {}, {"data": "2"})
        db.save_query_cache("strategy", {}, {"data": "3"})

        # Invalidate all
        deleted = db.invalidate_query_cache()
        assert deleted == 3

        # All should be gone
        assert db.get_query_cache("read", {}) is None
        assert db.get_query_cache("analyze", {}) is None
        assert db.get_query_cache("strategy", {}) is None


class TestWorkContext:
    """Tests for work context functionality."""

    def test_save_and_get_work_context(self, db):
        """Test saving and retrieving work context."""
        db.save_work_context(
            project_path="/test/project",
            focus_area="authentication",
            recent_files=["auth.py", "login.py"],
            recent_commits=[{"hash": "abc123", "message": "Add auth"}],
            current_branch="feature/auth",
            confidence=0.9,
        )

        context = db.get_latest_work_context("/test/project")

        assert context is not None
        assert context["focus_area"] == "authentication"
        assert len(context["recent_files"]) == 2
        assert context["current_branch"] == "feature/auth"
        assert context["confidence"] == 0.9

    def test_work_context_expiration(self, db):
        """Test that expired context is not returned."""
        from datetime import timedelta

        # Manually insert expired context
        import sqlite3
        import json

        expires_at = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

        with sqlite3.connect(db.db_path) as conn:
            conn.execute(
                """
                INSERT INTO work_context (
                    project_path, focus_area, recent_files, 
                    recent_commits, expires_at, confidence
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "/test",
                    "api",
                    json.dumps(["api.py"]),
                    json.dumps([]),
                    expires_at,
                    0.8,
                ),
            )
            conn.commit()

        # Should not return expired context
        context = db.get_latest_work_context("/test")
        assert context is None


class TestAutoCleanup:
    """Tests for auto-cleanup functionality."""

    def test_cleanup_expired_data(self, db):
        """Test that cleanup removes expired data."""
        from datetime import timedelta
        import sqlite3
        import json

        # Add expired work context
        expires_at = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        with sqlite3.connect(db.db_path) as conn:
            conn.execute(
                """
                INSERT INTO work_context (
                    project_path, focus_area, recent_files,
                    recent_commits, expires_at, confidence
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("/test", "api", "[]", "[]", expires_at, 0.8),
            )
            conn.commit()

        # Add expired query cache
        with sqlite3.connect(db.db_path) as conn:
            conn.execute(
                """
                INSERT INTO query_cache (
                    query_hash, query_type, result, expires_at
                ) VALUES (?, ?, ?, ?)
                """,
                ("hash123", "read", "{}", expires_at),
            )
            conn.commit()

        # Run cleanup
        deleted = db.cleanup_expired_data()

        assert deleted["work_context"] >= 1
        assert deleted["query_cache"] >= 1

    def test_get_database_stats(self, db):
        """Test database statistics."""
        # Add some data
        db.save_profile(
            path="/test",
            languages={"Python": 100},
            primary_language="Python",
        )

        db.save_work_context(
            project_path="/test",
            focus_area="api",
            recent_files=[],
            recent_commits=[],
        )

        stats = db.get_database_stats()

        assert stats["profiles_count"] == 1
        assert stats["work_context_count"] == 1
        assert stats["db_size_bytes"] > 0
        assert stats["db_size_mb"] > 0
