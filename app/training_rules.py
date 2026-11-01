"""Hattrick training rules (FEAT-036 onwards): which positions each training trains.

Sources: the Hattrick wiki "Training" page and Hattrick Organizer's training types
(core/training/type/*WeeklyTraining.java), which are kept current; where they
differ (the goalkeeper in Shooting and Crossing) we follow HO. Change rules here
only with a source.
"""

import math

# Sectors use the keys of Hattrick's MatchPositions translations
KEEPER = "Keeper"
WING_BACK = "WingBack"
CENTRAL_DEFENDER = "CentralDefender"
INNER_MIDFIELD = "InnerMidfield"
WINGER = "Winger"
FORWARD = "Forward"
SECTORS = (KEEPER, WING_BACK, CENTRAL_DEFENDER, INNER_MIDFIELD, WINGER, FORWARD)

# CHPP matchRoleID of the 14 field positions
ROLE_SECTORS = {
    100: KEEPER,
    101: WING_BACK,
    102: CENTRAL_DEFENDER,
    103: CENTRAL_DEFENDER,
    104: CENTRAL_DEFENDER,
    105: WING_BACK,
    106: WINGER,
    107: INNER_MIDFIELD,
    108: INNER_MIDFIELD,
    109: INNER_MIDFIELD,
    110: WINGER,
    111: FORWARD,
    112: FORWARD,
    113: FORWARD,
}
ROLE_SHORT = {
    100: "GK",
    101: "RB",
    102: "RCD",
    103: "CD",
    104: "LCD",
    105: "LB",
    106: "RW",
    107: "RIM",
    108: "IM",
    109: "LIM",
    110: "LW",
    111: "RF",
    112: "FW",
    113: "LF",
}

# Training effect of a position, best first
FULL = "full"
PARTIAL = "partial"  # the wiki's (brackets), HO's "partly"
OSMOSIS = "osmosis"  # the wiki's ((double brackets)): a very small effect
EFFECT_ORDER = (FULL, PARTIAL, OSMOSIS)
MINUTES_PER_WEEK = 90  # a player gets at most 90 minutes of training a week

_OUTFIELD = (WING_BACK, CENTRAL_DEFENDER, INNER_MIDFIELD, WINGER, FORWARD)


def _effects(full=(), partial=(), osmosis=()):
    return (
        dict.fromkeys(full, FULL)
        | dict.fromkeys(partial, PARTIAL)
        | dict.fromkeys(osmosis, OSMOSIS)
    )


def _others(*trained):
    return tuple(s for s in SECTORS if s not in trained)


# CHPP trainingType id -> {sector: effect}; types not listed (general, stamina,
# individual) don't depend on positions
TRAINING_POSITION_EFFECTS = {
    2: _effects(full=SECTORS),  # Set pieces (+ bonus for keeper and taker, not shown)
    3: _effects(
        full=(CENTRAL_DEFENDER, WING_BACK),
        osmosis=_others(CENTRAL_DEFENDER, WING_BACK),
    ),  # Defending
    4: _effects(full=(FORWARD,), osmosis=_others(FORWARD)),  # Scoring
    5: _effects(
        full=(WINGER,),
        partial=(WING_BACK,),
        osmosis=(CENTRAL_DEFENDER, INNER_MIDFIELD, FORWARD),
    ),  # Crossing (winger): no effect for the keeper
    6: _effects(full=SECTORS),  # Shooting: everyone, keeper included
    7: _effects(
        full=(INNER_MIDFIELD, WINGER, FORWARD),
        osmosis=(KEEPER, WING_BACK, CENTRAL_DEFENDER),
    ),  # Short passes
    8: _effects(
        full=(INNER_MIDFIELD,),
        partial=(WINGER,),
        osmosis=(KEEPER, WING_BACK, CENTRAL_DEFENDER, FORWARD),
    ),  # Playmaking
    9: _effects(full=(KEEPER,)),  # Goalkeeping
    10: _effects(
        full=(WING_BACK, CENTRAL_DEFENDER, INNER_MIDFIELD, WINGER),
        osmosis=(KEEPER, FORWARD),
    ),  # Through passes
    11: _effects(
        full=(KEEPER, WING_BACK, CENTRAL_DEFENDER, INNER_MIDFIELD, WINGER),
        osmosis=(FORWARD,),
    ),  # Defensive positions
    12: _effects(
        full=(WINGER, FORWARD),
        osmosis=(KEEPER, WING_BACK, CENTRAL_DEFENDER, INNER_MIDFIELD),
    ),  # Wing attacks
}


