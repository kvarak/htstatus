"""Tests for app/team_stats.py (stats page numbers)."""

from types import SimpleNamespace

from app import team_stats as ts


def _player(**fields):
    base = {
        "age_years": 25,
        "tsi": 1000,
        "salary": 5000,
        "career_goals": 0,
        "current_team_goals": 0,
        "current_team_matches": 0,
        "native_country_id": 1,
        "keeper": 0,
        "defender": 0,
        "playmaker": 0,
        "winger": 0,
        "passing": 0,
        "scorer": 0,
        "set_pieces": 0,
        "leadership": 0,
    }
    base.update(fields)
    return SimpleNamespace(**base)


def test_team_statistics_empty():
    assert ts.team_statistics([]) == {}


def test_team_statistics_averages_and_totals():
    players = [
        _player(
            age_years=20,
            tsi=1000,
            salary=1000,
            keeper=6,
            current_team_goals=3,
            current_team_matches=4,
            career_goals=10,
        ),
        _player(
            age_years=30,
            tsi=3000,
            salary=3000,
            keeper=None,
            current_team_goals=1,
            current_team_matches=4,
            career_goals=5,
        ),
    ]
    stats = ts.team_statistics(players)
    assert stats["total_players"] == 2
    assert stats["avg_age"] == 25
    assert stats["avg_tsi"] == 2000
    assert stats["avg_wage"] == 2000
    assert stats["total_career_goals"] == 15
    assert stats["total_matches"] == 8
    assert stats["goals_per_match"] == 0.5
    assert stats["skill_averages"]["keeper"] == 3


def test_top_scorers_by_ratio_without_matches_last():
    benched = _player(current_team_goals=0, current_team_matches=0, career_goals=99)
    sharp = _player(current_team_goals=4, current_team_matches=4)
    steady = _player(current_team_goals=5, current_team_matches=10)
    assert ts.top_scorers([benched, steady, sharp]) == [sharp, steady, benched]


def test_top_by_tsi_skips_players_without_tsi():
    low, high, none = _player(tsi=10), _player(tsi=900), _player(tsi=None)
    assert ts.top_by_tsi([low, none, high], limit=5) == [high, low]


def test_squad_composition_uses_best_position():
    keeper = _player(keeper=10)
    scorer = _player(scorer=12)
    empty = _player()
    composition = ts.squad_composition([keeper, scorer, empty])
    counts = {term: count for term, _, count in composition}
    assert counts["Keeper"] == 1
    assert counts["Forward"] == 1
    assert sum(counts.values()) == 2


def test_age_groups():
    players = [_player(age_years=a) for a in (17, 21, 22, 28, 29, None)]
    assert [count for _, count in ts.age_groups(players)] == [2, 2, 1]


def test_age_distributions_share_range():
    everyone = [_player(age_years=18), _player(age_years=21)]
    all_ages, subset = ts.age_distributions(everyone, everyone[1:])
    assert all_ages == [(18, 1), (19, 0), (20, 0), (21, 1)]
    assert subset == [(18, 0), (19, 0), (20, 0), (21, 1)]


def test_country_distribution_most_common_first():
    rows = ts.country_distribution(
        [
            _player(native_country_id=1),
            _player(native_country_id=2),
            _player(native_country_id=2),
        ]
    )
    assert [count for _, count, _ in rows] == [2, 1]
    assert all(color for _, _, color in rows)
