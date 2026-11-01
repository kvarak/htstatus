"""FEAT-036: minutes in training positions, from match lineups to "who got trained"."""

from datetime import date, datetime
import xml.etree.ElementTree as ET

import pytest

from app import trainees
from app.chpp.models import CHPPMatchLineup
from app.chpp.parsers import parse_matchlineup
from app.match_minutes import position_minutes
from app.training_rules import (
    FULL,
    OSMOSIS,
    PARTIAL,
    position_effect,
    trained_minutes,
    training_share,
)
from tests.factories import make_player_record, setup_authenticated_session

TEAM = 12345
PLAYMAKING, GOALKEEPING, SHOOTING, CROSSING, STAMINA = 8, 9, 6, 5, 1

LINEUP_XML = """<HattrickData>
  <MatchID>777</MatchID>
  <HomeTeam><HomeTeamID>12345</HomeTeamID><HomeTeamName>Us</HomeTeamName></HomeTeam>
  <AwayTeam><AwayTeamID>999</AwayTeamID><AwayTeamName>Them</AwayTeamName></AwayTeam>
  <MatchType>1</MatchType>
  <Team>
    <TeamID>12345</TeamID>
    <StartingLineup>
      <Player><PlayerID>1</PlayerID><RoleID>100</RoleID><FirstName>Ann</FirstName><LastName>Keeper</LastName></Player>
      <Player><PlayerID>2</PlayerID><RoleID>107</RoleID><FirstName>Bo</FirstName><LastName>Mid</LastName></Player>
      <Player><PlayerID>3</PlayerID><RoleID>106</RoleID><FirstName>Cy</FirstName><LastName>Wing</LastName></Player>
      <Player><PlayerID>4</PlayerID><RoleID>17</RoleID></Player>
    </StartingLineup>
    <Substitutions>
      <Substitution>
        <SubjectPlayerID>2</SubjectPlayerID><ObjectPlayerID>5</ObjectPlayerID>
        <OrderType>1</OrderType><NewPositionId>107</NewPositionId><MatchMinute>60</MatchMinute>
      </Substitution>
      <Substitution>
        <SubjectPlayerID>3</SubjectPlayerID><ObjectPlayerID>3</ObjectPlayerID>
        <OrderType>1</OrderType><NewPositionId>108</NewPositionId><MatchMinute>30</MatchMinute>
      </Substitution>
    </Substitutions>
    <Lineup>
      <Player><PlayerID>1</PlayerID><RoleID>100</RoleID><FirstName>Ann</FirstName><LastName>Keeper</LastName><RatingStars>5.5</RatingStars></Player>
    </Lineup>
  </Team>
</HattrickData>"""


def _lineup(starting, orders=()):
    return CHPPMatchLineup(
        ht_id=1,
        starting_roles=starting,
        substitutions=[
            {"subject": s, "object": o, "order_type": t, "new_role": r, "minute": m}
            for (s, o, t, r, m) in orders
        ],
    )


def test_parse_matchlineup_reads_our_team():
    lineup = parse_matchlineup(ET.fromstring(LINEUP_XML))

    assert lineup.ht_id == 777
    assert lineup.team_id == TEAM
    assert lineup.starting_roles == {1: 100, 2: 107, 3: 106, 4: 17}
    assert [o["minute"] for o in lineup.substitutions] == [30, 60]  # sorted
    assert lineup.home_team_players[0].name == "Ann Keeper"
    assert lineup.home_team_players[0].rating_stars == 5.5


def test_minutes_from_parsed_lineup():
    minutes = position_minutes(parse_matchlineup(ET.fromstring(LINEUP_XML)))

    assert minutes == {
        1: {100: 90},
        2: {107: 60},
        5: {107: 30},
        3: {106: 30, 108: 60},  # moved inside at 30'
    }  # 4 is only the set pieces taker (role 17), not a field position


def test_position_swap():
    minutes = position_minutes(
        _lineup({1: 106, 2: 107}, [(1, 2, 3, 0, 45)]),
    )
    assert minutes == {1: {106: 45, 107: 45}, 2: {107: 45, 106: 45}}


def test_red_card_and_injury_end_the_match_but_a_bruise_does_not():
    minutes = position_minutes(
        _lineup({1: 107, 2: 108, 3: 109}),
        bookings=[{"player_id": 1, "booking_type": 2, "minute": 20}],
        injuries=[
            {"player_id": 2, "injury_type": 2, "minute": 70},
            {"player_id": 3, "injury_type": 1, "minute": 10},
        ],
    )
    assert minutes == {1: {107: 20}, 2: {108: 70}, 3: {109: 90}}


def test_man_marking_changes_nothing():
    minutes = position_minutes(_lineup({1: 103}, [(1, 50, 4, 0, 30)]))
    assert minutes == {1: {103: 90}}


@pytest.mark.parametrize(
    ("training", "role", "effect"),
    [
        (PLAYMAKING, 107, FULL),
        (PLAYMAKING, 106, PARTIAL),
        (PLAYMAKING, 112, OSMOSIS),
        (GOALKEEPING, 100, FULL),
        (GOALKEEPING, 103, None),
        (SHOOTING, 100, FULL),  # HO: the keeper too
        (CROSSING, 100, None),  # HO: not the keeper
        (CROSSING, 101, PARTIAL),
        (STAMINA, 107, None),  # not position based
    ],
)
def test_position_effect(training, role, effect):
    assert position_effect(training, role) == effect


def test_only_the_best_90_minutes_count():
    # 60' inner midfield + 60' winger + 30' forward in a playmaking week
    counted = trained_minutes(PLAYMAKING, {107: 60, 106: 60, 112: 30})
    assert counted == {FULL: 60, PARTIAL: 30, OSMOSIS: 0}


