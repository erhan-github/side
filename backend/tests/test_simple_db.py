"""
Tests for simplified database.
"""

import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from side.storage.simple_db import SimplifiedDatabase


@pytest.fixture
def db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test.db"
    return SimplifiedDatabase(db_path)




class TestSimplifiedDatabase:
    """Tests for SimplifiedDatabase."""

    def test_init_creates_schema(self, db):
        """Test that database initialization creates tables."""
        # Should not raise any errors
        assert db.db_path.exists()

    def test_update_and_get_profile(self, db):
        """Test saving and retrieving profiles."""
        project_id = "test-project"
        profile_data = {
            "name": "Test User",
            "tech_stack": {
                "languages": {"Python": 100, "JavaScript": 50},
                "frameworks": ["FastAPI", "React"],
                "recent_commits": 10,
                "recent_files": ["test.py", "app.js"],
                "focus_areas": ["API", "Frontend"],
            }
        }
        db.update_profile(project_id, profile_data)

        profile = db.get_profile(project_id)

        assert profile is not None
        assert profile["id"] == project_id
        assert profile["name"] == "Test User"
        assert profile["languages"]["Python"] == 100
        assert len(profile["frameworks"]) == 2
        assert profile["recent_commits"] == 10


    def test_get_profile_count(self, db):
        """Test getting profile count."""
        assert db.get_profile_count() == 0

        db.update_profile("test", {"name": "Test Profile"})

        assert db.get_profile_count() == 1
