"""FEAT-042: the admin overview of measured training speed across all users."""

import pytest

from app import training_speed_stats as stats
from app.training_rules import schum_weeks_per_level
from tests.test_training_speed import logged_season, TEAM  # noqa: F401 (fixture)

PLAYMAKING, DEFENDING = 8, 3


def _pop(weeks, training_types=(PLAYMAKING,), age=18, intensity=100, team=1, player=1):
    return {
        "weeks": weeks,
        "training_types": list(training_types),
        "age_years": age,
        "intensity": intensity,
        "stamina_share": 10,
        "from": 7,
        "team_id": team,
        "player_id": player,
    }


@pytest.mark.parametrize(
    ("age", "band"),
    [(17, "17-18"), (18, "17-18"), (20, "19-20"), (23, "21-23"), (30, "24+")],
)
def test_age_band(age, band):
    assert stats.age_band(age) == band


@pytest.mark.parametrize(
    ("value", "band"), [(100, "100%"), (95, "90-99%"), (80, "<90%")]
)
def test_intensity_band(value, band):
    assert stats.intensity_band(value) == band


def test_summarize_gives_a_95_percent_interval():
    result = stats.summarize([4.0, 5.0, 6.0])
    # mean 5, sd 1, t(2) = 4.30: 5 ± 4.30 / sqrt(3)
    assert result["mean"] == 5.0
    assert result["ci_low"] == pytest.approx(5 - 4.30 / 3**0.5)
    assert (result["min"], result["max"], result["n"]) == (4.0, 6.0, 3)


def test_summarize_one_value_has_no_interval():
    assert stats.summarize([4.0])["ci_low"] is None


def test_overview_groups_and_compares_with_schum():
    pops = [
        _pop(4.0, player=1),
        _pop(6.0, player=2, team=2),
        _pop(5.0, age=22),
        _pop(3.0, training_types=(PLAYMAKING, DEFENDING)),  # mixed: left out
    ]
    result = stats.overview(pops)

    assert (result["total"], result["mixed"]) == (4, 1)
    first = result["rows"][0]
    assert (first["age_band"], first["n"], first["players"], first["teams"]) == (
        "17-18",
        2,
        2,
        2,
    )
    assert first["few"] is True
    expected = schum_weeks_per_level(PLAYMAKING, 7, 18, 100, 10)
    assert first["expected"] == pytest.approx(expected)
    assert first["ratio"] == pytest.approx(5.0 / expected)
    assert [r["age_band"] for r in result["rows"]] == ["17-18", "21-23"]


def test_schum_reference_is_in_the_wiki_ballpark():
    # Wiki: about 4 weeks for a 17-year-old playmaker, solid to excellent, with
    # 2 top assistants and 15% stamina
    weeks = schum_weeks_per_level(PLAYMAKING, 7, 17, 100, 15, assistants=10)
    assert 3.5 < weeks < 5


@pytest.mark.usefixtures("logged_season")
def test_measured_pops_pools_every_team(app_with_routes):
    with app_with_routes.app_context():
        pops = stats.measured_pops()
    assert sorted(p["weeks"] for p in pops) == [3.0, 3.0]
    assert {p["team_id"] for p in pops} == {TEAM}


def test_debug_page_shows_the_section(app_with_routes, db_session):
    from tests.test_main import _client

    html = (
        _client(app_with_routes, db_session, admin=True)
        .get("/debug")
        .get_data(as_text=True)
    )
    assert 'id="training-speed"' in html
    assert "No measured skill-ups yet" in html
