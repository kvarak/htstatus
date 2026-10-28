#!/usr/bin/env python3
"""
Strategic tests for app.utils module to improve coverage.

Focuses on utility functions, version detection, debugging, and admin functionality
that have missing coverage based on the coverage report.
"""

from datetime import datetime
import subprocess
from unittest.mock import MagicMock, patch

import pytest

# Import the module under test
from app.utils import (
    debug_print,
    diff,
    diff_month,
    dprint,
    get_admin_feedback_counts,
    get_version_info,
    initialize_utils,
)


class TestUtilsAdvanced:
    """Advanced tests for utils module covering uncovered functionality."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = MagicMock()
        db.session = MagicMock()
        return db

    def test_initialize_utils_sets_globals(self, mock_db):
        """Test that initialize_utils sets global variables correctly."""
        mock_app = MagicMock()

        # Test initialization
        initialize_utils(mock_app, mock_db, 2)

        # Import to check globals were set
        import app.utils

        assert app.utils.db is mock_db
        assert app.utils.debug_level == 2

    def test_dprint_with_debug_level_none(self):
        """Test dprint when debug_level is None (should always print)."""
        # Reset debug level to None
        initialize_utils(None, None, None)

        with patch("builtins.print") as mock_print:
            dprint(5, "Test message")

            # Should print regardless of level when debug_level is None
            mock_print.assert_called_once()
            args = mock_print.call_args[0]
            assert "Test message" in args

    def test_dprint_level_allowed(self):
        """Test dprint when message level is within debug level."""
        initialize_utils(None, None, 3)

        with patch("builtins.print") as mock_print:
            dprint(2, "Low level message")

            # Should print when level <= debug_level
            mock_print.assert_called_once()

    def test_dprint_level_too_high(self):
        """Test dprint when message level exceeds debug level."""
        initialize_utils(None, None, 1)

        with patch("builtins.print") as mock_print:
            dprint(5, "High level message")

            # Should not print when level > debug_level
            mock_print.assert_not_called()

    def test_debug_print_enhanced_format(self):
        """Test debug_print with enhanced format and filename extraction."""
        initialize_utils(None, None, 2)

        with patch("builtins.print") as mock_print:
            debug_print("/test/route", "test_function", "arg1", "arg2")

            mock_print.assert_called_once()
            args = mock_print.call_args[0]
            assert "/test/route::test_function() -" in str(args)
            assert "arg1" in args
            assert "arg2" in args

    def test_debug_print_doesnt_print_low_level(self):
        """Test debug_print doesn't print when debug level is too low."""
        initialize_utils(None, None, 1)

        with patch("builtins.print") as mock_print:
            debug_print("/route", "function", "message")

            # debug_print requires debug_level >= 2
            mock_print.assert_not_called()

    def test_diff_month_same_year(self):
        """Test diff_month calculation for dates in same year."""
        d1 = datetime(2024, 6, 15)
        d2 = datetime(2024, 3, 20)

        result = diff_month(d1, d2)
        assert result == 3  # June - March = 3 months

    def test_diff_month_different_years(self):
        """Test diff_month calculation across years."""
        d1 = datetime(2024, 2, 10)
        d2 = datetime(2023, 11, 5)

        result = diff_month(d1, d2)
        assert result == 3  # (2024-2023)*12 + 2-11 = 12-9 = 3

    def test_diff_month_negative(self):
        """Test diff_month with first date earlier than second."""
        d1 = datetime(2024, 1, 1)
        d2 = datetime(2024, 5, 1)

        result = diff_month(d1, d2)
        assert result == -4

    def test_diff_with_none_values(self):
        """Test diff function handles None values correctly."""
        assert diff(None, 5) is None
        assert diff(5, None) is None
        assert diff(None, None) is None

    def test_diff_with_numeric_values(self):
        """Test diff function with numeric arithmetic."""
        assert diff(10, 3) == 7
        assert diff(5.5, 2.2) == pytest.approx(3.3)
        assert diff(-5, -8) == 3

    def test_diff_with_lists(self):
        """Test diff function with list operations (set difference)."""
        list1 = [1, 2, 3, 4]
        list2 = [2, 4]

        result = diff(list1, list2)
        assert set(result) == {1, 3}

    def test_diff_with_sets(self):
        """Test diff function with set operations."""
        set1 = {1, 2, 3, 4}
        set2 = {2, 4, 5}

        result = diff(set1, set2)
        assert set(result) == {1, 3}

    @patch("subprocess.check_output")
    def test_get_version_info_simple_tag(self, mock_subprocess):
        """Test get_version_info with simple tag (no commits ahead)."""
        mock_subprocess.return_value = b"3.12.0\n"

        result = get_version_info()

        assert result["version"] == "3.12.0"
        assert result["fullversion"] == "3.12.0"
        assert result["versionstr"] == "3.12.0"

    @patch("subprocess.check_output")
    def test_get_version_info_with_git_tags(self, mock_subprocess):
        """Test get_version_info with commits ahead of tag."""
        mock_subprocess.return_value = b"3.12-5-g1a2b3c4\n"

        result = get_version_info()

        assert result["version"] == "3.12"
        # First hyphen becomes dot
        assert result["fullversion"] == "3.12.5-g1a2b3c4"
        assert result["versionstr"] == "3.12.5-g1a2b3c4"

    @patch("subprocess.check_output")
    def test_get_version_info_fallback(self, mock_subprocess):
        """Test get_version_info fallback when git command fails."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "git")

        result = get_version_info()

        assert result["version"] == "2.0.0"
        assert result["fullversion"] == "2.0.0-dev"
        assert result["versionstr"] == "2.0.0-dev"

    @patch("subprocess.check_output")
    def test_get_version_info_no_features(self, mock_subprocess):
        """Test get_version_info when git is not available."""
        mock_subprocess.side_effect = FileNotFoundError("git command not found")

        result = get_version_info()

        assert result["version"] == "2.0.0"
        assert result["fullversion"] == "2.0.0-dev"
        assert result["versionstr"] == "2.0.0-dev"

    def test_get_admin_feedback_counts_no_user(self):
        """Test get_admin_feedback_counts when no user_id provided."""
        result = get_admin_feedback_counts()
        assert result is None


def test_module_imports():
    """Test that utils module imports work correctly."""
    import app.utils

    # Verify required functions exist
    assert hasattr(app.utils, "initialize_utils")
    assert hasattr(app.utils, "dprint")
    assert hasattr(app.utils, "debug_print")
    assert hasattr(app.utils, "diff_month")
    assert hasattr(app.utils, "diff")
    assert hasattr(app.utils, "get_version_info")
    assert hasattr(app.utils, "get_admin_feedback_counts")
    assert hasattr(app.utils, "create_page")

    # Verify functions are callable
    assert callable(app.utils.initialize_utils)
    assert callable(app.utils.dprint)
    assert callable(app.utils.debug_print)
