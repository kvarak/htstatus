"""Tests for app/error_handlers.py - Standardized error handling utilities."""

from unittest.mock import patch

import pytest

from app.error_handlers import (
    AuthenticationError,
    HTStatusError,
    TeamAccessError,
    ValidationError,
    handle_error,
    validate_player_id,
    validate_team_id,
)


def test_module_imports():
    """Test that all error handler classes and functions can be imported correctly."""
    assert HTStatusError is not None
    assert AuthenticationError is not None
    assert ValidationError is not None
    assert TeamAccessError is not None
    assert callable(handle_error)
    assert callable(validate_team_id)
    assert callable(validate_player_id)


class TestHTStatusError:
    """Test base HTStatusError exception class."""

    def test_htstatus_error_basic(self):
        """Test HTStatusError with basic parameters."""
        error = HTStatusError("Test error")

        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.error_code is None
        assert error.template == "main.html"
        assert error.title == "Error"

    def test_htstatus_error_with_all_params(self):
        """Test HTStatusError with all parameters specified."""
        error = HTStatusError(
            message="Custom error",
            error_code="TEST_001",
            template="error.html",
            title="Custom Error"
        )

        assert str(error) == "Custom error"
        assert error.message == "Custom error"
        assert error.error_code == "TEST_001"
        assert error.template == "error.html"
        assert error.title == "Custom Error"


