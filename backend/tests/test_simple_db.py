"""
Tests for simplified database.
"""

import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from side.intel.market import Article
from side.storage.simple_db import SimplifiedDatabase


@pytest.fixture
def db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test.db"
    return SimplifiedDatabase(db_path)


@pytest.fixture
def sample_article():
    """Create a sample article for testing."""
    return Article(
        id="test-123",
        title="Test Article",
        url="https://example.com/test",
        source="test",
        description="A test article",
        author="Test Author",
        score=100,
        published_at=datetime.now(timezone.utc),
        tags=["test", "example"],
    )


class TestSimplifiedDatabase:
    """Tests for SimplifiedDatabase."""

    def test_init_creates_schema(self, db):
        """Test that database initialization creates tables."""
        # Should not raise any errors
        assert db.db_path.exists()

    def test_save_and_get_profile(self, db):
        """Test saving and retrieving profiles."""
        db.save_profile(
            path="/test/project",
            languages={"Python": 100, "JavaScript": 50},
            primary_language="Python",
            frameworks=["FastAPI", "React"],
            recent_commits=10,
            recent_files=["test.py", "app.js"],
            focus_areas=["API", "Frontend"],
        )

        profile = db.get_profile("/test/project")

        assert profile is not None
        assert profile["path"] == "/test/project"
        assert profile["primary_language"] == "Python"
        assert len(profile["languages"]) == 2
        assert len(profile["frameworks"]) == 2
        assert profile["recent_commits"] == 10

    def test_get_latest_profile(self, db):
        """Test getting the most recent profile."""
        # Save two profiles
        db.save_profile(
            path="/project1",
            languages={"Python": 100},
            primary_language="Python",
        )

        db.save_profile(
            path="/project2",
            languages={"JavaScript": 100},
            primary_language="JavaScript",
        )

        latest = db.get_latest_profile()

        assert latest is not None
        # Should be the most recently updated
        assert latest["path"] == "/project2"

    def test_save_article(self, db, sample_article):
        """Test saving an article."""
        db.save_article(sample_article)

        # Verify it was saved (check via get_cached_articles)
        articles = db.get_cached_articles(max_age_hours=1, limit=10)

        assert len(articles) == 1
        assert articles[0].id == "test-123"
        assert articles[0].title == "Test Article"

    def test_get_cached_articles_respects_age(self, db, sample_article):
        """Test that cached articles respect max age."""
        # Save an article
        db.save_article(sample_article)

        # Should be returned with 1 hour max age
        articles = db.get_cached_articles(max_age_hours=1, limit=10)
        assert len(articles) == 1

        # Manually update fetched_at to be old
        import sqlite3

        with sqlite3.connect(db.db_path) as conn:
            old_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            conn.execute(
                "UPDATE articles SET fetched_at = ? WHERE id = ?",
                (old_time, sample_article.id),
            )
            conn.commit()

        # Should not be returned with 1 hour max age
        articles = db.get_cached_articles(max_age_hours=1, limit=10)
        assert len(articles) == 0

    def test_save_and_get_article_score(self, db, sample_article):
        """Test caching article scores."""
        db.save_article(sample_article)

        profile_hash = "test_hash_123"
        score = 85.5
        reason = "Highly relevant to your stack"

        # Save score
        db.save_article_score(sample_article.id, profile_hash, score, reason)

        # Retrieve score
        cached_score = db.get_article_score(sample_article.id, profile_hash)

        assert cached_score is not None
        assert cached_score["score"] == score
        assert cached_score["reason"] == reason
        assert "cached_at" in cached_score

    def test_get_article_score_different_profiles(self, db, sample_article):
        """Test that scores are cached per profile."""
        db.save_article(sample_article)

        # Save scores for two different profiles
        db.save_article_score(sample_article.id, "profile1", 90.0, "Great for profile1")
        db.save_article_score(sample_article.id, "profile2", 50.0, "Meh for profile2")

        # Retrieve scores
        score1 = db.get_article_score(sample_article.id, "profile1")
        score2 = db.get_article_score(sample_article.id, "profile2")

        assert score1["score"] == 90.0
        assert score2["score"] == 50.0

    def test_get_article_count(self, db, sample_article):
        """Test getting article count."""
        assert db.get_article_count() == 0

        db.save_article(sample_article)

        assert db.get_article_count() == 1

    def test_get_profile_count(self, db):
        """Test getting profile count."""
        assert db.get_profile_count() == 0

        db.save_profile(
            path="/test",
            languages={"Python": 100},
            primary_language="Python",
        )

        assert db.get_profile_count() == 1

    def test_update_profile(self, db):
        """Test updating an existing profile."""
        # Save initial profile
        db.save_profile(
            path="/test",
            languages={"Python": 100},
            primary_language="Python",
            recent_commits=5,
        )

        # Update with new data
        db.save_profile(
            path="/test",
            languages={"Python": 150, "JavaScript": 50},
            primary_language="Python",
            recent_commits=10,
        )

        # Should have updated, not created new
        assert db.get_profile_count() == 1

        profile = db.get_profile("/test")
        assert profile["recent_commits"] == 10
        assert len(profile["languages"]) == 2
