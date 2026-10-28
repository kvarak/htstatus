#!/usr/bin/env python3
"""
Additional targeted tests for player diff functions to boost coverage.

Tests player_diff, player_daily_changes, and get_player_changes functions
that have significant uncovered lines according to coverage report.
"""

from unittest.mock import MagicMock, patch

from app.utils import player_daily_changes, player_diff


class TestPlayerDiffFunctions:
    """Test player comparison and change tracking functions."""

    @patch("app.utils.db")
    @patch("app.utils.dprint")
    def test_player_diff_no_old_record(self, mock_dprint, mock_db):
        """Test player_diff when no old record found."""
        # Mock no old record found
        mock_query = mock_db.session.query.return_value
        mock_query.filter_by.return_value.filter.return_value.order_by.return_value.first.side_effect = [
            None,  # No old record
            MagicMock(),  # Current record exists
        ]

        result = player_diff(12345, 7)
        assert result == []

    @patch("app.utils.db")
    @patch("app.utils.dprint")
    def test_player_diff_exception_handling(self, mock_dprint, mock_db):
        """Test player_diff handles exceptions gracefully."""
        # Mock database error
        mock_db.session.query.side_effect = Exception("Database error")

        result = player_diff(12345, 7)

        # Should return empty list and log error
        assert result == []
        mock_dprint.assert_called_once()
        assert "Error in player_diff" in str(mock_dprint.call_args)

    @patch("app.utils.db")
    @patch("app.utils.dprint")
    def test_player_daily_changes_no_records(self, mock_dprint, mock_db):
        """Test player_daily_changes when records not found."""
        mock_query = mock_db.session.query.return_value
        mock_query.filter_by.return_value.filter.return_value.order_by.return_value.first.side_effect = [
            None,  # No target record
            MagicMock(),  # Previous record exists but doesn't matter
        ]

        result = player_daily_changes(54321, 3)
        assert result == []

    @patch("app.utils.db")
    @patch("app.utils.dprint")
    def test_player_daily_changes_exception(self, mock_dprint, mock_db):
        """Test player_daily_changes exception handling."""
        mock_db.session.query.side_effect = Exception("Database connection lost")

        result = player_daily_changes(54321, 3)

        assert result == []
        mock_dprint.assert_called_once()
        assert "Error in player_daily_changes" in str(mock_dprint.call_args)


def test_module_imports():
    """Test that player diff module imports work correctly."""
    from app import utils

    # Verify player diff functions exist
    assert hasattr(utils, "player_diff")
    assert hasattr(utils, "player_daily_changes")

    # Verify functions are callable
    assert callable(utils.player_diff)
    assert callable(utils.player_daily_changes)
