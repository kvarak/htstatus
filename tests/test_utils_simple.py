#!/usr/bin/env python3
"""Additional targeted tests for simple utility functions to boost coverage."""

import subprocess
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from app import utils


class TestDiffFunctions(unittest.TestCase):
    """Test date and comparison utility functions."""

    def test_diff_month_same_year(self):
        """Test diff_month with dates in same year."""
        d1 = datetime(2023, 5, 15)
        d2 = datetime(2023, 2, 10)
        result = utils.diff_month(d1, d2)
        assert result == 3

    def test_diff_month_different_years(self):
        """Test diff_month across different years."""
        d1 = datetime(2024, 1, 1)
        d2 = datetime(2023, 10, 15)
        result = utils.diff_month(d1, d2)
        assert result == 3

    def test_diff_month_negative(self):
        """Test diff_month with first date earlier."""
        d1 = datetime(2023, 3, 1)
        d2 = datetime(2023, 7, 15)
        result = utils.diff_month(d1, d2)
        assert result == -4

    def test_diff_with_none_values(self):
        """Test diff function with None values."""
        assert utils.diff(None, 5) is None
        assert utils.diff(10, None) is None
        assert utils.diff(None, None) is None

    def test_diff_numeric_values(self):
        """Test diff with numeric values."""
        assert utils.diff(10, 3) == 7
        assert utils.diff(5, 8) == -3
        assert utils.diff(0, 0) == 0

    def test_diff_list_operations(self):
        """Test diff with lists."""
        first = [1, 2, 3, 4]
        second = [2, 4]
        result = utils.diff(first, second)
        assert set(result) == {1, 3}

    def test_diff_tuple_operations(self):
        """Test diff with tuples."""
        first = (1, 2, 3)
        second = (2, 3, 4)
        result = utils.diff(first, second)
        assert set(result) == {1}

    def test_diff_set_operations(self):
        """Test diff with sets."""
        first = {1, 2, 3, 4, 5}
        second = {3, 4, 5, 6}
        result = utils.diff(first, second)
        assert set(result) == {1, 2}

    def test_diff_empty_collections(self):
        """Test diff with empty collections."""
        assert utils.diff([], [1, 2]) == []
        assert utils.diff([1, 2], []) == [1, 2]
        assert utils.diff([], []) == []


class TestVersionUtilities(unittest.TestCase):
    """Test version detection utilities."""

    @patch('subprocess.check_output')
    def test_get_version_info_exact_tag(self, mock_subprocess):
        """Test get_version_info with exact tag match."""
        mock_subprocess.return_value = b"3.12\n"

        result = utils.get_version_info()

        assert result['version'] == "3.12"
        assert result['fullversion'] == "3.12"
        assert result['versionstr'] == "3.12"
        mock_subprocess.assert_called_once_with(["git", "describe", "--tags"])

    @patch('subprocess.check_output')
    def test_get_version_info_commits_ahead(self, mock_subprocess):
        """Test get_version_info with commits ahead of tag."""
        mock_subprocess.return_value = b"3.15-8-g5015d35\n"

        result = utils.get_version_info()

        assert result['version'] == "3.15"
        assert result['fullversion'] == "3.15.8-g5015d35"
        assert result['versionstr'] == "3.15.8-g5015d35"

    @patch('subprocess.check_output')
    def test_get_version_info_git_error(self, mock_subprocess):
        """Test get_version_info with git command failure."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'git')

        result = utils.get_version_info()

        assert result['version'] == "2.0.0"
        assert result['fullversion'] == "2.0.0-dev"
        assert result['versionstr'] == "2.0.0-dev"


class TestDebugUtilities(unittest.TestCase):
    """Test debugging and logging utilities."""

    def setUp(self):
        """Set up test environment."""
        # Store original debug_level
        self.original_debug_level = utils.debug_level

    def tearDown(self):
        """Clean up after tests."""
        # Restore original debug_level
        utils.debug_level = self.original_debug_level

    @patch('builtins.print')
    def test_dprint_with_level(self, mock_print):
        """Test dprint with debug level set."""
        utils.debug_level = 2
        utils.dprint(1, "Test message", "additional arg")

        mock_print.assert_called_once()
        # Check that the call includes the filename and message
        call_args = mock_print.call_args[0]
        assert "Test message" in str(call_args)
        assert "additional arg" in str(call_args)

    @patch('builtins.print')
    def test_dprint_level_too_high(self, mock_print):
        """Test dprint when message level exceeds debug level."""
        utils.debug_level = 1
        utils.dprint(2, "Should not print")

        mock_print.assert_not_called()

    @patch('builtins.print')
    def test_dprint_none_debug_level(self, mock_print):
        """Test dprint when debug_level is None."""
        utils.debug_level = None
        utils.dprint(5, "Should print anyway")

        mock_print.assert_called_once()

    @patch('builtins.print')
    def test_debug_print_enabled(self, mock_print):
        """Test debug_print when debug level is sufficient."""
        utils.debug_level = 2
        utils.debug_print("/test", "function_name", "arg1", "arg2")

        mock_print.assert_called_once()
        call_args = mock_print.call_args[0]
        assert "/test" in str(call_args)
        assert "function_name()" in str(call_args)
        assert "arg1" in str(call_args)

    @patch('builtins.print')
    def test_debug_print_disabled(self, mock_print):
        """Test debug_print when debug level is too low."""
        utils.debug_level = 1
        utils.debug_print("/test", "function_name", "message")

        mock_print.assert_not_called()

    @patch('builtins.print')
    def test_debug_print_none_level(self, mock_print):
        """Test debug_print when debug_level is None."""
        utils.debug_level = None
        utils.debug_print("/test", "function_name", "message")

        mock_print.assert_called_once()


class TestUtilityInitialization(unittest.TestCase):
    """Test utility module initialization."""

    def test_initialize_utils(self):
        """Test initialize_utils function."""
        mock_app = Mock()
        mock_db = Mock()
        debug_level_value = 3

        utils.initialize_utils(mock_app, mock_db, debug_level_value)

        assert utils.db == mock_db
        assert utils.debug_level == debug_level_value


if __name__ == '__main__':
    unittest.main()
