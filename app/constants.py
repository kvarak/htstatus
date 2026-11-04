"""Application constants for HT Status."""

# Default settings
DEFAULT_GROUP_ORDER = 99

# Player column definitions for UI tables
ALL_COLUMNS = [
    ("Group", "group"),
    ("Number", "number"),
    ("Specialty", "specialty"),
    ("Name", "name"),
    ("Age", "age_years"),
    ("Keeper", "keeper"),
    ("Defence", "defender"),
    ("Playmaking", "playmaker"),
    ("Winger", "winger"),
    ("Passing", "passing"),
    ("Scorer", "scorer"),
    ("Set pieces", "set_pieces"),
    ("Max stars", "max_stars"),
    ("Last stars", "last_stars"),
    ("Status", "status"),
    ("First seen", "firstseen"),
    ("Player notes", "owner_notes"),
    ("Leadership", "leadership"),
    ("Agreeability", "agreeability"),
    ("Aggressiveness", "aggressiveness"),
    ("Honesty", "honesty"),
    ("Experience", "experience"),
    ("Loyalty", "loyalty"),
    ("TSI", "tsi"),
    ("Form", "form"),
    ("Stamina", "stamina"),
    ("Career goals", "career_goals"),
    ("Statement", "statement"),
    ("Salary", "salary"),
    ("Goalkeeper contribution (GC)", "GC"),
    ("Central Defender Normal (CD)", "CD"),
    ("Central Defender Offensive (CDO)", "CDO"),
    ("Side Central Defender Towards Wing (CDTW)", "CDTW"),
    ("Wing Back Defensive (WBD)", "WBD"),
    ("Wingback Normal (WBN)", "WBN"),
    ("Wing Back Offensive (WBO)", "WBO"),
    ("Wingback Towards Middle (WBTM)", "WBTM"),
    ("Winger Offensive (WO)", "WO"),
    ("Winger Towards Middle (WTM)", "WTM"),
    ("Winger Normal (WN)", "WN"),
    ("Winger Defensive (WD)", "WD"),
    ("Inner Midfielder Normal (IMN)", "IMN"),
    ("Inner Midfielder Defensive (IMD)", "IMD"),
    ("Inner Midfielder Offensive (IMO)", "IMO"),
    ("Inner Midfielder Towards Wing (IMTW)", "IMTW"),
    ("Forward Normal (FW)", "FW"),
    ("Forward Towards Wing (FTW) ", "FTW"),
    ("Defensive Forward (DF)", "DF"),
    ("Best position", "bestposition"),
    ("Man marking capability", "MMC"),
    # Add new columns at the end: everyone gets them (see COLUMNS_BEFORE_AUTO_ADD)
    ("Current bid", "current_bid"),
]

_COLUMN_BY_KEY = {key: (title, key) for title, key in ALL_COLUMNS}
DEFAULT_COLUMNS = [
    _COLUMN_BY_KEY[key]
    for key in (
        "group",
        "number",
        "specialty",
        "name",
        "age_years",
        "keeper",
        "defender",
        "playmaker",
        "winger",
        "passing",
        "scorer",
        "set_pieces",
        "max_stars",
        "last_stars",
        "status",
        "firstseen",
        "bestposition",
    )
]

# Every column that existed before new columns were added automatically.
# Never extend this: columns added to ALL_COLUMNS later are shown by default and
# appended once to every user's saved column list (app/columns.py).
COLUMNS_BEFORE_AUTO_ADD = frozenset(
    key for _title, key in ALL_COLUMNS if key not in {"current_bid"}
)
DEFAULT_COLUMNS += [c for c in ALL_COLUMNS if c[1] not in COLUMNS_BEFORE_AUTO_ADD]

TRACE_COLUMNS = [
    "keeper",
    "defender",
    "playmaker",
    "winger",
    "passing",
    "scorer",
    "set_pieces",
]

CALC_COLUMNS = [
    "GC",
    "CD",
    "CDO",
    "CDTW",
    "WBD",
    "WBN",
    "WBO",
    "WBTM",
    "WO",
    "WTM",
    "WN",
    "WD",
    "IMN",
    "IMD",
    "IMO",
    "IMTW",
    "FW",
    "FTW",
    "DF",
]

# CHPP MatchTypeID -> name (docs/datatypes.md); Hattrick's translations don't include these
MATCH_TYPE_NAMES = {
    1: "League",
    2: "Qualification",
    3: "Cup",
    4: "Friendly",
    5: "Friendly (cup rules)",
    7: "Hattrick Masters",
    8: "International friendly",
    9: "International friendly (cup rules)",
    10: "National teams competition",
    11: "National teams competition (cup rules)",
    12: "National teams friendly",
    50: "Tournament league",
    51: "Tournament playoff",
    61: "Duel",
    62: "Ladder",
    80: "Preparation",
    100: "Youth league",
    101: "Youth friendly",
    103: "Youth friendly (cup rules)",
    105: "Youth international friendly",
    106: "Youth international friendly (cup rules)",
}
