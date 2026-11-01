"""Tests for app/blueprints/team.py"""

from unittest.mock import MagicMock, patch

import pytest

from tests.factories import make_player_record


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


def _listed_details():
    from app.chpp.models import BidderTeam, TransferDetails

    details = _fake_chpp_details()
    details.transfer_listed = True
    details.transfer_details = TransferDetails(
        asking_price=500000,
        deadline="2026-11-01 20:15:00",
        highest_bid=620000,
        bidder_team=BidderTeam(team_id=55, team_name="Bidders FC"),
    )
    return details


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
            league_level_unit_id=288,
            players=lambda: [
                _fake_chpp_player(801, "Ann", "Keeper", keeper=0),
                _fake_chpp_player(803, "New", "Signing"),
            ],
        )
        chpp = SimpleNamespace(
            user=lambda: SimpleNamespace(_teams_ht_id=[self.TEAM], language_id=None),
            team=lambda ht_id: team,
            player=lambda id_: (
                _listed_details() if id_ == 803 else _fake_chpp_details()
            ),
        )
        no_matches = {"success": True, "recent_count": 0, "upcoming_count": 0}

        client = setup_authenticated_session(app_with_routes.test_client(), self.TEAM)
        with (
            patch("app.blueprints.team.get_chpp_client", return_value=chpp),
            patch("app.utils.downloadRecentMatches", return_value=no_matches),
            patch("app.blueprints.team.series.refresh") as refresh_series,
            patch("app.blueprints.team.training_log.refresh") as refresh_training,
        ):
            response = client.get("/update")

        html = response.get_data(as_text=True)
        assert response.status_code == 200, html[:500]
        assert "New Signing" in html and "Old Sold" in html
        refresh_series.assert_called_once_with(chpp, self.TEAM, 288)  # FEAT-030
        refresh_training.assert_called_once()  # FEAT-035
        assert refresh_training.call_args.args[2] == self.TEAM

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
        # FEAT-025: bids from the same playerdetails call are kept until next Update
        from app.transfers import team_transfers

        with app_with_routes.app_context():
            saved = team_transfers(self.TEAM)
        assert saved == {
            803: {
                "asking_price": 500000,
                "highest_bid": 620000,
                "deadline": "2026-11-01 20:15:00",
                "bidder": "Bidders FC",
            }
        }


def test_update_error_page_shows_error_and_details(app_with_routes):
    """Regression: the template had a stray endblock and crashed."""
    from app.blueprints.team import update_error_page

    with app_with_routes.test_request_context("/update"):
        html = update_error_page("Hattrick is down", "Traceback: boom")
    assert "Hattrick is down" in html
    assert "Traceback: boom" in html
