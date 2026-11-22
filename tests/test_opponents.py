"""Tests for app/opponents.py (FEAT-008 scouting)."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from app.opponents import (
    opponent_of,
    prune_opponent_matches,
    refresh_opponent_matches,
    setup_summary,
    summarise,
)
from models import Match

OUR_ID = 1
THEIR_ID = 2


def make_match(
    home, away, home_goals, away_goals, when, status="FINISHED", matchtype=1
):
    """Build a Match row for team ids home and away."""
    return Match(
        {
            "ht_id": int(when.timestamp()) + home * 10 + away,
            "home_team_id": home,
            "home_team_name": f"Team {home}",
            "away_team_id": away,
            "away_team_name": f"Team {away}",
            "datetime": when,
            "matchtype": matchtype,
            "context_id": 0,
            "rule_id": 0,
            "cup_level": 0,
            "cup_level_index": 0,
            "home_goals": home_goals,
            "away_goals": away_goals,
            "status": status,
        }
    )


class TestOpponentOf:
    def test_returns_away_side_when_we_are_home(self):
        match = make_match(OUR_ID, THEIR_ID, None, None, datetime(2030, 1, 1))
        assert opponent_of(match, OUR_ID) == THEIR_ID

    def test_returns_home_side_when_we_are_away(self):
        match = make_match(THEIR_ID, OUR_ID, None, None, datetime(2030, 1, 1))
        assert opponent_of(match, OUR_ID) == THEIR_ID


class TestSummarise:
    def test_counts_results_from_our_side_and_splits_home_away(self):
        matches = [
            make_match(OUR_ID, THEIR_ID, 2, 1, datetime(2024, 1, 1)),  # home W
            make_match(THEIR_ID, OUR_ID, 3, 0, datetime(2024, 2, 1)),  # away L
            make_match(OUR_ID, THEIR_ID, 1, 1, datetime(2024, 3, 1)),  # home D
            make_match(THEIR_ID, OUR_ID, 0, 2, datetime(2024, 4, 1)),  # away W
        ]
        result = summarise(matches, OUR_ID)

        assert result["record"]["all"] == {"W": 2, "D": 1, "L": 1}
        assert result["record"]["home"] == {"W": 1, "D": 1, "L": 0}
        assert result["record"]["away"] == {"W": 1, "D": 0, "L": 1}

    def test_rows_are_newest_first_with_goals_from_our_side(self):
        matches = [
            make_match(THEIR_ID, OUR_ID, 3, 0, datetime(2024, 2, 1)),
            make_match(OUR_ID, THEIR_ID, 2, 1, datetime(2024, 1, 1)),
        ]
        rows = summarise(matches, OUR_ID)["matches"]

        assert [r["date"] for r in rows] == [datetime(2024, 2, 1), datetime(2024, 1, 1)]
        assert rows[0]["goals_for"] == 0
        assert rows[0]["goals_against"] == 3
        assert rows[0]["result"] == "L"
        assert rows[0]["home"] is False
        assert rows[0]["opponent"] == "Team 2"

    def test_skips_unfinished_matches(self):
        matches = [
            make_match(OUR_ID, THEIR_ID, 0, 0, datetime(2030, 1, 1), status="ONGOING"),
            make_match(OUR_ID, THEIR_ID, None, None, datetime(2030, 2, 1), status=None),
        ]
        result = summarise(matches, OUR_ID)

        assert result["matches"] == []
        assert result["record"]["all"] == {"W": 0, "D": 0, "L": 0}

    def test_empty_input(self):
        result = summarise([], OUR_ID)
        assert result["matches"] == []


class TestRefreshOpponentMatches:
    @patch("app.opponents._process_matches_enhanced")
    @patch("app.db")
    def test_fetches_each_opponent_without_enhanced_data(self, mock_db, mock_process):
        upcoming = [make_match(OUR_ID, THEIR_ID, None, None, datetime(2099, 1, 1))]
        mock_db.session.query.return_value.filter.return_value.all.return_value = (
            upcoming
        )
        chpp = Mock()
        chpp.matches.return_value = ["sentinel"]

        refresh_opponent_matches(chpp, [OUR_ID])

        chpp.matches.assert_called_once_with(id_=THEIR_ID, is_youth=False)
        mock_process.assert_called_once_with(["sentinel"], chpp, fetch_enhanced=False)

    @patch("app.opponents._process_matches_enhanced")
    @patch("app.db")
    def test_failing_opponent_does_not_stop_others(self, mock_db, mock_process):
        upcoming = [
            make_match(OUR_ID, 3, None, None, datetime(2099, 1, 1)),
            make_match(OUR_ID, 4, None, None, datetime(2099, 1, 8)),
        ]
        mock_db.session.query.return_value.filter.return_value.all.return_value = (
            upcoming
        )
        chpp = Mock()
        chpp.matches.side_effect = [RuntimeError("boom"), ["ok"]]

        refresh_opponent_matches(chpp, [OUR_ID])

        assert chpp.matches.call_count == 2
        mock_process.assert_called_once_with(["ok"], chpp, fetch_enhanced=False)

    @patch("app.opponents._process_matches_enhanced")
    @patch("app.db")
    def test_skips_unknown_opponent_ids(self, mock_db, mock_process):
        upcoming = [make_match(OUR_ID, 0, None, None, datetime(2099, 1, 1))]
        mock_db.session.query.return_value.filter.return_value.all.return_value = (
            upcoming
        )
        chpp = Mock()

        refresh_opponent_matches(chpp, [OUR_ID])

        chpp.matches.assert_not_called()


def make_setup_match(when, matchtype, formation, tactic_type, team_side="home"):
    """A finished match where OUR_ID plays THEIR_ID, with setup stored on OUR_ID's side."""
    if team_side == "home":
        match = make_match(OUR_ID, THEIR_ID, 1, 0, when, matchtype=matchtype)
        match.home_team_formation = formation
        match.home_team_tactic_type = tactic_type
    else:
        match = make_match(THEIR_ID, OUR_ID, 0, 1, when, matchtype=matchtype)
        match.away_team_formation = formation
        match.away_team_tactic_type = tactic_type
    return match


