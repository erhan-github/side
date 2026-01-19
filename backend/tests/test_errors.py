"""
Tests for error handling utilities.
"""

import pytest
import httpx

from side.utils.errors import validate_url, validate_arguments, handle_tool_errors


class TestValidateUrl:
    """Tests for URL validation."""

    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        url = validate_url("https://example.com")
        assert url == "https://example.com"

    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        url = validate_url("http://example.com")
        assert url == "http://example.com"

    def test_adds_https_if_missing(self):
        """Test that https:// is added if missing."""
        url = validate_url("example.com")
        assert url == "https://example.com"

    def test_strips_whitespace(self):
        """Test that whitespace is stripped."""
        url = validate_url("  https://example.com  ")
        assert url == "https://example.com"

    def test_empty_url_raises_error(self):
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError, match="URL cannot be empty"):
            validate_url("")

    def test_url_with_spaces_raises_error(self):
        """Test that URL with spaces raises ValueError."""
        with pytest.raises(ValueError, match="URL contains spaces"):
            validate_url("https://example.com/path with spaces")

    def test_too_long_url_raises_error(self):
        """Test that very long URL raises ValueError."""
        long_url = "https://example.com/" + "a" * 3000
        with pytest.raises(ValueError, match="URL is too long"):
            validate_url(long_url)


class TestValidateArguments:
    """Tests for argument validation."""

    def test_valid_required_arguments(self):
        """Test validation with all required arguments."""
        args = {"url": "https://example.com", "limit": 10}
        # Should not raise
        validate_arguments(args, required=["url", "limit"])

    def test_missing_required_argument_raises_error(self):
        """Test that missing required argument raises ValueError."""
        args = {"url": "https://example.com"}
        with pytest.raises(ValueError, match="Missing required argument: limit"):
            validate_arguments(args, required=["url", "limit"])

    def test_none_value_raises_error(self):
        """Test that None value for required argument raises ValueError."""
        args = {"url": None}
        with pytest.raises(ValueError, match="Missing required argument: url"):
            validate_arguments(args, required=["url"])

    def test_optional_arguments(self):
        """Test validation with optional arguments."""
        args = {"url": "https://example.com", "limit": 10}
        # Should not raise
        validate_arguments(args, required=["url"], optional=["limit"])

    def test_unknown_arguments_logged(self, caplog):
        """Test that unknown arguments are logged."""
        args = {"url": "https://example.com", "unknown": "value"}
        validate_arguments(args, required=["url"])

        # Should log warning about unknown argument
        assert "Unknown argument: unknown" in caplog.text


class TestHandleToolErrors:
    """Tests for tool error handling decorator."""

    @pytest.mark.asyncio
    async def test_successful_execution(self):
        """Test that successful execution returns result."""

        @handle_tool_errors
        async def test_tool(args):
            return "Success!"

        result = await test_tool({})
        assert result == "Success!"

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self):
        """Test handling of timeout errors."""

        @handle_tool_errors
        async def test_tool(args):
            raise httpx.TimeoutException("Request timed out")

        result = await test_tool({})
        assert "Request Timed Out" in result
        assert "⏱️" in result

    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors."""

        @handle_tool_errors
        async def test_tool(args):
            raise httpx.ConnectError("Connection failed")

        result = await test_tool({})
        assert "Network Error" in result
        assert "🌐" in result

    @pytest.mark.asyncio
    async def test_rate_limit_error_handling(self):
        """Test handling of rate limit errors."""

        @handle_tool_errors
        async def test_tool(args):
            response = httpx.Response(429, request=httpx.Request("GET", "http://test"))
            raise httpx.HTTPStatusError("Rate limited", request=response.request, response=response)

        result = await test_tool({})
        assert "Rate Limited" in result
        assert "🚦" in result

    @pytest.mark.asyncio
    async def test_server_error_handling(self):
        """Test handling of server errors."""

        @handle_tool_errors
        async def test_tool(args):
            response = httpx.Response(500, request=httpx.Request("GET", "http://test"))
            raise httpx.HTTPStatusError("Server error", request=response.request, response=response)

        result = await test_tool({})
        assert "Service Unavailable" in result
        assert "🔧" in result

    @pytest.mark.asyncio
    async def test_value_error_handling(self):
        """Test handling of validation errors."""

        @handle_tool_errors
        async def test_tool(args):
            raise ValueError("Invalid input")

        result = await test_tool({})
        assert "Invalid Input" in result
        assert "⚠️" in result

    @pytest.mark.asyncio
    async def test_generic_error_handling(self):
        """Test handling of unexpected errors."""

        @handle_tool_errors
        async def test_tool(args):
            raise RuntimeError("Unexpected error")

        result = await test_tool({})
        assert "Unexpected Error" in result
        assert "❌" in result
