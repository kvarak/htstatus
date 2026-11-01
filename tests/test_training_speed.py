"""FEAT-037: measured training speed from player snapshots, the training log and minutes."""

from datetime import date, datetime, timedelta
from types import SimpleNamespace

import pytest

from app import training_speed
from app.training_speed import (
    find_pops,
    INCOMPLETE,
    measure_player,
    MEASURED,
    UNKNOWN_START,
    UNKNOWN_WEEK,
)
from tests.factories import make_player_record, setup_authenticated_session

TEAM = 12345
PLAYER = 601
PLAYMAKING, DEFENDING = 8, 3
THU = date(2026, 10, 1)  # a Thursday


def _snap(day, playmaker, defender=5, age=18):
    return SimpleNamespace(
        data_date=datetime.combine(day, datetime.min.time()),
        playmaker=playmaker,
        defender=defender,
        age_years=age,
        age_days=10,
        keeper=1,
        winger=1,
        passing=1,
        scorer=1,
        set_pieces=1,
    )


def _week(n):
    return THU + timedelta(weeks=n)


def test_find_pops_knows_the_week_only_with_one_training_in_between():
    snaps = [
        _snap(_week(0) + timedelta(days=1), 6),  # Friday
        _snap(_week(1) + timedelta(days=1), 7),  # a week later: one Thursday
        _snap(_week(3) + timedelta(days=1), 8),  # two weeks later: two Thursdays
    ]
    pops = find_pops(snaps, "playmaker")

    assert [(p["from"], p["to"], p["week"]) for p in pops] == [
        (6, 7, _week(1)),
        (7, 8, None),
    ]
    assert pops[0]["after_reset"] is True
    assert pops[1]["after_reset"] is False


def test_thursday_snapshot_is_before_that_nights_training():
    snaps = [_snap(_week(0), 6), _snap(_week(1), 7)]  # both on Thursdays
    assert find_pops(snaps, "playmaker")[0]["week"] == _week(0)


def test_a_drop_or_double_jump_resets_the_chain():
    snaps = [
        _snap(_week(0) + timedelta(days=1), 6),
        _snap(_week(1) + timedelta(days=1), 5),  # drop
        _snap(_week(2) + timedelta(days=1), 6),
    ]
    assert find_pops(snaps, "playmaker")[0]["after_reset"] is True


class _Data:
    """Stand-in for WeekData: every week logged, the player trains a fixed share."""

    def __init__(self, share=1.0, training_type=PLAYMAKING, missing=()):
        self.share, self.training_type, self.missing = share, training_type, missing

    def interval(self, player_id, skill, after, until):
        weeks = (until - after).days // 7
        if any(after < m <= until for m in self.missing):
            return None
        trains = self.training_type in training_speed.SKILL_TRAINING_TYPES[skill]
        return {
            "weeks": weeks * self.share if trains else 0.0,
            "training_types": [self.training_type] if trains else [],
            "intensity": 100,
            "stamina_share": 10,
        }

    def last_week(self):
        return _week(12)


def _weekly_pops(levels):
    """Weekly snapshots (Fridays) with the given playmaking levels."""
    return [_snap(_week(n) + timedelta(days=1), lvl) for n, lvl in enumerate(levels)]


def test_measure_player_counts_effective_weeks_between_pops():
    # pops seen in weeks 1, 5 and 9: 4 trained weeks each, at 75% training
    snaps = _weekly_pops([6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9])
    result = measure_player(snaps, _Data(share=0.75), PLAYER)["playmaker"]

    assert [p["status"] for p in result["pops"]] == [UNKNOWN_START, MEASURED, MEASURED]
    assert [p["weeks"] for p in result["pops"][1:]] == [3.0, 3.0]
    assert result["per_level"] == 3.0
    # last pop in week 9, last training week 12: 3 weeks at 75% = 2.25 done
    assert result["next_in"] == pytest.approx(0.75)


def test_measure_player_marks_gaps_incomplete():
    snaps = _weekly_pops([6, 7, 7, 7, 7, 8])
    result = measure_player(snaps, _Data(missing=[_week(3)]), PLAYER)["playmaker"]

    assert result["pops"][1]["status"] == INCOMPLETE
    assert result["per_level"] is None