class TestDefaultSetup:
    def test_scouting_defaults_to_all_regardless_of_match_type(self):
        from app.opponents import scouting_for

        now = datetime(2030, 1, 1)
        league = make_match(OUR_ID, THEIR_ID, None, None, now, status=None, matchtype=1)
        cup = make_match(OUR_ID, THEIR_ID, None, None, now, status=None, matchtype=3)

        with patch("app.opponents._past_matches", return_value=[]):
            assert scouting_for(league, OUR_ID, now)["setup_default"] == "all"
            assert scouting_for(cup, OUR_ID, now)["setup_default"] == "all"


class TestSetupSummary:
    def setup_method(self):
        self.matches = [
            make_setup_match(datetime(2024, 1, 1), 1, "4-4-2", 1),
            make_setup_match(datetime(2024, 2, 1), 3, "5-3-2", 2, team_side="away"),
            make_setup_match(datetime(2024, 3, 1), 1, "4-4-2", 1, team_side="away"),
            make_setup_match(datetime(2024, 4, 1), 2, "3-5-2", 8),
        ]

    def test_league_only_keeps_league_matches(self):
        result = setup_summary(self.matches, OUR_ID, "league")

        assert len(result["matches"]) == 2
        assert result["formations"] == [("4-4-2", 2, 100)]
        assert result["tactics"] == [(1, 2, 100)]

    def test_cup_only_keeps_cup_matches(self):
        result = setup_summary(self.matches, OUR_ID, "cup")

        assert len(result["matches"]) == 1
        assert result["formations"] == [("5-3-2", 1, 100)]
        assert result["tactics"] == [(2, 1, 100)]

    def test_all_keeps_every_match_type(self):
        result = setup_summary(self.matches, OUR_ID, "all")

        assert len(result["matches"]) == 4
        assert result["formations"][0] == ("4-4-2", 2, 50)
        assert {f[0] for f in result["formations"][1:]} == {"5-3-2", "3-5-2"}
        assert result["record"]["all"] == {"W": 4, "D": 0, "L": 0}

    def test_caps_at_ten_most_recent_matches(self):
        many = [
            make_setup_match(datetime(2024, 1, 1 + i), 1, f"f{i}", 1) for i in range(12)
        ]
        result = setup_summary(many, OUR_ID, "league")

        assert len(result["matches"]) == 10
        assert result["matches"][0]["date"] == datetime(2024, 1, 12)

    def test_not_stored_setup_is_an_unknown_share(self):
        matches = [
            make_setup_match(datetime(2024, 1, 1), 1, None, None),
            make_setup_match(datetime(2024, 1, 2), 1, "", 1),
            make_setup_match(datetime(2024, 1, 3), 1, "4-4-2", 1),
            make_setup_match(datetime(2024, 1, 4), 1, "4-4-2", 1),
        ]
        result = setup_summary(matches, OUR_ID, "league")

        assert result["formations"] == [("4-4-2", 2, 50), (None, 2, 50)]
        assert result["tactics"] == [(1, 3, 75), (None, 1, 25)]

    def test_normal_tactic_counts_as_a_tactic(self):
        matches = [make_setup_match(datetime(2024, 1, 1), 1, "4-4-2", 0)]
        result = setup_summary(matches, OUR_ID, "league")

        assert result["tactics"] == [(0, 1, 100)]

    def test_no_matches_give_no_shares(self):
        result = setup_summary([], OUR_ID, "cup")

        assert result["formations"] == []
        assert result["tactics"] == []


