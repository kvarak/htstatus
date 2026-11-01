"""Training speed overview for admins (FEAT-042): what all users' measured pops say.

Pools FEAT-037's measured intervals over every team with a training log and
groups them by training type, age band and intensity band. Only intervals
with a single training type are used. Each pop is compared with Schum's
formula (``schum_weeks_per_level``) assuming a solid coach and no assistants,
because coach level and assistants aren't fetched yet (StaffList).

Aggregates only: no player or team names leave this module. Database only.
"""

import math
from statistics import mean, stdev

from app.training_rules import schum_weeks_per_level
from app.training_speed import measure_team, MEASURED

AGE_BANDS = ((17, 18), (19, 20), (21, 23), (24, 99))
FEW_POPS = 5  # rows with fewer pops are shown but marked as unreliable
# Two-sided 95% t values by degrees of freedom (1.96 beyond the table)
_T95 = {
    1: 12.71,
    2: 4.30,
    3: 3.18,
    4: 2.78,
    5: 2.57,
    6: 2.45,
    7: 2.36,
    8: 2.31,
    9: 2.26,
    10: 2.23,
    12: 2.18,
    15: 2.13,
    20: 2.09,
    25: 2.06,
    30: 2.04,
}
SNAPSHOT_MARGIN_DAYS = 14  # snapshots this long before the first logged week


def age_band(age):
    for low, high in AGE_BANDS:
        if low <= age <= high:
            return f"{low}+" if high == 99 else f"{low}-{high}"
    return "<17"


def intensity_band(intensity):
    if intensity is None:
        return "?"
    if intensity >= 100:
        return "100%"
    if intensity >= 90:
        return "90-99%"
    return "<90%"


def t95(df):
    if df <= 0:
        return None
    for limit in sorted(_T95):
        if df <= limit:
            return _T95[limit]
    return 1.96


def summarize(values):
    """n, mean, 95% confidence interval of the mean, min and max."""
    n = len(values)
    avg = mean(values)
    low = high = None
    if n >= 2:
        margin = t95(n - 1) * stdev(values) / math.sqrt(n)
        low, high = avg - margin, avg + margin
    return {
        "n": n,
        "mean": avg,
        "ci_low": low,
        "ci_high": high,
        "min": min(values),
        "max": max(values),
    }


def measured_pops():
    """Every measured single-type pop of every team with a training log."""
    from datetime import datetime, time, timedelta

    from sqlalchemy import func

    from app import db
    from models import Players, TrainingWeek

    first_week = dict(
        db.session.query(TrainingWeek.team_id, func.min(TrainingWeek.training_date))
        .group_by(TrainingWeek.team_id)
        .all()
    )
    pops = []
    for team_id, first in first_week.items():
        since = datetime.combine(first - timedelta(days=SNAPSHOT_MARGIN_DAYS), time.min)
        snapshots = {}
        for record in (
            Players.query.filter(Players.owner == team_id, Players.data_date >= since)
            .order_by(Players.data_date)
            .all()
        ):
            snapshots.setdefault(record.ht_id, []).append(record)
        for player_id, skills in measure_team(team_id, snapshots).items():
            for skill in skills.values():
                for pop in skill["pops"]:
                    if pop["status"] == MEASURED:
                        pops.append({**pop, "team_id": team_id, "player_id": player_id})
    return pops


def overview(pops):
    """Rows per training type × age band × intensity band, plus what was left out."""
    groups = {}
    mixed = 0
    for pop in pops:
        if len(pop["training_types"]) != 1:
            mixed += 1
            continue
        training_type = pop["training_types"][0]
        key = (
            training_type,
            age_band(pop["age_years"]),
            intensity_band(pop["intensity"]),
        )
        groups.setdefault(key, []).append(pop)

    rows = []
    for (training_type, age, intensity), group in sorted(groups.items()):
        weeks = [p["weeks"] for p in group]
        expected = [
            schum_weeks_per_level(
                training_type,
                p["from"],
                p["age_years"],
                p["intensity"],
                p["stamina_share"],
            )
            for p in group
        ]
        ratios = [w / e for w, e in zip(weeks, expected, strict=True) if e]
        rows.append(
            {
                "training_type": training_type,
                "age_band": age,
                "intensity_band": intensity,
                "players": len({(p["team_id"], p["player_id"]) for p in group}),
                "teams": len({p["team_id"] for p in group}),
                "few": len(group) < FEW_POPS,
                "expected": mean([e for e in expected if e]) if any(expected) else None,
                "ratio": mean(ratios) if ratios else None,
                **summarize(weeks),
            }
        )
    return {"rows": rows, "mixed": mixed, "total": len(pops)}