class TestAuthenticationError:
    """Test AuthenticationError exception class."""

    def test_authentication_error_default(self):
        """Test AuthenticationError with default message."""
        error = AuthenticationError()

        assert str(error) == "Authentication required"
        assert error.message == "Authentication required"
        assert error.error_code == "AUTH_001"
        assert error.template == "login.html"
        assert error.title == "Authentication Required"

    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message."""
        error = AuthenticationError("Please log in first")

        assert str(error) == "Please log in first"
        assert error.message == "Please log in first"
        assert error.error_code == "AUTH_001"
        assert error.template == "login.html"
        assert error.title == "Authentication Required"


class TestValidationError:
    """Test ValidationError exception class."""

    def test_validation_error_without_field(self):
        """Test ValidationError without field name."""
        error = ValidationError("Invalid input")

        assert str(error) == "Invalid input"
        assert error.message == "Invalid input"
        assert error.error_code == "VALIDATION_001"
        assert error.field_name is None

    def test_validation_error_with_field(self):
        """Test ValidationError with field name."""
        error = ValidationError("Invalid email format", field_name="email")

        assert str(error) == "Invalid email format"
        assert error.message == "Invalid email format"
        assert error.error_code == "VALIDATION_EMAIL"
        assert error.field_name == "email"


class TestTeamAccessError:
    """Test TeamAccessError exception class."""

    def test_team_access_error_default(self):
        """Test TeamAccessError with default message."""
        error = TeamAccessError()

        assert str(error) == "Access denied for this team"
        assert error.message == "Access denied for this team"
        assert error.error_code == "TEAM_ACCESS_001"
        assert error.template == "main.html"
        assert error.title == "Team Access Error"

    def test_team_access_error_custom_message(self):
        """Test TeamAccessError with custom message."""
        error = TeamAccessError("Team not found")

        assert str(error) == "Team not found"
        assert error.message == "Team not found"
        assert error.error_code == "TEAM_ACCESS_001"
        assert error.template == "main.html"
        assert error.title == "Team Access Error"


class TestHandleError:
    """Test handle_error function."""

    @patch('app.error_handlers.create_page')
    def test_handle_error_with_htstatus_error(self, mock_create_page):
        """Test handle_error with HTStatusError instance."""
        mock_create_page.return_value = "error_page"

        error = ValidationError("Invalid data", field_name="test")
        result = handle_error(error, extra_context="test_value")

        assert result == "error_page"
        mock_create_page.assert_called_once_with(
            template="main.html",
            title="Error",
            error="Invalid data",
            error_code="VALIDATION_TEST",
            extra_context="test_value"
        )

    @patch('app.error_handlers.create_page')
    def test_handle_error_with_string(self, mock_create_page):
        """Test handle_error with string error."""
        mock_create_page.return_value = "error_page"

        result = handle_error("Simple error message")

        assert result == "error_page"
        mock_create_page.assert_called_once_with(
            template="error.html",
            title="Error",
            error="Simple error message"
        )

    @patch('app.error_handlers.create_page')
    def test_handle_error_with_exception(self, mock_create_page):
        """Test handle_error with generic exception."""
        mock_create_page.return_value = "error_page"

        error = ValueError("Value error message")
        result = handle_error(error)

        assert result == "error_page"
        mock_create_page.assert_called_once_with(
            template="error.html",
            title="Error",
            error="Value error message"
        )

    @patch('app.error_handlers.create_page')
    def test_handle_error_with_none(self, mock_create_page):
        """Test handle_error with None error."""
        mock_create_page.return_value = "error_page"

        result = handle_error(None)

        assert result == "error_page"
        mock_create_page.assert_called_once_with(
            template="error.html",
            title="Error",
            error="An unexpected error occurred"
        )


class TestValidateTeamId:
    """Test validate_team_id function."""

    def test_validate_team_id_valid(self):
        """Test validate_team_id with valid team ID."""
        result = validate_team_id("12345")
        assert result == 12345

    def test_validate_team_id_valid_large_number(self):
        """Test validate_team_id with large valid team ID."""
        result = validate_team_id("9999999")
        assert result == 9999999

    def test_validate_team_id_empty_string(self):
        """Test validate_team_id with empty string."""
        with pytest.raises(ValidationError) as exc_info:
            validate_team_id("")

        assert "Team ID is required" in str(exc_info.value)
        assert exc_info.value.field_name == "team_id"

    def test_validate_team_id_none(self):
        """Test validate_team_id with None."""
        with pytest.raises(ValidationError) as exc_info:
            validate_team_id(None)

        assert "Team ID is required" in str(exc_info.value)
        assert exc_info.value.field_name == "team_id"

    def test_validate_team_id_invalid_format(self):
        """Test validate_team_id with invalid format."""
        with pytest.raises(ValidationError) as exc_info:
            validate_team_id("abc123")

        assert "Invalid team ID format" in str(exc_info.value)
        assert exc_info.value.field_name == "team_id"

    def test_validate_team_id_zero(self):
        """Test validate_team_id with zero."""
        with pytest.raises(ValidationError) as exc_info:
            validate_team_id("0")

        assert "Team ID must be positive" in str(exc_info.value)
        assert exc_info.value.field_name == "team_id"

    def test_validate_team_id_negative(self):
        """Test validate_team_id with negative number."""
        with pytest.raises(ValidationError) as exc_info:
            validate_team_id("-123")

        assert "Team ID must be positive" in str(exc_info.value)
        assert exc_info.value.field_name == "team_id"


class TestValidatePlayerId:
    """Test validate_player_id function."""

    def test_validate_player_id_valid(self):
        """Test validate_player_id with valid player ID."""
        result = validate_player_id("67890")
        assert result == 67890

    def test_validate_player_id_valid_large_number(self):
        """Test validate_player_id with large valid player ID."""
        result = validate_player_id("8888888")
        assert result == 8888888

    def test_validate_player_id_empty_string(self):
        """Test validate_player_id with empty string."""
        with pytest.raises(ValidationError) as exc_info:
            validate_player_id("")

        assert "Player ID is required" in str(exc_info.value)
        assert exc_info.value.field_name == "player_id"

    def test_validate_player_id_none(self):
        """Test validate_player_id with None."""
        with pytest.raises(ValidationError) as exc_info:
            validate_player_id(None)

        assert "Player ID is required" in str(exc_info.value)
        assert exc_info.value.field_name == "player_id"

    def test_validate_player_id_invalid_format(self):
        """Test validate_player_id with invalid format."""
        with pytest.raises(ValidationError) as exc_info:
            validate_player_id("xyz789")

        assert "Invalid player ID format" in str(exc_info.value)
        assert exc_info.value.field_name == "player_id"

    def test_validate_player_id_zero(self):
        """Test validate_player_id with zero."""
        with pytest.raises(ValidationError) as exc_info:
            validate_player_id("0")

        assert "Player ID must be positive" in str(exc_info.value)
        assert exc_info.value.field_name == "player_id"

    def test_validate_player_id_negative(self):
        """Test validate_player_id with negative number."""
        with pytest.raises(ValidationError) as exc_info:
            validate_player_id("-456")

        assert "Player ID must be positive" in str(exc_info.value)
        assert exc_info.value.field_name == "player_id"