class TestSaveMissingSetups:
    @patch("app.db")
    def test_writes_the_teams_own_side_from_matchdetails(self, mock_db):
        from app.opponents import _save_missing_setups

        match = make_match(THEIR_ID, OUR_ID, 0, 1, datetime(2024, 1, 1))
        details = Mock(
            home_team_formation="4-4-2",
            away_team_formation="5-3-2",
            home_team_tactic_type=1,
            away_team_tactic_type=2,
        )
        chpp = Mock()
        chpp.matchdetails.return_value = details

        _save_missing_setups(chpp, OUR_ID, [match])

        chpp.matchdetails.assert_called_once_with(id_=match.ht_id, match_events=False)
        assert match.away_team_formation == "5-3-2"
        assert match.away_team_tactic_type == 2
        assert match.home_team_formation is None
        mock_db.session.commit.assert_called_once()

    @patch("app.db")
    def test_skips_matches_that_already_have_a_formation(self, mock_db):
        from app.opponents import _save_missing_setups

        match = make_setup_match(datetime(2024, 1, 1), 1, "4-4-2", 1)
        chpp = Mock()

        _save_missing_setups(chpp, OUR_ID, [match])

        chpp.matchdetails.assert_not_called()

    @patch("app.db")
    def test_fetches_at_most_ten_newest_matches(self, mock_db):
        from app.opponents import _save_missing_setups

        matches = [
            make_match(OUR_ID, THEIR_ID, 1, 0, datetime(2024, 1, 1 + i))
            for i in range(12)
        ]
        chpp = Mock()
        chpp.matchdetails.return_value = Mock(
            home_team_formation="4-4-2", home_team_tactic_type=None
        )

        _save_missing_setups(chpp, OUR_ID, matches)

        assert chpp.matchdetails.call_count == 10

    @patch("app.db")
    def test_failed_request_is_left_for_next_update(self, mock_db):
        from app.opponents import _save_missing_setups

        match = make_match(OUR_ID, THEIR_ID, 1, 0, datetime(2024, 1, 1))
        chpp = Mock()
        chpp.matchdetails.side_effect = RuntimeError("boom")

        _save_missing_setups(chpp, OUR_ID, [match])

        assert match.home_team_formation is None
        mock_db.session.commit.assert_not_called()


class TestPruneOpponentMatches:
    """INFRA-094: Update keeps only the scouting card's matches, not every opponent match."""

    @staticmethod
    def _our_team(db_session, ht_id=OUR_ID):
        from models import Team, User

        db_session.add(User(ht_id, "HT", f"u{ht_id}", "pw", "k", "s"))
        db_session.flush()
        db_session.add(Team(ht_id=ht_id, team_name=f"Team {ht_id}", user_id=ht_id))
        db_session.flush()

    def test_keeps_owned_and_recent_opponent_matches_deletes_the_rest(self, db_session):
        self._our_team(db_session)
        now = datetime.now()

        # Upcoming match makes team 2 a current opponent (this match is ours -> kept).
        upcoming = make_match(
            OUR_ID, 2, None, None, now + timedelta(days=3), status=None
        )
        db_session.add(upcoming)

        # Opponent 2: 12 finished league matches -> only the last 10 are needed.
        opp2 = [
            make_match(2, 50, 1, 0, now - timedelta(days=40 - i)) for i in range(12)
        ]
        db_session.add_all(opp2)

        # Opponent 3 is no longer upcoming -> its scouting match is dropped entirely.
        old_opponent = make_match(3, 60, 2, 2, now - timedelta(days=5))
        db_session.add(old_opponent)

        # Our own past match against a non-user team -> owned history, kept.
        own_history = make_match(OUR_ID, 70, 3, 1, now - timedelta(days=5))
        db_session.add(own_history)
        db_session.commit()

        keep_recent = opp2[2].ht_id
        gone_old = [opp2[0].ht_id, opp2[1].ht_id, old_opponent.ht_id]
        upcoming_id, own_id = upcoming.ht_id, own_history.ht_id

        deleted = prune_opponent_matches()

        remaining = {m.ht_id for m in db_session.query(Match).all()}
        assert deleted == 3  # 2 oldest opponent-2 matches + the old opponent match
        assert all(ht_id not in remaining for ht_id in gone_old)
        assert keep_recent in remaining
        assert upcoming_id in remaining
        assert own_id in remaining

    def test_no_upcoming_opponents_removes_all_scouting_only_matches(self, db_session):
        self._our_team(db_session)
        now = datetime.now()

        own_history = make_match(OUR_ID, 70, 1, 0, now - timedelta(days=5))
        scouting_only = make_match(2, 50, 1, 0, now - timedelta(days=5))
        db_session.add_all([own_history, scouting_only])
        db_session.commit()

        own_id, scouting_id = own_history.ht_id, scouting_only.ht_id

        deleted = prune_opponent_matches()

        remaining = {m.ht_id for m in db_session.query(Match).all()}
        assert deleted == 1
        assert scouting_id not in remaining
        assert own_id in remaining
