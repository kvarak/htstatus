"""Squad statistics for the stats page, computed from the latest Players records."""

from collections import Counter

from app.hattrick_countries import get_country_info
from app.utils import best_position

SKILLS = (
    "keeper",
    "defender",
    "playmaker",
    "winger",
    "passing",
    "scorer",
    "set_pieces",
    "leadership",
)

# (Hattrick MatchPositions term, English fallback, best_position codes)
POSITION_GROUPS = (
    ("Keeper", "Goalkeepers", ("GC",)),
    ("CentralDefender", "Defenders", ("CD", "CDO", "CDTW")),
    ("WingBack", "Wing Defenders", ("WBD", "WBN", "WBO", "WBTM")),
    ("InnerMidfield", "Midfielders", ("IMN", "IMD", "IMO", "IMTW")),
    ("Winger", "Wingers", ("WO", "WTM", "WN", "WD")),
    ("Forward", "Forwards", ("FW", "FTW", "DF")),
)

MIN_AGE = 16


def _n(player, attr):
    return getattr(player, attr, None) or 0


def team_statistics(players):
    """Averages and totals shown in the stats cards; {} for an empty squad."""
    if not players:
        return {}
    count = len(players)

    def average(attr, digits=1):
        return round(sum(_n(p, attr) for p in players) / count, digits)

    goals = sum(_n(p, "current_team_goals") for p in players)
    matches = sum(_n(p, "current_team_matches") for p in players)
    return {
        "total_players": count,
        "avg_age": average("age_years"),
        "avg_tsi": average("tsi", 0),
        "avg_wage": average("salary", 0),
        "total_career_goals": sum(_n(p, "career_goals") for p in players),
        "total_matches": matches,
        "goals_per_match": round(goals / matches, 1) if matches else 0,
        "skill_averages": {skill: average(skill) for skill in SKILLS},
    }


def top_scorers(players, limit=10):
    """Players by goals per match for the club (players without matches last)."""

    def ratio(p):
        matches = _n(p, "current_team_matches")
        return (matches > 0, _n(p, "current_team_goals") / matches if matches else 0)

    return sorted(players, key=ratio, reverse=True)[:limit]


def top_by_tsi(players, limit=10):
    """Players with a TSI, highest first."""
    rated = [p for p in players if _n(p, "tsi") > 0]
    return sorted(rated, key=lambda p: p.tsi, reverse=True)[:limit]


def squad_composition(players):
    """[(term, english, count)] of players per best-position group."""
    group_of = {code: term for term, _, codes in POSITION_GROUPS for code in codes}
    counts = Counter(group_of.get(best_position(p)) for p in players)
    return [(term, english, counts[term]) for term, english, _ in POSITION_GROUPS]


def age_groups(players):
    """[(label, count)] of youth (≤21), prime (22-28) and veterans (29+)."""
    ages = [p.age_years for p in players if p.age_years is not None]
    return [
        ("Youth (≤21)", sum(a <= 21 for a in ages)),
        ("Prime (22-28)", sum(22 <= a <= 28 for a in ages)),
        ("Veterans (29+)", sum(a >= 29 for a in ages)),
    ]


def age_distributions(all_players, subset):
    """[(age, count)] for both lists over the same age range (players ≥ 16)."""
    ages = [_n(p, "age_years") for p in all_players]
    ages = [a for a in ages if a >= MIN_AGE]
    if not ages:
        return [], []
    span = range(min(ages), max(ages) + 1)
    all_counts = Counter(ages)
    sub_counts = Counter(_n(p, "age_years") for p in subset)
    return (
        [(age, all_counts[age]) for age in span],
        [(age, sub_counts[age]) for age in span],
    )


def country_distribution(players):
    """[(flag + name, count, flag color)], most common first."""
    counts, colors = Counter(), {}
    for p in players:
        info = get_country_info(getattr(p, "native_country_id", None))
        label = f"{info['flag']} {info['name']}"
        counts[label] += 1
        colors[label] = info["color"]
    return [(label, n, colors[label]) for label, n in counts.most_common()]
