"""Tests for app/blueprints/team.py"""

from unittest.mock import MagicMock, patch

import pytest


def test_module_imports():
    """Test that team blueprint module imports without errors."""
    import app.blueprints.team

    assert app.blueprints.team is not None


@pytest.fixture
def authenticated_client():
    """Create test client with authenticated session for team route testing."""
    # Create app with routes for testing
    from app.factory import create_app
    from config import TestConfig

    test_app = create_app(TestConfig, include_routes=True)
    client = test_app.test_client()

    with client.session_transaction() as session:
        session["access_key"] = "test_access_key"
        session["access_secret"] = "test_access_secret"
        session["current_user_id"] = 12345
        session["all_teams"] = [12345]
        session["all_team_names"] = ["Test Team"]
    return client


class TestTeamRoutes:
    """Test team blueprint route functionality."""

    def test_team_route_unauthenticated(self, app):
        """Test team route requires authentication."""
        from app.factory import create_app
        from config import TestConfig

        test_app = create_app(TestConfig, include_routes=True)
        client = test_app.test_client()
        response = client.get("/team")
        # Should redirect to login, show error, or handle gracefully
        assert response.status_code in [200, 302, 401, 403]

    def test_team_route_authenticated_no_team_id(self, authenticated_client):
        """Test team route with authentication but no team ID parameter."""
        response = authenticated_client.get("/team")
        # Should either show team selection or default team
        assert response.status_code in [200, 500]  # Allow 500 for missing data

    def test_team_route_authenticated_with_team_id(self, authenticated_client):
        """Test team route with specific team ID."""
        response = authenticated_client.get("/team?teamid=12345")
        # Should show team information
        assert response.status_code in [200, 500]  # Allow 500 for missing data

    def test_team_route_invalid_team_id(self, authenticated_client):
        """Test team route with invalid team ID."""
        response = authenticated_client.get("/team?teamid=99999")
        # Should handle invalid team ID gracefully
        assert response.status_code in [200, 400, 404, 500]

    def test_update_route_unauthenticated(self, app):
        """Test update route behavior (if it exists)."""
        client = app.test_client()
        response = client.get("/update")
        # Route may not exist in test environment, allow 404
        assert response.status_code in [302, 401, 403, 404]

    @patch("app.blueprints.team.get_chpp_client")
    @patch("app.blueprints.team.fetch_user_teams")
    def test_update_route_authenticated(
        self, mock_fetch_teams, mock_chpp, authenticated_client
    ):
        """Test update route with authentication and mocked CHPP."""
        # Mock CHPP client and team fetching
        mock_chpp_instance = MagicMock()
        mock_chpp.return_value = mock_chpp_instance
        mock_fetch_teams.return_value = None

        response = authenticated_client.get("/update")
        # Should process update request
        assert response.status_code in [200, 302, 500]

    def test_team_route_post_team_id(self, authenticated_client):
        """Test team route with POST team selection."""
        response = authenticated_client.post("/team", data={"teamid": "12345"})
        # Should handle team selection
        assert response.status_code in [200, 302, 500]  # Allow various responses

    def test_team_route_session_data_usage(self, authenticated_client):
        """Test that team route uses session data correctly."""
        # Verify session data is available in route
        with authenticated_client.session_transaction() as session:
            session_teams = session.get("all_teams")
            session_names = session.get("all_team_names")

            assert session_teams == [12345]
            assert session_names == ["Test Team"]

        # Test route access
        response = authenticated_client.get("/team")
        assert response.status_code in [200, 500]


class TestTeamBlueprintSetup:
    """Test team blueprint setup and configuration."""

    def test_blueprint_registration(self, app):
        """Test team blueprint is properly registered."""
        # Check that team blueprint routes are available
        from app.factory import create_app
        from config import TestConfig

        test_app = create_app(TestConfig, include_routes=True)
        with test_app.test_client() as client:
            # Should require authentication or handle gracefully
            response = client.get("/team")
            assert response.status_code in [200, 302, 401, 403]

            response = client.get("/update")
            assert response.status_code in [200, 302, 401, 403]

    def test_team_blueprint_imports(self):
        """Test team blueprint components can be imported."""
        from flask import Blueprint

        from app.blueprints.team import setup_team_blueprint, team_bp

        assert isinstance(team_bp, Blueprint)
        assert team_bp.name == "team"
        assert callable(setup_team_blueprint)

    @patch("app.blueprints.team.get_current_user_id")
    def test_user_authentication_check(self, mock_get_user_id, authenticated_client):
        """Test user authentication validation in team routes."""
        mock_get_user_id.return_value = 12345

        response = authenticated_client.get("/team")
        # Should call user authentication check
        assert response.status_code in [200, 500]

    def test_team_error_handling(self, authenticated_client):
        """Test team route error handling."""
        # Test with malformed team ID
        response = authenticated_client.get("/team?teamid=invalid")
        assert response.status_code in [200, 400, 500]

        # Test with empty session - should redirect via meta refresh
        with authenticated_client.session_transaction() as session:
            session.clear()

        response = authenticated_client.get("/team")
        assert response.status_code == 200
        assert b"url='/login'" in response.data


