"""Application constants for HT Status."""

# Default settings
DEFAULT_GROUP_ORDER = 99

# Hattrick match types
HT_MATCH_TYPE = {
    1: "League match",
    2: "Qualification match",
    3: "Cup match (standard league match)",
    4: "Friendly (normal rules)",
    5: "Friendly (cup rules)",
    6: "Not currently in use, but reserved for international competition matches with normal rules (may or may not be implemented at some future point).",
    7: "Hattrick Masters",
    8: "International friendly (normal rules)",
    9: "International friendly (cup rules)",
    10: "National teams competition match (normal rules)",
    11: "National teams competition match (cup rules)",
    12: "National teams friendly",
    50: "Tournament League match",
    51: "Tournament Playoff match",
    61: "Single match",
    62: "Ladder match",
    80: "Preparation match",
    100: "Youth league match",
    101: "Youth friendly match",
    102: "RESERVED",
    103: "Youth friendly match (cup rules)",
    104: "RESERVED",
    105: "Youth international friendly match",
    106: "Youth international friendly match (Cup rules)",
    107: "RESERVED"
}

# Hattrick match roles (player positions)
HT_MATCH_ROLE = {
    100: "Keeper",
    101: "Right back",
    102: "Right central defender",
    103: "Middle central defender",
    104: "Left central defender",
    105: "Left back",
    106: "Right winger",
    107: "Right inner midfield",
    108: "Middle inner midfield",
    109: "Left inner midfield",
    110: "Left winger",
    111: "Right forward",
    112: "Middle forward",
    113: "Left forward",
    114: "Substitution (Keeper)",
    115: "Substitution (Defender)",
    116: "Substitution (Inner midfield)",
    117: "Substitution (Winger)",
    118: "Substitution (Forward)",
    200: "Substitution (Keeper)",
    201: "Substitution (Central defender)",
    202: "Substitution (Wing back)",
    203: "Substitution (Inner midfielder)",
    204: "Substitution (Forward)",
    205: "Substitution (Winger)",
    206: "Substitution (Extra)",
    207: "Backup (Keeper)",
    208: "Backup (Central defender)",
    209: "Backup (Wing back)",
    210: "Backup (Inner midfielder)",
    211: "Backup (Forward)",
    212: "Backup (Winger)",
    213: "Backup (Extra)",
    17: "Set pieces",
    18: "Captain",
    19: "Replaced Player #1",
    20: "Replaced Player #2",
    21: "Replaced Player #3",
    22: "Penalty taker (1)",
    23: "Penalty taker (2)",
    24: "Penalty taker (3)",
    25: "Penalty taker (4)",
    26: "Penalty taker (5)",
    27: "Penalty taker (6)",
    28: "Penalty taker (7)",
    29: "Penalty taker (8)",
    30: "Penalty taker (9)",
    31: "Penalty taker (10)",
    32: "Penalty taker (11)"
}

# Hattrick match behaviors
HT_MATCH_BEHAVIOUR = {
    -1: "No change",
    0: "Normal",
    1: "Offensive",
    2: "Defensive",
    3: "Towards middle",
    4: "Towards wing",
    5: "Extra forward",
    6: "Extra inner midfield",
    7: "Extra defender"
}

# Player column definitions for UI tables
ALL_COLUMNS = [
    ('Group', 'group'), ('Number', 'number'),
    ('Specialty', 'specialty'), ('Name', 'name'),
    ('Age', 'age_years'), ('Keeper', 'keeper'),
    ('Defence', 'defender'), ('Playmaking', 'playmaker'),
    ('Winger', 'winger'), ('Passing', 'passing'),
    ('Scorer', 'scorer'), ('Set pieces', 'set_pieces'),
    ('Max stars', 'max_stars'), ('Last stars', 'last_stars'),
    ('Status', 'status'), ('First seen', 'firstseen'),
    ('Player notes', 'owner_notes'),
    ('Leadership', 'leadership'), ('Agreeability', 'agreeability'),
    ('Aggressiveness', 'aggressiveness'), ('Honesty', 'honesty'),
    ('Experience', 'experience'), ('Loyalty', 'loyalty'), ('TSI', 'tsi'),
    ('Form', 'form'), ('Stamina', 'stamina'),
    ('Career goals', 'career_goals'), ('Statement', 'statement'),
    ('Salary', 'salary'),
    ('Goalkeeper contribution (GC)', 'GC'),
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
    ("Man marking capability", "MMC")
]

DEFAULT_COLUMNS = [
    ('Group', 'group'), ('Number', 'number'),
    ('Specialty', 'specialty'), ('Name', 'name'),
    ('Age', 'age_years'), ('Keeper', 'keeper'),
    ('Defence', 'defender'), ('Playmaking', 'playmaker'),
    ('Winger', 'winger'), ('Passing', 'passing'),
    ('Scorer', 'scorer'), ('Set pieces', 'set_pieces'),
    ('Max stars', 'max_stars'), ('Last stars', 'last_stars'),
    ('Status', 'status'), ('First seen', 'firstseen'),
    ("Best position", "bestposition")
]

TRACE_COLUMNS = [
    'keeper', 'defender', 'playmaker',
    'winger', 'passing', 'scorer', 'set_pieces'
]

CALC_COLUMNS = [
    'GC',
    'CD', 'CDO', 'CDTW',
    'WBD', 'WBN', 'WBO', 'WBTM',
    'WO', 'WTM', 'WN', 'WD',
    'IMN', 'IMD', 'IMO', 'IMTW',
    'FW',
    'FTW', 'DF'
]
