"""Tests for app/chpp_utilities.py"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.chpp_utilities import (
    fetch_user_teams,
    get_chpp_client,
    get_chpp_client_no_auth,
    get_current_user_context,
)


def _fake_chpp():
    chpp = MagicMock()
    chpp.user.return_value = SimpleNamespace(
        _teams_ht_id=[11, 22], username="kvarak", ht_id=7
    )
    chpp.team.side_effect = lambda ht_id: SimpleNamespace(name=f"Team {ht_id}")
    return chpp


def test_get_chpp_client_uses_app_config_and_session(app):
    with app.app_context(), patch("app.chpp_utilities.CHPP") as chpp_cls:
        get_chpp_client({"access_key": "ak", "access_secret": "as"})

    chpp_cls.assert_called_once_with(
        app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRETS"], "ak", "as"
    )


def test_get_chpp_client_explicit_credentials():
    with patch("app.chpp_utilities.CHPP") as chpp_cls:
        get_chpp_client({"access_key": "ak", "access_secret": "as"}, "ck", "cs")

    chpp_cls.assert_called_once_with("ck", "cs", "ak", "as")


def test_get_chpp_client_no_auth_has_no_tokens(app):
    with app.app_context(), patch("app.chpp_utilities.CHPP") as chpp_cls:
        get_chpp_client_no_auth()

    chpp_cls.assert_called_once_with(
        app.config["CONSUMER_KEY"], app.config["CONSUMER_SECRETS"]
    )


def test_fetch_user_teams_returns_ids_and_names():
    team_ids, team_names = fetch_user_teams(_fake_chpp())

    assert team_ids == [11, 22]
    assert team_names == ["Team 11", "Team 22"]


def test_get_current_user_context():
    context = get_current_user_context(_fake_chpp())

    assert context["team_ids"] == [11, 22]
    assert context["team_names"] == ["Team 11", "Team 22"]
    assert context["ht_user"] == "kvarak"
    assert context["ht_id"] == 7


def test_fetch_user_teams_youth_team_fallback():
    import xml.etree.ElementTree as ET

    chpp = MagicMock()
    chpp.user.side_effect = ValueError("YouthTeamId missing")
    chpp.request.return_value = ET.fromstring(
        "<root><Teams><Team><TeamId>11</TeamId></Team>"
        "<Team><TeamId>22</TeamId></Team></Teams></root>"
    )
    chpp.team.side_effect = [SimpleNamespace(name="A"), RuntimeError("boom")]

    assert fetch_user_teams(chpp) == ([11, 22], ["A", "Team 22"])


def test_fetch_user_teams_other_errors_propagate():
    import pytest

    chpp = MagicMock()
    chpp.user.side_effect = RuntimeError("network down")
    with pytest.raises(RuntimeError):
        fetch_user_teams(chpp)