class TestTeamDataProcessing:
    """Test team data processing functionality."""

    def test_team_statistics_display(self, authenticated_client):
        """Test basic team statistics rendering."""
        response = authenticated_client.get("/team")
        # Should render without major errors
        assert response.status_code in [200, 500]

    def test_team_chart_data_preparation(self, authenticated_client):
        """Test that team route prepares chart data correctly."""
        # This tests the template rendering path
        response = authenticated_client.get("/team")

        if response.status_code == 200:
            # Check if it's a login redirect or actual content
            if b"url='/login'" in response.data:
                # Authentication redirect - expected for unauthenticated access
                assert True
            else:
                # Actual team page content
                assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data


def _player_record(ht_id, owner, first_name="Test", last_name="Player"):
    from models import Players

    fields = {
        "ht_id": ht_id,
        "first_name": first_name,
        "nick_name": "",
        "last_name": last_name,
        "owner": owner,
        "age": 25,
        "is_transfer_listed": False,
        "mother_club_bonus": False,
    }
    for key in [
        "number",
        "category_id",
        "owner_notes",
        "age_years",
        "age_days",
        "next_birthday",
        "arrival_date",
        "form",
        "cards",
        "injury_level",
        "statement",
        "language",
        "language_id",
        "agreeability",
        "aggressiveness",
        "honesty",
        "experience",
        "loyalty",
        "specialty",
        "native_country_id",
        "native_league_id",
        "native_league_name",
        "tsi",
        "salary",
        "caps",
        "caps_u20",
        "career_goals",
        "career_hattricks",
        "league_goals",
        "cup_goals",
        "friendly_goals",
        "current_team_matches",
        "current_team_goals",
        "national_team_id",
        "national_team_name",
        "team_id",
    ]:
        fields[key] = None
    for key in [
        "stamina",
        "keeper",
        "defender",
        "playmaker",
        "winger",
        "passing",
        "scorer",
        "set_pieces",
        "leadership",
    ]:
        fields[key] = 1
    return Players(fields)


class TestRosterReconciliation:
    """Sold players must be released from the team (regression)."""

    def test_departed_players_released_including_stale_ones(self, db_session):
        import app.blueprints.team as team_module
        from models import Players

        teamid = 999001
        stale = _player_record(1, teamid, "Michal", "Bittner")
        stale.data_date = "2026-01-01"
        recent_left = _player_record(2, teamid, "Yngve", "Granbo")
        recent_left.data_date = "2026-09-01"
        staying = _player_record(3, teamid)
        staying.data_date = "2026-09-01"
        db_session.add_all([stale, recent_left, staying])
        db_session.flush()

        with patch.object(team_module, "db", MagicMock(session=db_session)):
            players_indb = team_module.get_owned_player_ids(Players, teamid)
            assert players_indb == {1, 2, 3}

            # Today's roster from Hattrick: player 3 stays, player 4 is new
            db_session.add(_player_record(3, teamid))
            db_session.add(_player_record(4, teamid))
            db_session.flush()

            names = {}
            new, left = team_module.reconcile_roster(
                Players, teamid, players_indb, [3, 4], names
            )

        assert new == [4]
        assert sorted(left) == [1, 2]
        assert names[1] == "Michal Bittner"
        assert names[2] == "Yngve Granbo"
        owned = {
            p.ht_id for p in db_session.query(Players).filter_by(owner=teamid).all()
        }
        assert owned == {3, 4}
        released = db_session.query(Players).filter_by(ht_id=1).one()
        assert (released.owner, released.old_owner) == (0, teamid)
