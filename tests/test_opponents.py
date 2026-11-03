"""Tests for app/opponents.py (FEAT-008 scouting)."""

from datetime import datetime
from unittest.mock import Mock, patch

from app.opponents import (
    default_setup,
    opponent_of,
    refresh_opponent_matches,
    setup_summary,
    summarise,
    tactic_label,
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
    def test_league_match_defaults_to_league(self):
        assert default_setup(1) == "league"

    def test_cup_match_defaults_to_cup(self):
        assert default_setup(3) == "cup"

    def test_other_match_types_default_to_all(self):
        assert default_setup(2) == "all"
        assert default_setup(None) == "all"


class TestTacticLabel:
    def test_known_and_unknown_types(self):
        assert tactic_label(1) == "Pressing"
        assert tactic_label(5) == "Tactic 5"

    def test_missing_type_is_none(self):
        assert tactic_label(None) is None

    def test_zero_is_normal(self):
        assert tactic_label(0) == "Normal"

    def test_creative_and_longshots_follow_chpp(self):
        assert tactic_label(7) == "Creative"
        assert tactic_label(8) == "Longshots"


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
        assert result["tactics"] == [("Pressing", 2, 100)]

    def test_cup_only_keeps_cup_matches(self):
        result = setup_summary(self.matches, OUR_ID, "cup")

        assert len(result["matches"]) == 1
        assert result["formations"] == [("5-3-2", 1, 100)]
        assert result["tactics"] == [("Counter-Attack", 1, 100)]

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
        assert result["tactics"] == [("Pressing", 3, 75), (None, 1, 25)]

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
