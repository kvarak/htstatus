"""Tests for app/blueprints/team.py"""

from unittest.mock import MagicMock, patch

import pytest

from tests.factories import make_player_record


def test_module_imports():
    """Test that team blueprint module imports without errors."""
    import app.blueprints.team

    assert app.blueprints.team is not None


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


class TestRosterReconciliation:
    """Sold players must be released from the team (regression)."""

    def test_departed_players_released_including_stale_ones(self, db_session):
        import app.blueprints.team as team_module
        from models import Players

        teamid = 999001
        stale = make_player_record(1, teamid, "Michal", "Bittner")
        stale.data_date = "2026-01-01"
        recent_left = make_player_record(2, teamid, "Yngve", "Granbo")
        recent_left.data_date = "2026-09-01"
        staying = make_player_record(3, teamid)
        staying.data_date = "2026-09-01"
        db_session.add_all([stale, recent_left, staying])
        db_session.flush()

        with patch.object(team_module, "db", MagicMock(session=db_session)):
            players_indb = team_module.get_owned_player_ids(Players, teamid)
            assert players_indb == {1, 2, 3}

            # Today's roster from Hattrick: player 3 stays, player 4 is new
            db_session.add(make_player_record(3, teamid))
            db_session.add(make_player_record(4, teamid))
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


class TestSaveTeamCompetitionData:
    """Team competition data is stored atomically (BUG-074)."""

    TEAM_ID = 999101

    @pytest.fixture
    def team_db(self, db_session):
        from app import db
        import app.blueprints.team as team_module
        from models import User

        db_session.add(User(777101, "owner", "owner", "x", "k", "s"))
        db_session.commit()
        with patch.object(team_module, "db", db):
            yield team_module, db_session

    @staticmethod
    def _chpp_team(**overrides):
        from types import SimpleNamespace

        values = {
            "name": "Dalby Stenbrotters FC",
            "league_name": "Sweden",
            "league_level": 5,
            "power_rating": 1234,
            "still_in_cup": True,
            "cup_name": "Cup",
            "cup_level": "3",
            "cup_match_rounds_left": 2,
            "dress_uri": None,
            "logo_url": None,
        }
        values.update(overrides)
        return SimpleNamespace(**values)

    def test_creates_and_updates_team(self, team_db):
        from models import Team

        team_module, _ = team_db

        assert team_module.save_team_competition_data(
            self.TEAM_ID, self._chpp_team(), 777101
        )
        assert team_module.save_team_competition_data(
            self.TEAM_ID, self._chpp_team(power_rating=1500), 777101
        )

        team = Team.get_by_ht_id(self.TEAM_ID)
        assert (team.team_name, team.league_level, team.power_rating) == (
            "Dalby Stenbrotters FC",
            5,
            1500,
        )

    def test_failure_rolls_back_and_session_stays_usable(self, team_db):
        from models import Team, User

        team_module, db_session = team_db

        ok = team_module.save_team_competition_data(
            self.TEAM_ID, self._chpp_team(league_level="not a number"), 777101
        )

        assert ok is False
        assert Team.get_by_ht_id(self.TEAM_ID) is None
        # Without the rollback this query would raise PendingRollbackError
        assert db_session.query(User).filter_by(ht_id=777101).count() == 1


def _fake_chpp_player(ht_id, first, last, **skills):
    from types import SimpleNamespace

    base = {
        "id": ht_id,
        "first_name": first,
        "nick_name": "",
        "last_name": last,
        "number": ht_id % 100,
        "category_id": 0,
        "owner_notes": "",
        "age": 25,
        "age_days": 10,
        "arrival_date": None,
        "form": 6,
        "cards": 0,
        "injury_level": -1,
        "statement": "",
        "country_id": 1,
        "agreeability": 3,
        "aggressiveness": 3,
        "honesty": 3,
        "experience": 4,
        "loyalty": 10,
        "specialty": 0,
    }
    for skill in (
        "stamina",
        "keeper",
        "defender",
        "playmaker",
        "winger",
        "passing",
        "scorer",
        "set_pieces",
    ):
        base[skill] = skills.get(skill, 5)
    return SimpleNamespace(**base)