def test_unknown_pop_week():
    snaps = [
        _snap(_week(0) + timedelta(days=1), 6),
        _snap(_week(2) + timedelta(days=1), 7),
    ]
    pop = measure_player(snaps, _Data(), PLAYER)["playmaker"]["pops"][0]
    assert pop["status"] == UNKNOWN_WEEK


@pytest.fixture
def logged_season(db_session):
    """Weeks 1-8 of playmaking, all logged; PLAYER plays 90' inner midfield each week."""
    from models import Match, MatchPositionMinutes, TrainingWeek

    for n in range(1, 9):
        db_session.add(
            TrainingWeek(
                team_id=TEAM,
                training_date=_week(n),
                training_type=PLAYMAKING,
                intensity=100,
                stamina_share=10,
                planned=False,
            )
        )
        match_id = 9000 + n
        db_session.add(
            Match(
                {
                    "ht_id": match_id,
                    "home_team_id": TEAM,
                    "home_team_name": "Us",
                    "away_team_id": 1,
                    "away_team_name": "Them",
                    "datetime": datetime.combine(
                        _week(n) - timedelta(days=4), datetime.min.time()
                    ),
                    "matchtype": 1,
                    "context_id": 0,
                    "rule_id": 0,
                    "cup_level": 0,
                    "cup_level_index": 0,
                    "home_goals": 1,
                    "away_goals": 0,
                }
            )
        )
        db_session.add(
            MatchPositionMinutes(
                match_id=match_id,
                team_id=TEAM,
                player_id=PLAYER,
                role_id=107,
                minutes=90,
            )
        )
    # Pops seen the Friday after weeks 1, 4 and 7
    for n, level in [(0, 6), (1, 7), (2, 7), (3, 7), (4, 8), (5, 8), (6, 8), (7, 9)]:
        record = make_player_record(PLAYER, TEAM, "Pim", "Maker")
        record.data_date = datetime.combine(
            _week(n) + timedelta(days=1), datetime.min.time()
        )
        record.playmaker = level
        db_session.add(record)
    db_session.commit()


@pytest.mark.usefixtures("logged_season")
def test_measure_team_from_the_database(app_with_routes):
    from models import Players

    with app_with_routes.app_context():
        snaps = (
            Players.query.filter_by(ht_id=PLAYER, owner=TEAM)
            .order_by(Players.data_date)
            .all()
        )
        result = training_speed.measure_team(TEAM, {PLAYER: snaps})[PLAYER]["playmaker"]

    assert [p["weeks"] for p in result["pops"]] == [None, 3.0, 3.0]
    assert result["pops"][1]["training_types"] == [PLAYMAKING]
    assert result["per_level"] == 3.0
    assert result["next_in"] == pytest.approx(2.0)  # 1 trained week since the last pop


@pytest.mark.usefixtures("logged_season")
def test_a_match_without_lineup_makes_the_interval_incomplete(
    app_with_routes, db_session
):
    from models import MatchPositionMinutes, Players

    MatchPositionMinutes.query.filter_by(match_id=9003).delete()
    db_session.commit()
    with app_with_routes.app_context():
        snaps = Players.query.filter_by(ht_id=PLAYER).order_by(Players.data_date).all()
        pops = training_speed.measure_team(TEAM, {PLAYER: snaps})[PLAYER]["playmaker"][
            "pops"
        ]

    assert [p["status"] for p in pops] == [UNKNOWN_START, INCOMPLETE, MEASURED]


@pytest.mark.usefixtures("logged_season")
def test_training_page_shows_measured_speed(app_with_routes, db_session):
    from tests.conftest import create_test_user

    user = create_test_user(db_session)
    client = setup_authenticated_session(app_with_routes.test_client(), user)

    html = client.get(f"/training?id={TEAM}").get_data(as_text=True)

    assert "3.0 wk" in html  # in the Training History
    assert "≈3.0 wk/level" in html  # in Current Skills
