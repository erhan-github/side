"""
Tests for Technical Intelligence.
"""

import tempfile
from pathlib import Path

import pytest

from cso_ai.intel.technical import TechnicalAnalyzer


class TestTechnicalAnalyzer:
    """Tests for TechnicalAnalyzer."""

    @pytest.fixture
    def temp_codebase(self) -> Path:
        """Create a temporary codebase for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create Python files
            (root / "main.py").write_text("print('hello')")
            (root / "utils.py").write_text("def helper(): pass")

            # Create requirements.txt
            (root / "requirements.txt").write_text(
                "fastapi>=0.100.0\nuvicorn>=0.23.0\npydantic>=2.0.0"
            )

            # Create README
            (root / "README.md").write_text("# Test Project\n\nA test project.")

            # Create tests directory
            (root / "tests").mkdir()
            (root / "tests" / "test_main.py").write_text("def test_hello(): pass")

            yield root

    @pytest.mark.asyncio
    async def test_detect_languages(self, temp_codebase: Path) -> None:
        """Test language detection."""
        analyzer = TechnicalAnalyzer()
        intel = await analyzer.analyze(temp_codebase)

        assert "Python" in intel.languages
        assert intel.primary_language == "Python"

    @pytest.mark.asyncio
    async def test_parse_dependencies(self, temp_codebase: Path) -> None:
        """Test dependency parsing."""
        analyzer = TechnicalAnalyzer()
        intel = await analyzer.analyze(temp_codebase)

        assert "pip" in intel.dependencies
        assert "fastapi" in intel.dependencies["pip"]

    @pytest.mark.asyncio
    async def test_detect_frameworks(self, temp_codebase: Path) -> None:
        """Test framework detection."""
        analyzer = TechnicalAnalyzer()
        intel = await analyzer.analyze(temp_codebase)

        assert "FastAPI" in intel.frameworks

    @pytest.mark.asyncio
    async def test_health_signals(self, temp_codebase: Path) -> None:
        """Test health signal detection."""
        analyzer = TechnicalAnalyzer()
        intel = await analyzer.analyze(temp_codebase)

        assert intel.health_signals["has_readme"] is True
        assert intel.health_signals["has_tests"] is True
