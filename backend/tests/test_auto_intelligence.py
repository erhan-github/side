"""
Tests for auto_intelligence module.
"""

import pytest
from pathlib import Path

from side.intel.auto_intelligence import AutoIntelligence, QuickProfile


class TestQuickProfile:
    """Tests for QuickProfile dataclass."""

    def test_to_dict(self):
        """Test serialization to dict."""
        profile = QuickProfile(
            path="/test/path",
            languages={"Python": 100, "JavaScript": 50},
            primary_language="Python",
            frameworks=["FastAPI", "React"],
            recent_commits=10,
            recent_files=["test.py", "app.js"],
            focus_areas=["API development", "Frontend"],
        )

        data = profile.to_dict()

        assert data["path"] == "/test/path"
        assert data["languages"] == {"Python": 100, "JavaScript": 50}
        assert data["primary_language"] == "Python"
        assert data["frameworks"] == ["FastAPI", "React"]
        assert data["recent_commits"] == 10
        assert len(data["recent_files"]) == 2
        assert len(data["focus_areas"]) == 2

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "path": "/test/path",
            "languages": {"Python": 100},
            "primary_language": "Python",
            "frameworks": ["FastAPI"],
            "recent_commits": 5,
            "recent_files": ["test.py"],
            "focus_areas": ["Testing"],
            "created_at": "2026-01-16T00:00:00+00:00",
            "expires_at": "2026-01-17T00:00:00+00:00",
        }

        profile = QuickProfile.from_dict(data)

        assert profile.path == "/test/path"
        assert profile.primary_language == "Python"
        assert len(profile.frameworks) == 1

    def test_get_hash(self):
        """Test profile hash generation."""
        profile1 = QuickProfile(
            path="/test",
            languages={"Python": 100},
            frameworks=["FastAPI"],
        )

        profile2 = QuickProfile(
            path="/test",
            languages={"Python": 100},
            frameworks=["FastAPI"],
        )

        # Same languages and frameworks should produce same hash
        assert profile1.get_hash() == profile2.get_hash()

        profile3 = QuickProfile(
            path="/test",
            languages={"JavaScript": 100},
            frameworks=["React"],
        )

        # Different stack should produce different hash
        assert profile1.get_hash() != profile3.get_hash()

    def test_is_expired(self):
        """Test expiration check."""
        from datetime import datetime, timedelta, timezone

        # Create expired profile
        profile = QuickProfile(path="/test")
        profile.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)

        assert profile.is_expired()

        # Create fresh profile
        profile2 = QuickProfile(path="/test")
        profile2.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        assert not profile2.is_expired()


class TestAutoIntelligence:
    """Tests for AutoIntelligence."""

    @pytest.mark.asyncio
    async def test_get_or_create_profile_creates_new(self, tmp_path):
        """Test profile creation for new path."""
        auto_intel = AutoIntelligence()

        # Create a simple test project
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        profile = await auto_intel.get_or_create_profile(str(tmp_path))

        assert profile is not None
        assert profile.path == str(tmp_path.resolve())
        assert isinstance(profile.languages, dict)

    @pytest.mark.asyncio
    async def test_get_or_create_profile_uses_cache(self, tmp_path):
        """Test that cached profile is reused."""
        auto_intel = AutoIntelligence()

        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        # First call - creates profile
        profile1 = await auto_intel.get_or_create_profile(str(tmp_path))

        # Second call - should use cache
        profile2 = await auto_intel.get_or_create_profile(str(tmp_path))

        # Should be the same object (from cache)
        assert profile1 is profile2

    @pytest.mark.asyncio
    async def test_detect_languages_fast(self, tmp_path):
        """Test language detection."""
        auto_intel = AutoIntelligence()

        # Create test files
        (tmp_path / "test.py").write_text("print('hello')")
        (tmp_path / "app.js").write_text("console.log('hello')")
        (tmp_path / "style.css").write_text("body { color: red; }")

        languages = await auto_intel._detect_languages_fast(tmp_path)

        assert "Python" in languages
        assert "JavaScript" in languages
        assert languages["Python"] == 1
        assert languages["JavaScript"] == 1

    @pytest.mark.asyncio
    async def test_detect_frameworks_fast_python(self, tmp_path):
        """Test Python framework detection."""
        auto_intel = AutoIntelligence()

        # Create requirements.txt with FastAPI
        requirements = tmp_path / "requirements.txt"
        requirements.write_text("fastapi==0.100.0\nuvicorn==0.20.0")

        frameworks = await auto_intel._detect_frameworks_fast(tmp_path)

        assert "FastAPI" in frameworks

    @pytest.mark.asyncio
    async def test_detect_frameworks_fast_javascript(self, tmp_path):
        """Test JavaScript framework detection."""
        import json

        auto_intel = AutoIntelligence()

        # Create package.json with React
        package_json = tmp_path / "package.json"
        package_json.write_text(
            json.dumps(
                {
                    "dependencies": {
                        "react": "^18.0.0",
                        "react-dom": "^18.0.0",
                    }
                }
            )
        )

        frameworks = await auto_intel._detect_frameworks_fast(tmp_path)

        assert "React" in frameworks

    @pytest.mark.asyncio
    async def test_infer_focus_from_files(self):
        """Test focus area inference from file paths."""
        auto_intel = AutoIntelligence()

        files = [
            "src/api/endpoints/users.py",
            "src/api/endpoints/auth.py",
            "tests/test_auth.py",
            "docker-compose.yml",
        ]

        focus_areas = auto_intel._infer_focus_from_files(files)

        # Should detect at least 2 focus areas from these files
        assert len(focus_areas) >= 2
        # API files should be detected
        assert any("API" in area or "Testing" in area or "Infrastructure" in area for area in focus_areas)

    @pytest.mark.asyncio
    async def test_handles_invalid_path(self):
        """Test handling of invalid path."""
        auto_intel = AutoIntelligence()

        profile = await auto_intel.get_or_create_profile("/nonexistent/path")

        # Should return empty profile, not crash
        assert profile.path == "/nonexistent/path"
        assert len(profile.languages) == 0
        assert profile.primary_language is None
