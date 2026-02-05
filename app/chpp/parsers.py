"""XML parsing functions for CHPP API responses.

Transforms CHPP XML responses into Python data structures.
Handles optional fields gracefully (YouthTeamId fix).
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

from app.chpp.models import CHPPMatch, CHPPPlayer, CHPPTeam, CHPPUser


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

    # INFRA-028: Extract missing critical data parity fields
    logo_url = safe_find_text(root, ".//Team/LogoURL")

    # Power rating information
    power_rating = safe_find_int(root, ".//PowerRating/PowerRating", None)
    power_rating_global_ranking = safe_find_int(root, ".//PowerRating/GlobalRanking", None)
    power_rating_league_ranking = safe_find_int(root, ".//PowerRating/LeagueRanking", None)
    power_rating_region_ranking = safe_find_int(root, ".//PowerRating/RegionRanking", None)

    # League level unit information
    league_level_unit_id = safe_find_int(root, ".//LeagueLevelUnit/LeagueLevelUnitID", None)
    league_level_unit_name = safe_find_text(root, ".//LeagueLevelUnit/LeagueLevelUnitName")
    # Override league_level with proper LeagueLevelUnit extraction
    league_level_unit_level = safe_find_int(root, ".//LeagueLevelUnit/LeagueLevel", None)
    if league_level_unit_level is not None:
        league_level = league_level_unit_level

    # Cup information
    cup_name = safe_find_text(root, ".//Cup/CupName")
    cup_level = safe_find_int(root, ".//Cup/CupLevel", None)
    still_in_cup = safe_find_bool(root, ".//Cup/StillInCup", False)

    # Team performance streaks
    number_of_victories = safe_find_int(root, ".//NumberOfVictories", None)
    number_of_undefeated = safe_find_int(root, ".//NumberOfUndefeated", None)

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
        # INFRA-028: Include missing data parity fields
        logo_url=logo_url,
        power_rating=power_rating,
        power_rating_global_ranking=power_rating_global_ranking,
        power_rating_league_ranking=power_rating_league_ranking,
        power_rating_region_ranking=power_rating_region_ranking,
        league_level_unit_id=league_level_unit_id,
        league_level_unit_name=league_level_unit_name,
        cup_name=cup_name,
        cup_level=cup_level,
        still_in_cup=still_in_cup,
        number_of_victories=number_of_victories,
        number_of_undefeated=number_of_undefeated,
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
        experience = safe_find_int(player_node, "Experience")
        loyalty = safe_find_int(player_node, "Loyalty")

        # 7 Core Skills (extract from PlayerSkills container)
        player_skills = player_node.find("PlayerSkills")
        if player_skills is not None:
            # Use correct API field names from PlayerSkills container
            stamina = safe_find_int(player_skills, "StaminaSkill")
            keeper = safe_find_int(player_skills, "KeeperSkill")
            defender = safe_find_int(player_skills, "DefenderSkill")
            playmaker = safe_find_int(player_skills, "PlaymakerSkill")
            winger = safe_find_int(player_skills, "WingerSkill")
            passing = safe_find_int(player_skills, "PassingSkill")
            scorer = safe_find_int(player_skills, "ScorerSkill")
            set_pieces = safe_find_int(player_skills, "SetPiecesSkill")
        else:
            # Fallback: try direct field names (may not exist in players endpoint)
            stamina = safe_find_int(player_node, "Stamina")
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

        # Goal statistics extraction (MISSING IN ORIGINAL IMPLEMENTATION)
        career_goals = safe_find_int(player_node, "CareerGoals", 0)
        career_hattricks = safe_find_int(player_node, "CareerHattricks", 0)
        league_goals = safe_find_int(player_node, "LeagueGoals", 0)
        cup_goals = safe_find_int(player_node, "CupGoals", 0)
        friendlies_goals = safe_find_int(player_node, "FriendliesGoals", 0)
        current_team_matches = safe_find_int(player_node, "MatchesCurrentTeam", 0)
        goals_current_team = safe_find_int(player_node, "GoalsCurrentTeam", 0)
        assists_current_team = safe_find_int(player_node, "AssistsCurrentTeam", 0)
        career_assists = safe_find_int(player_node, "CareerAssists", 0)

        # Team and league data
        caps = safe_find_int(player_node, "Caps", 0)
        caps_u20 = safe_find_int(player_node, "CapsU20", 0)
        country_id = safe_find_int(player_node, "NativeLeagueID", None)
        salary = safe_find_int(player_node, "Salary", None)
        national_team_id = safe_find_int(player_node, "NationalTeamID", None)

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
            # Goal statistics (ADDED)
            career_goals=career_goals,
            career_hattricks=career_hattricks,
            league_goals=league_goals,
            cup_goals=cup_goals,
            friendlies_goals=friendlies_goals,
            matches_current_team=current_team_matches,
            goals_current_team=goals_current_team,
            assists_current_team=assists_current_team,
            career_assists=career_assists,
            # Team data (ADDED)
            caps=caps,
            caps_u20=caps_u20,
            country_id=country_id,
            salary=salary,
            national_team_id=national_team_id,
            _SOURCE_FILE="players",
        )
        players.append(player)

    return players


def parse_player(root: ET.Element) -> CHPPPlayer:
    """Parse player XML to CHPPPlayer object (single player).

    Used for individual player fetches via player() endpoint.

    Args:
        root: XML root element from player response

    Returns:
        CHPPPlayer instance

    Example:
        >>> root = ET.fromstring(xml_response)
        >>> player = parse_player(root)
        >>> print(player.first_name, player.scorer)
    """
    # Navigate to Player element (API returns it under HattrickData/Player)
    player_elem = root.find(".//Player")
    if player_elem is None:
        raise ValueError("No Player element found in XML response")

    # Extract all player fields using safe_find_* helpers
    player_id = safe_find_int(player_elem, "PlayerID")
    first_name = safe_find_text(player_elem, "FirstName", "")
    last_name = safe_find_text(player_elem, "LastName", "")
    nick_name = safe_find_text(player_elem, "NickName")
    age = safe_find_int(player_elem, "Age")
    age_days = safe_find_int(player_elem, "AgeDays")
    tsi = safe_find_int(player_elem, "TSI")
    player_number = safe_find_int(player_elem, "PlayerNumber")
    category_id_text = safe_find_text(player_elem, "PlayerCategoryID")
    category_id = int(category_id_text) if category_id_text else None
    form = safe_find_int(player_elem, "PlayerForm")  # Form is PlayerForm in API
    experience = safe_find_int(player_elem, "Experience")
    loyalty = safe_find_int(player_elem, "Loyalty")

    # 7 core skills - from PlayerSkills container per CHPP API docs
    player_skills_elem = player_elem.find("PlayerSkills")
    if player_skills_elem is not None:
        stamina = safe_find_int(player_skills_elem, "StaminaSkill")
        keeper = safe_find_int(player_skills_elem, "KeeperSkill")
        defender = safe_find_int(player_skills_elem, "DefenderSkill")
        playmaker = safe_find_int(player_skills_elem, "PlaymakerSkill")
        winger = safe_find_int(player_skills_elem, "WingerSkill")
        passing = safe_find_int(player_skills_elem, "PassingSkill")
        scorer = safe_find_int(player_skills_elem, "ScorerSkill")
        set_pieces = safe_find_int(player_skills_elem, "SetPiecesSkill")
    else:
        # Fallback if PlayerSkills container not found
        stamina = 0
        keeper = 0
        defender = 0
        playmaker = 0
        winger = 0
        passing = 0
        scorer = 0
        set_pieces = 0

    # Additional attributes
    specialty = safe_find_int(player_elem, "Specialty", 0)  # Default to 0, not None
    category_id_text = safe_find_text(player_elem, "PlayerCategoryID")
    category_id = int(category_id_text) if category_id_text else None
    arrival_date_str = safe_find_text(player_elem, "ArrivalDate")
    # Parse arrival_date string to datetime object
    arrival_date = None
    if arrival_date_str:
        try:
            # Try parsing ISO format from API: "2024-01-15 14:30:00"
            arrival_date = datetime.fromisoformat(arrival_date_str.replace(" ", "T"))
        except (ValueError, AttributeError, TypeError):
            # If parsing fails, keep as None
            arrival_date = None
    cards = safe_find_int(player_elem, "Cards")
    agreeability = safe_find_text(player_elem, "Agreeability")
    aggressiveness = safe_find_text(player_elem, "Aggressiveness")
    honesty = safe_find_text(player_elem, "Honesty")
    country_id_text = safe_find_text(player_elem, "NativeLeagueID")
    country_id = int(country_id_text) if country_id_text else None
    salary_text = safe_find_text(player_elem, "Salary")
    salary = int(salary_text) if salary_text else None
    caps = safe_find_int(player_elem, "Caps")
    caps_u20 = safe_find_int(player_elem, "CapsU20")
    career_goals = safe_find_int(player_elem, "CareerGoals")
    career_hattricks = safe_find_int(player_elem, "CareerHattricks")
    league_goals = safe_find_int(player_elem, "LeagueGoals")
    cup_goals = safe_find_int(player_elem, "CupGoals")
    friendlies_goals = safe_find_int(player_elem, "FriendliesGoals")
    matches_current_team = safe_find_int(player_elem, "MatchesCurrentTeam")
    goals_current_team = safe_find_int(player_elem, "GoalsCurrentTeam")
    assists_current_team = safe_find_int(player_elem, "AssistsCurrentTeam")
    career_assists = safe_find_int(player_elem, "CareerAssists")
    # DEBUG: Print actual XML goal field values for investigation
    player_id_debug = safe_find_int(player_elem, "PlayerID")
    if player_id_debug in [461202762, 476003339, 474535474]:  # Key test players
        print(f"[XML DEBUG] Player {player_id_debug}: GoalsCurrentTeam='{player_elem.find('GoalsCurrentTeam')}', MatchesCurrentTeam='{player_elem.find('MatchesCurrentTeam')}'")
        if player_elem.find('GoalsCurrentTeam') is not None:
            print(f"[XML DEBUG] GoalsCurrentTeam element text: '{player_elem.find('GoalsCurrentTeam').text}'")
        if player_elem.find('MatchesCurrentTeam') is not None:
            print(f"[XML DEBUG] MatchesCurrentTeam element text: '{player_elem.find('MatchesCurrentTeam').text}'")

        # Show ALL available goal-related XML elements for debugging
        print(f"[XML DEBUG] Available goal fields for player {player_id_debug}:")
        for child in player_elem:
            if 'goal' in child.tag.lower() or 'match' in child.tag.lower() or 'assist' in child.tag.lower():
                print(f"  - {child.tag}: '{child.text}'")

        # Check if goals are in a different container
        for container in ['PlayerStats', 'Statistics', 'Goals', 'TeamStats']:
            container_elem = player_elem.find(container)
            if container_elem is not None:
                print(f"[XML DEBUG] Found container {container}, checking for goals...")
                for child in container_elem:
                    print(f"  - {container}/{child.tag}: '{child.text}'")

    national_team_id_text = safe_find_text(player_elem, "NationalTeamID")
    national_team_id = int(national_team_id_text) if national_team_id_text else None
    mother_club_bonus = safe_find_int(player_elem, "MotherClubBonus")
    leadership = safe_find_int(player_elem, "Leadership")
    injury_level = safe_find_int(player_elem, "InjuryLevel", -1)
    statement = safe_find_text(player_elem, "Statement")
    owner_notes = safe_find_text(player_elem, "OwnerNotes")
    transfer_listed = safe_find_bool(player_elem, "TransferListed")

    # Parse TransferDetails if player is on transfer list
    transfer_details = None
    if transfer_listed:
        transfer_elem = player_elem.find("TransferDetails")
        if transfer_elem is not None:
            from app.chpp.models import BidderTeam, TransferDetails

            asking_price = safe_find_int(transfer_elem, "AskingPrice")
            deadline = safe_find_text(transfer_elem, "Deadline", "")
            highest_bid = safe_find_int(transfer_elem, "HighestBid")
            max_bid_text = safe_find_text(transfer_elem, "MaxBid")
            max_bid = int(max_bid_text) if max_bid_text else None

            bidder_team = None
            bidder_elem = transfer_elem.find("BidderTeam")
            if bidder_elem is not None:
                bidder_team_id = safe_find_int(bidder_elem, "TeamID")
                bidder_team_name = safe_find_text(bidder_elem, "TeamName", "")
                if bidder_team_id:  # Only create if we have a team ID
                    bidder_team = BidderTeam(team_id=bidder_team_id, team_name=bidder_team_name)

            transfer_details = TransferDetails(
                asking_price=asking_price,
                deadline=deadline,
                highest_bid=highest_bid,
                max_bid=max_bid,
                bidder_team=bidder_team,
            )

    return CHPPPlayer(
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
        category_id=category_id,
        arrival_date=arrival_date,
        cards=cards,
        agreeability=agreeability,
        aggressiveness=aggressiveness,
        honesty=honesty,
        country_id=country_id,
        salary=salary,
        caps=caps,
        caps_u20=caps_u20,
        career_goals=career_goals,
        career_hattricks=career_hattricks,
        league_goals=league_goals,
        cup_goals=cup_goals,
        friendlies_goals=friendlies_goals,
        matches_current_team=matches_current_team,
        goals_current_team=goals_current_team,
        assists_current_team=assists_current_team,
        career_assists=career_assists,
        national_team_id=national_team_id,
        mother_club_bonus=mother_club_bonus,
        leadership=leadership,
        injury_level=injury_level,
        statement=statement,
        owner_notes=owner_notes,
        transfer_listed=transfer_listed,
        transfer_details=transfer_details,
        _SOURCE_FILE="player",
    )


def parse_matches(root: ET.Element) -> list[CHPPMatch]:
    """Parse matches XML to list of CHPPMatch objects.

    Used for match history fetches via matches endpoint.

    Args:
        root: XML root element from matches response

    Returns:
        List of CHPPMatch instances

    Example:
        >>> root = ET.fromstring(xml_response)
        >>> matches = parse_matches(root)
        >>> for match in matches:
        ...     print(match.home_team_name, match.home_goals)
    """
    matches = []

    # Navigate to match list - handle different endpoint structures
    # matchesarchive v1.5: HattrickData/Team/MatchList/Match
    # matches v2.6: Could be different structure
    match_elements = root.findall(".//Team/MatchList/Match")
    if not match_elements:
        # Try alternative structures for different endpoint versions
        match_elements = root.findall(".//MatchList/Match")
    if not match_elements:
        match_elements = root.findall(".//Match")

    for match_elem in match_elements:
        # Extract match fields using safe_find_* helpers
        ht_id = safe_find_int(match_elem, "MatchID")
        datetime = safe_find_text(match_elem, "MatchDate")

        # Parse datetime if present (format: "2024-01-15 14:30:00")
        # Keep as string for compatibility with existing code
        # (existing code calls match.datetime.year, month, day - will need conversion)

# Team information: different structures for different CHPP endpoint versions
        # matches v2.6: HomeTeam/HomeTeamID and AwayTeam/AwayTeamID
        # matchesarchive v1.5: HomeTeamID and AwayTeamID directly under Match
        home_team_id = safe_find_int(match_elem, "HomeTeam/HomeTeamID")
        home_team_name = safe_find_text(match_elem, "HomeTeam/HomeTeamName", "")
        away_team_id = safe_find_int(match_elem, "AwayTeam/AwayTeamID")
        away_team_name = safe_find_text(match_elem, "AwayTeam/AwayTeamName", "")

        # Fallback for matchesarchive v1.5 structure (direct under Match)
        if not home_team_name:
            home_team_name = safe_find_text(match_elem, "HomeTeamName", "")
        if not home_team_id:
            home_team_id = safe_find_int(match_elem, "HomeTeamID")
        if not away_team_name:
            away_team_name = safe_find_text(match_elem, "AwayTeamName", "")
        if not away_team_id:
            away_team_id = safe_find_int(match_elem, "AwayTeamID")
        home_goals = safe_find_int(match_elem, "HomeGoals")
        away_goals = safe_find_int(match_elem, "AwayGoals")

        matchtype = safe_find_int(match_elem, "MatchType")
        context_id = safe_find_int(match_elem, "ContextID")
        rule_id = safe_find_int(match_elem, "RuleID")
        cup_level = safe_find_int(match_elem, "CupLevel")
        cup_level_index = safe_find_int(match_elem, "CupLevelIndex")

        match = CHPPMatch(
            ht_id=ht_id,
            datetime=datetime,
            home_team_id=home_team_id,
            home_team_name=home_team_name,
            away_team_id=away_team_id,
            away_team_name=away_team_name,
            home_goals=home_goals,
            away_goals=away_goals,
            matchtype=matchtype,
            context_id=context_id,
            rule_id=rule_id,
            cup_level=cup_level,
            cup_level_index=cup_level_index,
            _SOURCE_FILE="matches",
        )
        matches.append(match)

    return matches
