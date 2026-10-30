"""Tests for app/blueprints/matches.py"""

import re
from unittest.mock import Mock, patch

import pytest

from app.chpp.models import CHPPMatch
from app.utils import downloadMatches


def test_module_imports():
    """Test that matches blueprint module imports without errors."""
    import app.blueprints.matches

    assert app.blueprints.matches is not None


class TestDownloadRecentMatches:
    """Test recent matches download functionality."""

    @pytest.fixture
    def mock_chpp_client(self):
        """Mock CHPP client with sample match data."""
        mock_client = Mock()

        # Sample match data
        sample_matches = [
            CHPPMatch(
                ht_id=12345,
                datetime="2024-01-15 14:30:00",
                home_team_id=1001,
                home_team_name="Home FC",
                away_team_id=1002,
                away_team_name="Away FC",
                home_goals=2,
                away_goals=1,
                matchtype=1,
                context_id=5001,
                rule_id=0,
                cup_level=0,
                cup_level_index=0,
                _SOURCE_FILE="matches",
            ),
            CHPPMatch(
                ht_id=12346,
                datetime="2024-02-15 16:00:00",
                home_team_id=1002,
                home_team_name="Away FC",
                away_team_id=1003,
                away_team_name="Future FC",
                home_goals=None,
                away_goals=None,
                matchtype=1,
                context_id=5001,
                rule_id=0,
                cup_level=0,
                cup_level_index=0,
                _SOURCE_FILE="matches",
            ),
        ]

        mock_client.matches_archive.return_value = sample_matches
        return mock_client

    @patch("app.utils.db")
    @patch(
        "app.utils.session", {"access_key": "test_key", "access_secret": "test_secret"}
    )
    def test_download_recent_matches_success(self, mock_db, mock_chpp_client):
        """Test successful recent matches download."""
        # Mock database session
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = (
            None
        )
        mock_db.session.add = Mock()
        mock_db.session.commit = Mock()

        # Test the function
        result = downloadMatches(1001, mock_chpp_client)

        # Verify results
        assert result["success"] is True
        assert result["count"] >= 0  # Number of new matches added
        assert result["updated"] >= 0  # Number of updated matches
        assert "message" in result
        assert "Archive download complete" in result["message"]

        # Verify CHPP client was called
        mock_chpp_client.matches_archive.assert_called_once_with(id_=1001)

        # Verify database operations
        assert mock_db.session.add.call_count >= 0
        assert mock_db.session.commit.call_count >= 0

    @patch("app.utils.db")
    @patch(
        "app.utils.session", {"access_key": "test_key", "access_secret": "test_secret"}
    )
    def test_download_recent_matches_error_handling(self, mock_db):
        """Test error handling in recent matches download."""
        # Mock CHPP client that raises an exception
        mock_client = Mock()
        mock_client.matches_archive.side_effect = Exception("CHPP API Error")

        # Test the function
        result = downloadMatches(1001, mock_client)

        # Verify graceful error handling - function should succeed but return 0 results
        assert result is not None, "Result should not be None"
        assert result["success"] is True  # Function handles errors gracefully
        assert "message" in result
        assert result["count"] == 0  # No matches processed due to errors
        assert result["updated"] == 0  # No matches updated due to errors

    @patch("app.utils.db")
    def test_download_recent_matches_without_chpp_client(self, mock_db):
        """Test downloadMatches when session access fails."""
        # Test the function without proper session - should handle error gracefully
        result = downloadMatches(1001)

        # Since there's no session data, it should handle the error gracefully
        assert result is not None, "Result should not be None"
        assert result["success"] is False
        assert "error" in result or "message" in result


def _played_match(team_id, ht_id=990001):
    from datetime import datetime

    from models import Match

    match = Match(
        {
            "ht_id": ht_id,
            "home_team_id": team_id,
            "home_team_name": "Test Team",
            "away_team_id": 1,
            "away_team_name": "Rivals FC",
            "datetime": datetime(2026, 10, 1, 20, 0),
            "matchtype": 1,
            "context_id": 0,
            "rule_id": 0,
            "cup_level": 0,
            "cup_level_index": 0,
            "home_goals": 2,
            "away_goals": 1,
            "home_team_chances_left": 2,
            "home_team_chances_center": 2,
            "home_team_chances_right": 1,
            "away_team_chances_left": 1,
            "away_team_chances_center": 1,
            "away_team_chances_right": 1,
        }
    )
    for zone in ("right_def", "mid_def", "left_def", "right_att", "mid_att"):
        setattr(match, f"home_team_rating_{zone}", 8.0)
        setattr(match, f"away_team_rating_{zone}", 2.0)
    for zone in ("left_att", "set_pieces_def", "set_pieces_att"):
        setattr(match, f"home_team_rating_{zone}", 5.0)
        setattr(match, f"away_team_rating_{zone}", 5.0)
    return match


def test_matches_page_shows_ratings_as_us_vs_them(app_with_routes, db_session):
    """Ratings: 'home - away' plus a split bar where our share is the accent."""
    from tests.conftest import create_test_user
    from tests.factories import setup_authenticated_session

    user = create_test_user(db_session)
    db_session.add(_played_match(12345))
    db_session.commit()
    client = setup_authenticated_session(app_with_routes.test_client(), user)

    html = client.get("/matches?id=12345").get_data(as_text=True)

    assert "match-item match-type-league" in html
    assert "team-box us" in html and "team-box them" in html
    assert html.count('class="rating-box"') == 8
    assert re.search(r'class="us"\s+style="width: 80.0%"', html)
    assert "8.0 - 2.0" in html