# How much a minute counts compared to a full-training minute (HO's
# WeeklyTrainingType.calcSkillIncrement: partly 0.5, osmosisKoeff per type)
PARTIAL_FACTOR = 0.5
OSMOSIS_FACTOR = 1 / 6
OSMOSIS_FACTORS = {8: 1 / 8, 5: 1 / 8, 12: 5 / 39}  # playmaking, crossing, wing attacks


def effect_factors(training_type):
    return {
        FULL: 1.0,
        PARTIAL: PARTIAL_FACTOR,
        OSMOSIS: OSMOSIS_FACTORS.get(training_type, OSMOSIS_FACTOR),
    }


def training_share(training_type, counted):
    """The week's training as a share of a full week (0.0-1.0) from counted minutes."""
    factors = effect_factors(training_type)
    return sum(counted[e] * factors[e] for e in EFFECT_ORDER) / MINUTES_PER_WEEK


def position_effect(training_type, role_id):
    """FULL, PARTIAL, OSMOSIS or None for a field position under a training type."""
    sector = ROLE_SECTORS.get(role_id)
    return TRAINING_POSITION_EFFECTS.get(training_type, {}).get(sector)


def trained_minutes(training_type, minutes_by_role):
    """Split a week's minutes by position into training minutes per effect.

    The best 90 minutes count: full minutes first, then partial, then osmosis.
    Returns ``{FULL: m, PARTIAL: m, OSMOSIS: m}``.
    """
    played = dict.fromkeys(EFFECT_ORDER, 0)
    for role_id, minutes in minutes_by_role.items():
        effect = position_effect(training_type, role_id)
        if effect:
            played[effect] += minutes
    left = MINUTES_PER_WEEK
    counted = {}
    for effect in EFFECT_ORDER:
        counted[effect] = min(played[effect], left)
        left -= counted[effect]
    return counted


# Schum's formula, as used by Hattrick Organizer (WeeklyTrainingType.
# calculateSkillIncreaseOfTrainingWeek): the share of a level gained in one week
#   K(train) * f(level) * K(coach) * K(assistants) * intensity * (1 - stamina)
#   * 54 / (age + 37) * K(time) / 100
# A reference to compare our measurements with, not the truth.
SCHUM_TRAINING_FACTORS = {
    9: 5.1,  # goalkeeping
    3: 2.88,  # defending
    4: 3.24,  # scoring
    5: 4.8,  # crossing
    6: 1.5,  # shooting
    7: 3.6,  # short passes
    8: 3.36,  # playmaking
    2: 14.7,  # set pieces
    10: 3.15,  # through passes
    11: 1.38,  # defensive positions
    12: 3.12,  # wing attacks
}
SCHUM_COACH_FACTORS = {4: 0.7343, 5: 0.8324, 6: 0.92, 7: 1.0, 8: 1.0375}
SOLID_COACH = 7


def schum_level_factor(level):
    if level < 9:
        return 16.289 * math.exp(-0.1396 * level)
    return 54.676 / level - 1.438


def schum_weeks_per_level(
    training_type,
    level,
    age,
    intensity=100,
    stamina_share=10,
    coach_level=SOLID_COACH,
    assistants=0,
):
    """Weeks of full training (K(time) = 1) to go from ``level`` to the next, or None."""
    factor = SCHUM_TRAINING_FACTORS.get(training_type)
    if factor is None or level is None or age is None:
        return None
    per_week = (
        factor
        * schum_level_factor(level)
        * SCHUM_COACH_FACTORS[coach_level]
        * (1 + assistants * 0.035)
        * (intensity if intensity is not None else 100)
        / 100
        * (1 - (stamina_share if stamina_share is not None else 10) / 100)
        * 54
        / (age + 37)
        / 100
    )
    return 1 / min(per_week, 1) if per_week > 0 else None