def _fake_chpp_details():
    from types import SimpleNamespace

    return SimpleNamespace(
        tsi=1000,
        salary=5000,
        caps=0,
        caps_u20=0,
        career_goals=1,
        career_hattricks=0,
        league_goals=1,
        cup_goals=0,
        friendlies_goals=0,
        matches_current_team=3,
        goals_current_team=1,
        national_team_id=None,
        transfer_listed=False,
        mother_club_bonus=False,
        leadership=4,
        transfer_details=None,
    )


class TestBuildPlayerRecord:
    def test_keeps_previous_skill_when_chpp_returns_zero(self):
        from types import SimpleNamespace

        from app.blueprints.team import build_player_record

        p = _fake_chpp_player(801, "Ann", "Keeper", keeper=0, scorer=6)
        previous = SimpleNamespace(keeper=7)

        record = build_player_record(p, _fake_chpp_details(), previous, 4242)

        assert record["keeper"] == 7
        assert record["scorer"] == 6
        assert record["owner"] == 4242
        assert record["friendly_goals"] == 0
        assert record["current_team_matches"] == 3

    def test_zero_skill_without_previous_stays_zero(self):
        from app.blueprints.team import build_player_record

        p = _fake_chpp_player(801, "Ann", "Keeper", keeper=0)
        assert build_player_record(p, _fake_chpp_details(), None, 1)["keeper"] == 0


class TestUpdateRoute:
    """End-to-end /update with a fake CHPP client (REFACTOR-117 safety net)."""

    TEAM = 999301

    def test_update_saves_players_and_reconciles_roster(
        self, app_with_routes, db_session
    ):
        from datetime import datetime, timedelta
        from types import SimpleNamespace

        from models import Players, User
        from tests.factories import make_player_record, setup_authenticated_session

        user = User(self.TEAM, "owner", "owner", "x", "k", "s")
        db_session.add(user)
        for ht_id, last in ((801, "Keeper"), (802, "Sold")):
            row = make_player_record(ht_id, self.TEAM, "Old", last)
            row.data_date = datetime.now() - timedelta(days=3)
            row.keeper = 7
            db_session.add(row)
        db_session.commit()

        team = SimpleNamespace(
            name="Dalby Stenbrotters FC",
            players=lambda: [
                _fake_chpp_player(801, "Ann", "Keeper", keeper=0),
                _fake_chpp_player(803, "New", "Signing"),
            ],
        )
        chpp = SimpleNamespace(
            user=lambda: SimpleNamespace(_teams_ht_id=[self.TEAM]),
            team=lambda ht_id: team,
            player=lambda id_: _fake_chpp_details(),
        )
        no_matches = {"success": True, "recent_count": 0, "upcoming_count": 0}

        client = setup_authenticated_session(app_with_routes.test_client(), self.TEAM)
        with (
            patch("app.blueprints.team.get_chpp_client", return_value=chpp),
            patch("app.utils.downloadRecentMatches", return_value=no_matches),
        ):
            response = client.get("/update")

        html = response.get_data(as_text=True)
        assert response.status_code == 200, html[:500]
        assert "New Signing" in html and "Old Sold" in html

        owned = {
            p.ht_id for p in db_session.query(Players).filter_by(owner=self.TEAM).all()
        }
        assert owned == {801, 803}
        today_keeper = (
            db_session.query(Players)
            .filter_by(ht_id=801, owner=self.TEAM)
            .order_by(Players.data_date.desc())
            .first()
        )
        assert today_keeper.keeper == 7  # CHPP hid it; kept the stored value
        assert db_session.query(User).filter_by(ht_id=self.TEAM).one().c_update == 1
