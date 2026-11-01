"""
Simple tests for app/api/players.py to meet coverage requirements.
"""

from unittest.mock import Mock


def test_api_blueprint_setup():
    """Test API blueprint setup function."""
    from app.api.players import setup_api_blueprint

    mock_db = Mock()
    setup_api_blueprint(mock_db)

    from app.api import players

    assert players.db == mock_db


def test_api_routes_basic():
    """Test that API routes are registered."""
    from app.api.players import api_bp

    # Basic blueprint coverage test
    assert api_bp.name == "api"
    assert api_bp.url_prefix == "/api"


class TestBulkAssign:
    """Real requests against /api/players/bulk-assign (player page bulk actions)."""

    TEAM = 12345

    def _setup(self, app_with_routes, db_session):
        from models import Group
        from tests.conftest import create_test_user
        from tests.factories import setup_authenticated_session

        create_test_user(db_session, user_id=self.TEAM)
        db_session.flush()
        group = Group(self.TEAM, "Main Squad", 1, "#ffffff", "#2e7d32")
        db_session.add(group)
        db_session.flush()
        group_id = group.id
        db_session.commit()
        client = setup_authenticated_session(app_with_routes.test_client(), self.TEAM)
        return client, group_id

    def _post(self, client, group_id, player_ids=(601, 602)):
        return client.post(
            "/api/players/bulk-assign",
            json={
                "player_ids": list(player_ids),
                "group_id": group_id,
                "team_id": self.TEAM,
            },
        )

    def test_assigns_and_clears_group(self, app_with_routes, db_session):
        from models import PlayerSetting

        client, group_id = self._setup(app_with_routes, db_session)

        response = self._post(client, str(group_id))
        assert response.status_code == 200, response.get_json()
        assert response.get_json()["success_count"] == 2
        settings = PlayerSetting.query.filter_by(user_id=self.TEAM).all()
        assert {(s.player_id, s.group_id) for s in settings} == {
            (601, group_id),
            (602, group_id),
        }

        response = self._post(client, None)
        assert response.status_code == 200, response.get_json()
        assert PlayerSetting.query.filter_by(user_id=self.TEAM).count() == 0

    def test_foreign_group_is_rejected_per_player(self, app_with_routes, db_session):
        client, _ = self._setup(app_with_routes, db_session)
        response = self._post(client, "999999", player_ids=[601])
        assert response.status_code == 200
        assert response.get_json()["failures"][0]["error"] == "Invalid group"
