"""XML parsing functions for CHPP API responses.

Transforms CHPP XML responses into Python data structures.
Handles optional fields gracefully (YouthTeamId fix).
"""

import xml.etree.ElementTree as ET
from typing import Any

from app.chpp.models import CHPPPlayer, CHPPTeam, CHPPUser


def safe_find_text(root: ET.Element, xpath: str, default: Any = None) -> Any:
    """Safely extract text from XML element.

    Args:
        root: XML element to search
        xpath: XPath query string
        default: Value to return if element not found or empty

    Returns:
        Element text if found and non-empty, otherwise default
    """
    elem = root.find(xpath)
    if elem is not None and elem.text:
        return elem.text
    return default


def safe_find_int(root: ET.Element, xpath: str, default: int = 0) -> int:
    """Extract integer from XML element.

    Args:
        root: XML element to search
        xpath: XPath query string
        default: Value to return if element not found or not an integer

    Returns:
        Integer value if found and valid, otherwise default
    """
    text = safe_find_text(root, xpath)
    if text:
        try:
            return int(text)
        except (ValueError, TypeError):
            return default
    return default


def safe_find_bool(root: ET.Element, xpath: str, default: bool = False) -> bool:
    """Extract boolean from XML element.

    Args:
        root: XML element to search
        xpath: XPath query string
        default: Value to return if element not found

    Returns:
        Boolean value (True/False) if found, otherwise default

    Note:
        CHPP uses "True"/"False" strings or "1"/"0" for booleans
    """
    text = safe_find_text(root, xpath)
    if text:
        return text.lower() in ("true", "1", "yes")
    return default


def parse_user(root: ET.Element) -> CHPPUser:
    """Parse managercompendium XML to CHPPUser object.

    YouthTeamId is handled as optional field (fixes pychpp bug).

    Args:
        root: XML root element from managercompendium response

    Returns:
        CHPPUser instance with ht_id, username, team IDs

    Example:
        >>> root = ET.fromstring(xml_response)
        >>> user = parse_user(root)
        >>> print(user.username, user.ht_id)
    """
    # Extract user ID and username
    ht_id = safe_find_int(root, ".//Manager/UserId")
    username = safe_find_text(root, ".//Manager/Loginname", "")

    # YouthTeamId FIX: Handle as optional field (eliminates 27-line workaround)
    youth_team_id_text = safe_find_text(root, ".//YouthTeam/YouthTeamId")
    youth_team_id = int(youth_team_id_text) if youth_team_id_text else None

    # Extract team IDs (senior teams only)
    team_nodes = root.findall(".//Teams/Team/TeamId")
    teams = [int(node.text) for node in team_nodes if node.text]

    return CHPPUser(
        ht_id=ht_id,
        username=username,
        _teams_ht_id=teams,
        youth_team_id=youth_team_id,
        _SOURCE_FILE="managercompendium",
    )


def parse_team(root: ET.Element) -> CHPPTeam:
    """Parse teamdetails XML to CHPPTeam object.

    Args:
        root: XML root element from teamdetails response

    Returns:
        CHPPTeam instance with team info

    Example:
        >>> root = ET.fromstring(xml_response)
        >>> team = parse_team(root)
        >>> print(team.name, team.team_id)
    """
    # Extract required fields
    team_id = safe_find_int(root, ".//Team/TeamID")
    name = safe_find_text(root, ".//Team/TeamName", "")
    short_name = safe_find_text(root, ".//Team/ShortTeamName", "")

    # Extract optional fields
    league_name = safe_find_text(root, ".//League/LeagueName")
    league_level = safe_find_int(root, ".//League/LeagueLevel", None)
    region_id = safe_find_int(root, ".//Team/RegionId", None)
    founded_date = safe_find_text(root, ".//Team/FoundedDate")
    arena_name = safe_find_text(root, ".//Arena/ArenaName")
    arena_id = safe_find_int(root, ".//Arena/ArenaId", None)

    # Fan data
    fanclub_size = safe_find_int(root, ".//FanClub/FanClubSize", None)
    fans_mood = safe_find_text(root, ".//Fans/FansMood")
    fans_match_attitude = safe_find_text(root, ".//Fans/FansMatchAttitude")

    # Team colors (hex values)
    dress_uri = safe_find_text(root, ".//Team/DressURI")
    dress_alternate_uri = safe_find_text(root, ".//Team/DressAlternateURI")

    return CHPPTeam(
        team_id=team_id,
        name=name,
        short_team_name=short_name,
        league_name=league_name,
        league_level=league_level,
        region_id=region_id,
        founded_date=founded_date,
        arena_name=arena_name,
        arena_id=arena_id,
        fanclub_size=fanclub_size,
        fans_mood=fans_mood,
        fans_match_attitude=fans_match_attitude,
        dress_uri=dress_uri,
        dress_alternate_uri=dress_alternate_uri,
        _SOURCE_FILE="teamdetails",
    )


def parse_players(root: ET.Element) -> list[CHPPPlayer]:
    """Parse players XML to list of CHPPPlayer objects.

    Args:
        root: XML root element from players response

    Returns:
        List of CHPPPlayer instances with full skill data

    Example:
        >>> root = ET.fromstring(xml_response)
        >>> players = parse_players(root)
        >>> for player in players:
        ...     print(player.first_name, player.scorer)
    """
    players = []

    for player_node in root.findall(".//PlayerList/Player"):
        # Extract player identity
        player_id = safe_find_int(player_node, "PlayerID")
        first_name = safe_find_text(player_node, "FirstName", "")
        last_name = safe_find_text(player_node, "LastName", "")
        nick_name = safe_find_text(player_node, "NickName")

        # Player attributes
        age = safe_find_int(player_node, "Age")
        age_days = safe_find_int(player_node, "AgeDays")
        tsi = safe_find_int(player_node, "TSI")
        player_number = safe_find_int(player_node, "PlayerNumber")

        # Current form and condition
        form = safe_find_int(player_node, "PlayerForm")
        stamina = safe_find_int(player_node, "Stamina")
        experience = safe_find_int(player_node, "Experience")
        loyalty = safe_find_int(player_node, "Loyalty")

        # 7 Core Skills (match real API field names)
        keeper = safe_find_int(player_node, "Keeper")
        defender = safe_find_int(player_node, "Defender")
        playmaker = safe_find_int(player_node, "Playmaker")
        winger = safe_find_int(player_node, "Winger")
        passing = safe_find_int(player_node, "Passing")
        scorer = safe_find_int(player_node, "Scorer")
        set_pieces = safe_find_int(player_node, "SetPieces")

        # Additional attributes
        specialty = safe_find_int(player_node, "Specialty", None)
        injury_level = safe_find_int(player_node, "InjuryLevel", 0)
        statement = safe_find_text(player_node, "Statement")
        owner_notes = safe_find_text(player_node, "OwnerNotes")

        # Transfer data
        transfer_listed = safe_find_bool(player_node, "TransferListed")

        player = CHPPPlayer(
            player_id=player_id,
            first_name=first_name,
            last_name=last_name,
            nick_name=nick_name,
            age=age,
            age_days=age_days,
            tsi=tsi,
            player_number=player_number,
            form=form,
            stamina=stamina,
            experience=experience,
            loyalty=loyalty,
            keeper=keeper,
            defender=defender,
            playmaker=playmaker,
            winger=winger,
            passing=passing,
            scorer=scorer,
            set_pieces=set_pieces,
            specialty=specialty,
            injury_level=injury_level,
            statement=statement,
            owner_notes=owner_notes,
            transfer_listed=transfer_listed,
            _SOURCE_FILE="players",
        )
        players.append(player)

    return players
