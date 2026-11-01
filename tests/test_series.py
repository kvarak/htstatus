"""Tests for FEAT-030: the series page (app/series.py, /series)."""

from unittest.mock import MagicMock
import xml.etree.ElementTree as ET

from app import series
from app.chpp.parsers import parse_leaguedetails, parse_leaguefixtures

US = 9838

DETAILS_XML = """<HattrickData>
  <LeagueID>1</LeagueID><LeagueName>Sverige</LeagueName>
  <LeagueLevel>4</LeagueLevel><MaxLevel>8</MaxLevel>
  <LeagueLevelUnitID>288</LeagueLevelUnitID><LeagueLevelUnitName>IV.203</LeagueLevelUnitName>
  <CurrentMatchRound>3</CurrentMatchRound>
  <Team><UserId>1</UserId><TeamID>2</TeamID><Position>2</Position><PositionChange>-1</PositionChange>
    <TeamName>Rivals FC</TeamName><Matches>2</Matches><GoalsFor>4</GoalsFor><GoalsAgainst>2</GoalsAgainst>
    <Points>4</Points><Won>1</Won><Draws>1</Draws><Lost>0</Lost></Team>
  <Team><UserId>182085</UserId><TeamID>9838</TeamID><Position>1</Position><PositionChange>1</PositionChange>
    <TeamName>Dalby Stenbrotters FC</TeamName><Matches>2</Matches><GoalsFor>5</GoalsFor><GoalsAgainst>1</GoalsAgainst>
    <Points>6</Points><Won>2</Won><Draws>0</Draws><Lost>0</Lost></Team>
</HattrickData>"""

FIXTURES_XML = """<HattrickData>
  <LeagueLevelUnitID>288</LeagueLevelUnitID><LeagueLevelUnitName>IV.203</LeagueLevelUnitName>
  <Season>92</Season>
  <Match><MatchID>11</MatchID><MatchRound>1</MatchRound>
    <HomeTeam><HomeTeamID>9838</HomeTeamID><HomeTeamName>Dalby Stenbrotters FC</HomeTeamName></HomeTeam>
    <AwayTeam><AwayTeamID>2</AwayTeamID><AwayTeamName>Rivals FC</AwayTeamName></AwayTeam>
    <MatchDate>2026-10-10 20:00:00</MatchDate><HomeGoals>2</HomeGoals><AwayGoals>1</AwayGoals></Match>
  <Match><MatchID>21</MatchID><MatchRound>3</MatchRound>
    <HomeTeam><HomeTeamID>2</HomeTeamID><HomeTeamName>Rivals FC</HomeTeamName></HomeTeam>
    <AwayTeam><AwayTeamID>9838</AwayTeamID><AwayTeamName>Dalby Stenbrotters FC</AwayTeamName></AwayTeam>
    <MatchDate>2026-11-07 20:00:00</MatchDate></Match>
</HattrickData>"""


def _team(team_id, position, points, name=None):
    return {
        "team_id": team_id,
        "team_name": name or f"Team {team_id}",
        "user_id": 0,
        "position": position,
        "position_change": 0,
        "matches": 4,
        "won": 0,
        "draws": 0,
        "lost": 0,
        "goals_for": 6,
        "goals_against": 4,
        "points": points,
    }


def _match(match_id, rnd, home, away, home_goals=None, away_goals=None):
    return {
        "match_id": match_id,
        "round": rnd,
        "date": f"2026-11-{rnd:02d} 20:00:00",
        "home_id": home,
        "home_name": f"Team {home}",
        "away_id": away,
        "away_name": f"Team {away}",
        "home_goals": home_goals,
        "away_goals": away_goals,
    }


def _series_data(level=4, max_level=8):
    """8-team series: we (1) are 3rd on 7 points; only teams 4 and 3 are within 3."""
    points = {2: 11, 4: 8, 1: 7, 3: 5, 5: 3, 6: 2, 7: 1, 8: 0}
    teams = [
        _team(tid, pos, points[tid])
        for pos, tid in enumerate(sorted(points, key=points.get, reverse=True), 1)
    ]
    matches = [
        _match(1, 1, 1, 2, 1, 1),
        _match(2, 2, 3, 1, 0, 2),
        _match(3, 3, 1, 4, 0, 1),
        _match(4, 4, 1, 3),  # our next match
        _match(5, 4, 5, 6),
        _match(6, 4, 2, 4),
        _match(7, 5, 6, 1),
    ]
    return {
        "details": {
            "league_name": "Sverige",
            "league_level": level,
            "max_level": max_level,
            "unit_id": 288,
            "unit_name": "IV.203",
            "current_round": 4,
            "teams": teams,
        },
        "fixtures": {"season": 92, "matches": matches},
        "fetched": "2026-11-01 06:00",
    }


