"""
Hattrick country utilities for mapping country IDs to names and flags.
Data sourced from: https://wiki.hattrick.org/wiki/Country
"""

COUNTRIES = {
    1: {"name": "Sweden", "flag": "🇸🇪", "color": "#006AA7"},  # Swedish blue
    2: {"name": "England", "flag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "color": "#CE1124"},  # St George's cross red
    3: {"name": "Germany", "flag": "🇩🇪", "color": "#FFCC00"},  # German gold ("black, red and gold")
    4: {"name": "Italy", "flag": "🇮🇹", "color": "#009246"},  # Italian green
    5: {"name": "France", "flag": "🇫🇷", "color": "#FFFFFF"},  # French white ("blue, white and red")
    6: {"name": "Mexico", "flag": "🇲🇽", "color": "#006341"},  # Mexican green
    7: {"name": "Argentina", "flag": "🇦🇷", "color": "#74ACDF"},  # Argentine blue
    8: {"name": "USA", "flag": "🇺🇸", "color": "#B22234"},  # American red
    9: {"name": "Norway", "flag": "🇳🇴", "color": "#EF2B2D"},  # Norwegian red
    11: {"name": "Denmark", "flag": "🇩🇰", "color": "#C8102E"},  # Danish red
    12: {"name": "Finland", "flag": "🇫🇮", "color": "#003580"},  # Finnish blue
    14: {"name": "Netherlands", "flag": "🇳🇱", "color": "#FF9B00"},  # Dutch orange
    15: {"name": "Oceania", "flag": "🌏", "color": "#00A693"},  # Ocean blue-green
    16: {"name": "Brazil", "flag": "🇧🇷", "color": "#009739"},  # Brazilian green
    17: {"name": "Canada", "flag": "🇨🇦", "color": "#FF0000"},  # Canadian red
    18: {"name": "Chile", "flag": "🇨🇱", "color": "#0039A6"},  # Chilean blue
    19: {"name": "Colombia", "flag": "🇨🇴", "color": "#FDE047"},  # Colombian yellow
    20: {"name": "India", "flag": "🇮🇳", "color": "#FF9933"},  # Indian saffron
    21: {"name": "Republic of Ireland", "flag": "🇮🇪", "color": "#169B62"},  # Irish green
    22: {"name": "Japan", "flag": "🇯🇵", "color": "#BC002D"},  # Japanese red
    23: {"name": "Peru", "flag": "🇵🇪", "color": "#D91023"},  # Peruvian red
    24: {"name": "Poland", "flag": "🇵🇱", "color": "#DC143C"},  # Polish red (changed for visibility)
    25: {"name": "Portugal", "flag": "🇵🇹", "color": "#006600"},  # Portuguese green
    26: {"name": "Scotland", "flag": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "color": "#005EB8"},  # Scottish blue
    27: {"name": "South Africa", "flag": "🇿🇦", "color": "#007A4D"},  # South African green
    28: {"name": "Uruguay", "flag": "🇺🇾", "color": "#0038A8"},  # Uruguayan blue
    29: {"name": "Venezuela", "flag": "🇻🇪", "color": "#FCDD09"},  # Venezuelan yellow
    30: {"name": "South Korea", "flag": "🇰🇷", "color": "#CD2E3A"},  # Korean red
    31: {"name": "Thailand", "flag": "🇹🇭", "color": "#A51931"},  # Thai red
    32: {"name": "Turkey", "flag": "🇹🇷", "color": "#E30A17"},  # Turkish red
    33: {"name": "Egypt", "flag": "🇪🇬", "color": "#FFD700"},  # Egyptian gold (changed for visibility)
    34: {"name": "China", "flag": "🇨🇳", "color": "#DE2910"},  # Chinese red
    35: {"name": "Russia", "flag": "🇷🇺", "color": "#FFFFFF"},  # Russian white ("white, blue and red")
    36: {"name": "Spain", "flag": "🇪🇸", "color": "#FFD700"},  # Spanish gold ("red and gold")
    37: {"name": "Romania", "flag": "🇷🇴", "color": "#002B7F"},  # Romanian blue ("blue, yellow and red")
    38: {"name": "Iceland", "flag": "🇮🇸", "color": "#003897"},  # Icelandic blue
    39: {"name": "Austria", "flag": "🇦🇹", "color": "#ED2939"},  # Austrian red
    40: {"name": "Unknown Country 40", "flag": "❓", "color": "#CCCCCC"},  # TODO: Research actual country
    44: {"name": "Belgium", "flag": "🇧🇪", "color": "#FFCD00"},  # Belgian yellow (changed from black)
    45: {"name": "Malaysia", "flag": "🇲🇾", "color": "#CC0001"},  # Malaysian red
    46: {"name": "Switzerland", "flag": "🇨🇭", "color": "#DA020E"},  # Swiss red
    47: {"name": "Singapore", "flag": "🇸🇬", "color": "#ED2939"},  # Singapore red ("red and white" - using red)
    50: {"name": "Greece", "flag": "🇬🇷", "color": "#0D5EAF"},  # Greek blue ("blue and white" - using blue)
    51: {"name": "Hungary", "flag": "🇭🇺", "color": "#436F4D"},  # Hungarian dark green ("red, white and dark green" - using green)
    52: {"name": "Czech Republic", "flag": "🇨🇿", "color": "#D7141A"},  # Czech red ("white, red and blue" - using red)
    53: {"name": "Latvia", "flag": "🇱🇻", "color": "#A4343A"},  # Latvian red
    54: {"name": "Indonesia", "flag": "🇮🇩", "color": "#CE1126"},  # Indonesian red
    55: {"name": "Philippines", "flag": "🇵🇭", "color": "#0038A8"},  # Filipino blue
    56: {"name": "Estonia", "flag": "🇪🇪", "color": "#000000"},  # Estonian black ("blue, black and white")
    57: {"name": "Serbia", "flag": "🇷🇸", "color": "#0C4076"},  # Serbian blue ("red, blue and white")
    58: {"name": "Croatia", "flag": "🇭🇷", "color": "#171796"},  # Croatian blue ("red, white and blue" - using blue)
    59: {"name": "Hong Kong", "flag": "🇭🇰", "color": "#BADB00"},  # Hong Kong bright green (distinctive from China red)
    60: {"name": "Taiwan", "flag": "🇹🇼", "color": "#FE0000"},  # Taiwanese red
    61: {"name": "Wales", "flag": "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "color": "#C8102E"},  # Welsh red ("red, green and white" - using red)
    62: {"name": "Bulgaria", "flag": "🇧🇬", "color": "#00966E"},  # Bulgarian green ("white, green and red" - using green)
    63: {"name": "Israel", "flag": "🇮🇱", "color": "#0038B8"},  # Israeli blue ("blue and white" - using blue)
    64: {"name": "Slovenia", "flag": "🇸🇮", "color": "#005DA4"},  # Slovenian blue
    66: {"name": "Lithuania", "flag": "🇱🇹", "color": "#FDB462"},  # Lithuanian yellow
    67: {"name": "Slovakia", "flag": "🇸🇰", "color": "#0B4EA2"},  # Slovak blue
    68: {"name": "Ukraine", "flag": "🇺🇦", "color": "#005BBB"},  # Ukrainian blue
    69: {"name": "Bosnia & Herzegovina", "flag": "🇧🇦", "color": "#002395"},  # Bosnian blue
    70: {"name": "Vietnam", "flag": "🇻🇳", "color": "#DA020E"},  # Vietnamese red
    71: {"name": "Pakistan", "flag": "🇵🇰", "color": "#FFFFFF"},  # Pakistani white ("green and white")
    72: {"name": "Paraguay", "flag": "🇵🇾", "color": "#FFFFFF"},  # Paraguayan white ("red, white and blue" - using white)
    73: {"name": "Ecuador", "flag": "🇪🇨", "color": "#FFD100"},  # Ecuadorian yellow ("yellow, blue and red" - using yellow)
    74: {"name": "Bolivia", "flag": "🇧🇴", "color": "#007934"},  # Bolivian green
    75: {"name": "Nigeria", "flag": "🇳🇬", "color": "#008751"},  # Nigerian green
    76: {"name": "Faroe Islands", "flag": "🇫🇴", "color": "#ED2939"},  # Faroese red
    77: {"name": "Morocco", "flag": "🇲🇦", "color": "#C1272D"},  # Moroccan red
    79: {"name": "Saudi Arabia", "flag": "🇸🇦", "color": "#006C35"},  # Saudi green
    80: {"name": "Tunisia", "flag": "🇹🇳", "color": "#E70013"},  # Tunisian red
    81: {"name": "Costa Rica", "flag": "🇨🇷", "color": "#002B7F"},  # Costa Rican blue
    83: {"name": "United Arab Emirates", "flag": "🇦🇪", "color": "#00732F"},  # UAE green
    84: {"name": "Luxembourg", "flag": "🇱🇺", "color": "#00A2E8"},  # Luxembourg light blue ("red, white and light blue" - using light blue)
    85: {"name": "Iran", "flag": "🇮🇷", "color": "#239F40"},  # Iranian green
    88: {"name": "Dominican Republic", "flag": "🇩🇴", "color": "#002D62"},  # Dominican blue
    89: {"name": "Cyprus", "flag": "🇨🇾", "color": "#D57800"},  # Cyprus orange
    91: {"name": "Belarus", "flag": "🇧🇾", "color": "#CF142B"},  # Belarusian red
    93: {"name": "Northern Ireland", "flag": "🇬🇧", "color": "#CF142B"},  # Northern Irish red
    94: {"name": "Jamaica", "flag": "🇯🇲", "color": "#009639"},  # Jamaican green
    95: {"name": "Kenya", "flag": "🇰🇪", "color": "#BB0000"},  # Kenyan red
    96: {"name": "Panama", "flag": "🇵🇦", "color": "#072B5F"},  # Panamanian blue
    97: {"name": "North Macedonia", "flag": "🇲🇰", "color": "#D20000"},  # Macedonian red
    98: {"name": "Albania", "flag": "🇦🇱", "color": "#E41E20"},  # Albanian red
    99: {"name": "Honduras", "flag": "🇭🇳", "color": "#0073CF"},  # Honduran blue
    100: {"name": "El Salvador", "flag": "🇸🇻", "color": "#0047AB"},  # Salvadoran blue
    101: {"name": "Malta", "flag": "🇲🇹", "color": "#CF142B"},  # Maltese red
    102: {"name": "Kyrgyzstan", "flag": "🇰🇬", "color": "#E4002B"},  # Kyrgyz red
    103: {"name": "Moldova", "flag": "🇲🇩", "color": "#0046AE"},  # Moldovan blue
    104: {"name": "Georgia", "flag": "🇬🇪", "color": "#FF0000"},  # Georgian red
    105: {"name": "Andorra", "flag": "🇦🇩", "color": "#10069F"},  # Andorran blue
    106: {"name": "Jordan", "flag": "🇯🇴", "color": "#FFFFFF"},  # Jordanian white ("black, white, green and red" - using white)
    107: {"name": "Guatemala", "flag": "🇬🇹", "color": "#4997D0"},  # Guatemalan blue
    110: {"name": "Trinidad & Tobago", "flag": "🇹🇹", "color": "#FFFFFF"},  # Trinidad white ("red, white and black" - using white)
    111: {"name": "Nicaragua", "flag": "🇳🇮", "color": "#0067C6"},  # Nicaraguan blue,
    112: {"name": "Kazakhstan", "flag": "🇰🇿", "color": "#1EB53A"},  # Kazakhstan green from flag
    113: {"name": "Suriname", "flag": "🇸🇷", "color": "#377E3F"},  # Suriname green
    117: {"name": "Liechtenstein", "flag": "🇱🇮", "color": "#002868"},  # Liechtenstein blue
    118: {"name": "Algeria", "flag": "🇩🇿", "color": "#006233"},  # Algeria green
    119: {"name": "Mongolia", "flag": "🇲🇳", "color": "#0066CC"},  # Mongolia blue
    120: {"name": "Lebanon", "flag": "🇱🇧", "color": "#ED1C24"},  # Lebanon red
    121: {"name": "Senegal", "flag": "🇸🇳", "color": "#FECB00"},  # Senegal yellow
    122: {"name": "Armenia", "flag": "🇦🇲", "color": "#F2A800"},  # Armenia orange
    123: {"name": "Bahrain", "flag": "🇧🇭", "color": "#8B0000"},  # Bahrain dark red
    124: {"name": "Barbados", "flag": "🇧🇧", "color": "#FFC72C"},  # Barbados gold
    125: {"name": "Cape Verde", "flag": "🇨🇻", "color": "#003DA5"},  # Cape Verde blue
    126: {"name": "Ivory Coast", "flag": "🇨🇮", "color": "#F77F00"},  # Ivory Coast orange
    127: {"name": "Kuwait", "flag": "🇰🇼", "color": "#007A3D"},  # Kuwait green
    128: {"name": "Iraq", "flag": "🇮🇶", "color": "#CE1126"},  # Iraq red
    129: {"name": "Azerbaijan", "flag": "🇦🇿", "color": "#3F9FD3"},  # Azerbaijan sky blue
    130: {"name": "Angola", "flag": "🇦🇴", "color": "#FFE135"},  # Angola yellow (different from Germany gold)
    131: {"name": "Montenegro", "flag": "🇲🇪", "color": "#C8102E"},  # Montenegro red
    132: {"name": "Bangladesh", "flag": "🇧🇩", "color": "#006A4E"},  # Bangladesh green
    133: {"name": "Yemen", "flag": "🇾🇪", "color": "#CE1126"},  # Yemen red
    134: {"name": "Oman", "flag": "🇴🇲", "color": "#239F40"},  # Oman green
    135: {"name": "Mozambique", "flag": "🇲🇿", "color": "#FCDD09"},  # Mozambique yellow
    136: {"name": "Brunei", "flag": "🇧🇳", "color": "#FFCC02"},  # Brunei yellow
    137: {"name": "Ghana", "flag": "🇬🇭", "color": "#FCD116"},  # Ghana yellow
    138: {"name": "Kampuchea", "flag": "🇰🇭", "color": "#032EA1"},  # Cambodia blue
    139: {"name": "Benin", "flag": "🇧🇯", "color": "#FDD017"},  # Benin yellow
    140: {"name": "Syria", "flag": "🇸🇾", "color": "#FFFFFF"},  # Syrian white ("red, white, black and green" - using white)
    141: {"name": "Qatar", "flag": "🇶🇦", "color": "#8B1538"},  # Qatar maroon
    142: {"name": "Tanzania", "flag": "🇹🇿", "color": "#00A86B"},  # Tanzania green
    143: {"name": "Uganda", "flag": "🇺🇬", "color": "#FCDC00"},  # Uganda yellow
    144: {"name": "Maldives", "flag": "🇲🇻", "color": "#D21034"},  # Maldives red
    145: {"name": "Uzbekistan", "flag": "🇺🇿", "color": "#00AFCA"},  # Uzbekistan light blue ("blue, white, green and red" - using blue)
    146: {"name": "Cameroon", "flag": "🇨🇲", "color": "#007A5E"},  # Cameroon green
    147: {"name": "Cuba", "flag": "🇨🇺", "color": "#002A8F"},  # Cuba blue
    148: {"name": "Palestine", "flag": "🇵🇸", "color": "#007A3D"},  # Palestinian green ("black, white, green and red" - using green)
    149: {"name": "Sao Tome & Principe", "flag": "🇸🇹", "color": "#12AD2B"},  # Sao Tome green
    151: {"name": "Comoros", "flag": "🇰🇲", "color": "#3D5AA1"},  # Comoros blue
    152: {"name": "Sri Lanka", "flag": "🇱🇰", "color": "#FF7300"},  # Sri Lanka orange
    153: {"name": "Curaçao", "flag": "🇨🇼", "color": "#FAAB36"},  # Curaçao orange (distinctive from Liechtenstein blue)
    154: {"name": "Guam", "flag": "🇬🇺", "color": "#1F75FE"},  # Guam blue
    155: {"name": "DR Congo", "flag": "🇨🇩", "color": "#007FFF"},  # DR Congo blue
    156: {"name": "Ethiopia", "flag": "🇪🇹", "color": "#FCDD09"},  # Ethiopia yellow
    157: {"name": "Saint Vincent & the Grenadines", "flag": "🇻🇨", "color": "#012169"},  # St. Vincent blue
    158: {"name": "Belize", "flag": "🇧🇿", "color": "#003F87"},  # Belize blue
    159: {"name": "Madagascar", "flag": "🇲🇬", "color": "#FC3D32"},  # Madagascar red
    160: {"name": "Botswana", "flag": "🇧🇼", "color": "#6EB5D0"},  # Botswana light blue
    161: {"name": "Myanmar", "flag": "🇲🇲", "color": "#FECB00"},  # Myanmar yellow
    162: {"name": "Zambia", "flag": "🇿🇲", "color": "#198A00"},  # Zambia green
    163: {"name": "San Marino", "flag": "🇸🇲", "color": "#5EB3F5"},  # San Marino light blue
    164: {"name": "Haiti", "flag": "🇭🇹", "color": "#00209F"},  # Haiti blue
    165: {"name": "Puerto Rico", "flag": "🇵🇷", "color": "#00235B"},  # Puerto Rico navy blue (distinctive color)
    166: {"name": "Nepal", "flag": "🇳🇵", "color": "#003893"},  # Nepal blue ("crimson, blue and white" - using blue)
    167: {"name": "Tahiti", "flag": "🇵🇫", "color": "#ED2939"},  # Red from French Polynesia flag
    168: {"name": "Guinea", "flag": "🇬🇳", "color": "#FECB00"},  # Guinea yellow ("red, yellow and green" - using yellow)
    169: {"name": "Grenada", "flag": "🇬🇩", "color": "#007A33"},  # Grenada green ("green, yellow and red" - using green)
    170: {"name": "Guyana", "flag": "🇬🇾", "color": "#009E49"},  # Green from flag
    171: {"name": "Bahamas", "flag": "🇧🇸", "color": "#00778B"},  # Blue from flag
    172: {"name": "Guinea Ecuatorial", "flag": "🇬🇶", "color": "#3E9A00"},  # Green from flag
    173: {"name": "Rwanda", "flag": "🇷🇼", "color": "#00A1DE"},  # Blue from flag
    174: {"name": "Saint Kitts and Nevis", "flag": "🇰🇳", "color": "#DA291C"},  # Red from flag
    175: {"name": "Burkina Faso", "flag": "🇧🇫", "color": "#EF2B2D"},  # Red from flag
    176: {"name": "Gibraltar", "flag": "🇬🇮", "color": "#DA020E"},  # Red from flag
    177: {"name": "Bhutan", "flag": "🇧🇹", "color": "#FFD520"},  # Yellow from flag
    178: {"name": "Belize", "flag": "🇧🇿", "color": "#CE1126"},  # Second Belize entry (duplicate country) - using red
    180: {"name": "Unknown Country 180", "flag": "❓", "color": "#DDDDDD"},  # TODO: Research actual country
    191: {"name": "Unknown Country 191", "flag": "❓", "color": "#EEEEEE"},  # TODO: Research actual country
    1000: {"name": "Hattrick International", "flag": "🌍", "color": "#4A90E2"},  # International blue
}


def get_country_name(country_id):
    """
    Get country name from Hattrick country ID.

    Args:
        country_id (int): Hattrick country ID

    Returns:
        str: Country name or 'Unknown' if ID not found
    """
    if country_id is None:
        return 'Unknown'

    country_data = COUNTRIES.get(country_id)
    return country_data['name'] if country_data else 'Unknown'


def get_country_flag(country_id):
    """
    Get country flag emoji from Hattrick country ID.

    Args:
        country_id (int): Hattrick country ID

    Returns:
        str: Country flag emoji or '🏳️' if ID not found
    """
    if country_id is None:
        return '🏳️'

    country_data = COUNTRIES.get(country_id)
    return country_data['flag'] if country_data else '🏳️'


def get_country_color(country_id):
    """
    Get country color from Hattrick country ID.

    Args:
        country_id (int): Hattrick country ID

    Returns:
        str: Country color hex code or '#6B7280' (gray) if ID not found
    """
    if country_id is None:
        return '#6B7280'

    country_data = COUNTRIES.get(country_id)
    return country_data.get('color', '#6B7280') if country_data else '#6B7280'


def get_country_data(country_id):
    """
    Get complete country display information.

    Args:
        country_id (int): Hattrick country ID

    Returns:
        dict: Dictionary with name, flag, and color
    """
    return {
        'name': get_country_name(country_id),
        'flag': get_country_flag(country_id),
        'color': get_country_color(country_id)
    }


def get_country_info(country_id):
    """
    Get complete country information from Hattrick country ID.

    Args:
        country_id (int): Hattrick country ID

    Returns:
        dict: Dictionary with 'name', 'flag', and 'color' keys, or defaults if ID not found
    """
    if country_id is None:
        return {'name': 'Unknown', 'flag': '🏳️', 'color': '#6B7280'}

    country_data = COUNTRIES.get(country_id)
    if country_data:
        return {
            'name': country_data['name'],
            'flag': country_data['flag'],
            'color': country_data.get('color', '#6B7280')
        }
    else:
        return {'name': 'Unknown', 'flag': '🏳️', 'color': '#6B7280'}


def get_country_display(country_id, include_flag=True):
    """
    Get formatted country display string.

    Args:
        country_id (int): Hattrick country ID
        include_flag (bool): Whether to include flag emoji

    Returns:
        str: Formatted country string (e.g., "🇸🇪 Sweden" or "Sweden")
    """
    country_info = get_country_info(country_id)

    if include_flag:
        return f"{country_info['flag']} {country_info['name']}"
    else:
        return country_info['name']