@pytest.mark.parametrize(
    ("training", "counted", "share"),
    [
        (PLAYMAKING, {FULL: 90, PARTIAL: 0, OSMOSIS: 0}, 1.0),
        (PLAYMAKING, {FULL: 0, PARTIAL: 90, OSMOSIS: 0}, 0.5),
        (PLAYMAKING, {FULL: 0, PARTIAL: 0, OSMOSIS: 90}, 1 / 8),  # HO: 1/8 for PM
        (3, {FULL: 0, PARTIAL: 0, OSMOSIS: 90}, 1 / 6),  # defending: default 1/6
        (PLAYMAKING, {FULL: 45, PARTIAL: 45, OSMOSIS: 0}, 0.75),
    ],
)
def test_training_share_adds_up_like_ho(training, counted, share):
    assert training_share(training, counted) == pytest.approx(share)


@pytest.mark.parametrize(
    ("day", "training_day"),
    [
        (date(2026, 10, 30), date(2026, 11, 5)),  # Friday -> next Thursday
        (date(2026, 11, 1), date(2026, 11, 5)),  # Sunday league match
        (date(2026, 11, 5), date(2026, 11, 5)),  # Thursday itself
    ],
)
def test_training_date_of(day, training_day):
    assert trainees.training_date_of(day) == training_day


def _match(ht_id, when, matchtype=1):
    from models import Match

    return Match(
        {
            "ht_id": ht_id,
            "home_team_id": TEAM,
            "home_team_name": "Test Team",
            "away_team_id": 1,
            "away_team_name": "Rivals",
            "datetime": when,
            "matchtype": matchtype,
            "context_id": 0,
            "rule_id": 0,
            "cup_level": 0,
            "cup_level_index": 0,
            "home_goals": 1,
            "away_goals": 0,
        }
    )


@pytest.fixture
def week_with_matches(db_session):
    """Playmaking on Thursday 2026-11-05: a league match, a friendly, a tournament match."""
    from models import MatchPositionMinutes, TrainingWeek

    db_session.add(
        TrainingWeek(
            team_id=TEAM,
            training_date=date(2026, 11, 5),
            training_type=PLAYMAKING,
            intensity=100,
            stamina_share=10,
            planned=True,
        )
    )
    db_session.add(_match(1, datetime(2026, 11, 1, 16, 0)))  # league
    db_session.add(_match(2, datetime(2026, 11, 4, 19, 0), matchtype=4))  # friendly
    db_session.add(_match(3, datetime(2026, 11, 3, 19, 0), matchtype=50))  # tournament
    for match_id, player, role, minutes in [
        (1, 601, 107, 90),  # full inner midfield
        (1, 602, 106, 90),  # winger: partial
        (1, 605, 112, 90),  # forward: osmosis only
        (2, 603, 108, 45),  # half a friendly in midfield
        (3, 604, 107, 90),  # tournament: doesn't count
    ]:
        db_session.add(
            MatchPositionMinutes(
                match_id=match_id,
                team_id=TEAM,
                player_id=player,
                role_id=role,
                minutes=minutes,
            )
        )
    db_session.commit()


@pytest.mark.usefixtures("week_with_matches")
def test_weekly_reports(app_with_routes):
    from models import TrainingWeek

    squad = {601: "Mid", 602: "Wing", 603: "Sub", 604: "Tourist", 605: "Striker"}
    with app_with_routes.app_context():
        week = TrainingWeek.query.filter_by(team_id=TEAM).one()
        report = trainees.weekly_reports(TEAM, [week], squad)[date(2026, 11, 5)]

    rows = {r["player_id"]: r for r in report["rows"]}
    assert (rows[601]["status"], rows[601][FULL]) == ("full", 90)
    assert (rows[602]["status"], rows[602][PARTIAL]) == ("partly", 90)
    assert (rows[603][FULL], rows[603]["needs"]) == (45, 45)
    assert [rows[p]["share"] for p in (601, 602, 603)] == [100, 50, 50]
    assert report["factors"] == {FULL: 100, PARTIAL: 50, OSMOSIS: 12}
    assert rows[604]["status"] == "none"
    assert rows[601]["positions"] == "RIM 90'"
    assert rows[605]["status"] == "minimal"
    assert (report["full"], report["partly"], report["minimal"]) == (1, 2, 1)


def test_save_position_minutes_replaces_the_match(app_with_routes, db_session):
    from types import SimpleNamespace

    from app.utils import save_position_minutes
    from models import MatchPositionMinutes

    details = SimpleNamespace(bookings=[], injuries=[])
    with app_with_routes.app_context():
        save_position_minutes(5, TEAM, _lineup({1: 107}), details)
        save_position_minutes(5, TEAM, _lineup({1: 108}), details)
        db_session.commit()
        rows = MatchPositionMinutes.query.filter_by(match_id=5).all()

    assert [(r.player_id, r.role_id, r.minutes) for r in rows] == [(1, 108, 90)]


@pytest.mark.usefixtures("week_with_matches")
def test_training_page_shows_who_got_trained(app_with_routes, db_session):
    from tests.conftest import create_test_user

    user = create_test_user(db_session)
    record = make_player_record(601, TEAM, "Bo", "Mid")
    db_session.add(record)
    db_session.commit()
    client = setup_authenticated_session(app_with_routes.test_client(), user)

    html = client.get(f"/training?id={TEAM}").get_data(as_text=True)

    assert 'id="who-got-trained"' in html
    assert "This week so far" in html
    assert "RIM 90&#39;" in html or "RIM 90'" in html
    assert "1 full" in html  # the log's Trained column