class TestParsers:
    def test_parse_leaguedetails(self):
        details = parse_leaguedetails(ET.fromstring(DETAILS_XML))
        assert details["unit_name"] == "IV.203"
        assert (details["league_level"], details["max_level"]) == (4, 8)
        assert details["current_round"] == 3
        assert [t["team_id"] for t in details["teams"]] == [9838, 2]  # by position
        assert details["teams"][0]["points"] == 6
        assert details["teams"][1]["position_change"] == -1

    def test_parse_leaguefixtures_marks_unplayed(self):
        fixtures = parse_leaguefixtures(ET.fromstring(FIXTURES_XML))
        assert fixtures["season"] == 92
        played, upcoming = fixtures["matches"]
        assert (played["home_goals"], played["away_goals"]) == (2, 1)
        assert upcoming["home_goals"] is None and upcoming["away_goals"] is None
        assert upcoming["home_name"] == "Rivals FC" and upcoming["round"] == 3


class TestForm:
    def test_form_from_our_point_of_view(self):
        matches = _series_data()["fixtures"]["matches"]
        assert series.form(matches, 1) == ["D", "W", "L"]
        assert series.form(matches, 3) == ["L"]
        assert series.form(matches, 8) == []


class TestBuildView:
    def test_table_next_round_and_opponent(self):
        view = series.build_view(_series_data(), 1)

        assert [r["position"] for r in view["table"]] == list(range(1, 9))
        us = view["us"]
        assert us["is_us"] and us["position"] == 3
        assert "zone" not in us  # no guessed promotion/relegation rules

        assert view["next_round"] == 4
        assert len(view["next_round_matches"]) == 3
        ours = [m for m in view["next_round_matches"] if m["is_ours"]]
        assert len(ours) == 1 and ours[0]["away_position"] == 4
        # Team 4 (8 pts) and team 3 (5 pts) are within 3 points of our 7
        key = {m["match_id"] for m in view["next_round_matches"] if m["is_key"]}
        assert key == {4, 6}

        opp = view["next_opponent"]
        assert opp["opponent_id"] == 3 and opp["venue"] == "home"
        assert opp["row"]["position"] == 4
        assert [e["result"] for e in opp["earlier_results"]] == ["W"]
        assert [f["round"] for f in view["our_remaining"]] == [4, 5]
        assert view["our_remaining"][1]["venue"] == "away"

        assert view["behind_leader"] == 4

    def test_leader_is_zero_behind(self):
        view = series.build_view(_series_data(), 2)
        assert view["us"]["position"] == 1
        assert view["behind_leader"] == 0

    def test_season_finished(self):
        data = _series_data()
        for m in data["fixtures"]["matches"]:
            m["home_goals"] = m["away_goals"] = 0
        view = series.build_view(data, 1)
        assert view["next_round"] is None
        assert view["next_opponent"] is None
        assert view["our_remaining"] == []


class TestRefresh:
    def test_stores_and_loads(self, app_with_routes):
        chpp = MagicMock()
        chpp.league_details.return_value = {"teams": []}
        chpp.league_fixtures.return_value = {"matches": []}

        series.refresh(chpp, US, 288)

        chpp.league_details.assert_called_once_with(288)
        assert series.load(US)["details"] == {"teams": []}

    def test_never_raises_and_skips_without_unit(self, app_with_routes):
        chpp = MagicMock()
        chpp.league_details.side_effect = RuntimeError("CHPP down")
        series.refresh(chpp, US, 288)
        series.refresh(chpp, US, None)
        assert series.load(US) is None
        assert chpp.league_details.call_count == 1


class TestSeriesPage:
    def _client(self, app_with_routes, db_session):
        from tests.conftest import create_test_user
        from tests.factories import setup_authenticated_session

        create_test_user(db_session, user_id=US)
        db_session.commit()
        client = setup_authenticated_session(
            app_with_routes.test_client(), US, "kvarak"
        )
        with client.session_transaction() as sess:
            sess["all_teams"] = [US]
            sess["all_team_names"] = ["Dalby Stenbrotters FC"]
        return client

    def test_without_data_asks_for_update(self, app_with_routes, db_session):
        html = self._client(app_with_routes, db_session).get(f"/series?id={US}")
        html = html.get_data(as_text=True)
        assert "No series data yet" in html
        assert 'class="page-header"' in html

    def test_shows_table_round_and_opponent(self, app_with_routes, db_session):
        data = _series_data()
        for row in data["details"]["teams"]:
            if row["team_id"] == 1:
                row["team_id"] = US
        for m in data["fixtures"]["matches"]:
            m["home_id"] = US if m["home_id"] == 1 else m["home_id"]
            m["away_id"] = US if m["away_id"] == 1 else m["away_id"]
        with app_with_routes.app_context():
            from app import instance_cache

            instance_cache.write_json(series.FOLDER, US, data)

        html = self._client(app_with_routes, db_session).get(f"/series?id={US}")
        html = html.get_data(as_text=True)

        assert "Series IV.203" in html
        assert html.count("series-us") == 2  # our table row + our next-round match
        assert (
            "zone-" not in html and "elegation" not in html and "romotion" not in html
        )
        assert "Next opponent" in html and "Round 4" in html
        assert "within 3 pts" in html
        assert "Points behind the leader" in html

    def test_unknown_team(self, app_with_routes, db_session):
        html = self._client(app_with_routes, db_session).get("/series?id=1")
        assert "Wrong teamid" in html.get_data(as_text=True)

    def test_nav_links_to_series(self, app_with_routes, db_session):
        html = self._client(app_with_routes, db_session).get(f"/series?id={US}")
        assert f'href="/series?id={US}"' in html.get_data(as_text=True)
