"""Data model classes for CHPP API responses.

Matches pychpp interface exactly for zero breaking changes.
Supports dict-like access for backward compatibility.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class BidderTeam:
    """Team information for transfer bid.

    Attributes:
        team_id: Hattrick team ID
        team_name: Team name
    """

    team_id: int
    team_name: str

    def __getitem__(self, key: str) -> Any:
        """Support dict-like access."""
        return getattr(self, key)


@dataclass
class TransferDetails:
    """Transfer details for a player on the transfer list.

    Attributes:
        asking_price: Original asking price
        deadline: Transfer deadline (DateTime)
        highest_bid: Highest bid made so far (0 if none)
        max_bid: Maximum autobid set by owner (None if not set)
        bidder_team: Team holding highest bid (None if no bids)
    """

    asking_price: int
    deadline: str  # DateTime string from API
    highest_bid: int = 0
    max_bid:  int | None = None
    bidder_team:  BidderTeam | None = None

    def __getitem__(self, key: str) -> Any:
        """Support dict-like access."""
        return getattr(self, key)


@dataclass
class CHPPUser:
    """User data from managercompendium endpoint.

    Attributes:
        ht_id: Hattrick user ID
        username: Hattrick login name
        _teams_ht_id: List of team IDs owned by user
        youth_team_id: Youth team ID (optional, fixes pychpp bug)
        _SOURCE_FILE: CHPP file name (for compatibility)
    """

    ht_id: int
    username: str
    _teams_ht_id: list[int]
    youth_team_id:  int | None = None
    _SOURCE_FILE: str = "managercompendium"

    def __getitem__(self, key: str) -> Any:
        """Support dict-like access: user['ht_id']."""
        return getattr(self, key)


@dataclass
class CHPPTeam:
    """Team data from teamdetails endpoint.

    Attributes:
        team_id: Hattrick team ID
        name: Full team name
        short_team_name: Abbreviated team name
        league_name: League name
        league_level: League level (1-11)
        region_id: Region ID
        founded_date: Team foundation date
        arena_name: Arena/stadium name
        arena_id: Arena ID
        fanclub_size: Number of fanclub members
        fans_mood: Current fan mood
        fans_match_attitude: Fan attitude for matches
        dress_uri: Team kit image URI
        dress_alternate_uri: Alternate kit image URI
        _players: Internal list of players (lazy loaded)
        _SOURCE_FILE: CHPP file name (for compatibility)
    """

    team_id: int
    name: str
    short_team_name: str
    league_name:  str | None = None
    league_level:  int | None = None
    region_id:  int | None = None
    founded_date:  str | None = None
    arena_name:  str | None = None
    arena_id:  int | None = None
    fanclub_size:  int | None = None
    fans_mood:  str | None = None
    fans_match_attitude:  str | None = None
    dress_uri:  str | None = None
    dress_alternate_uri:  str | None = None
    # INFRA-028: Missing data parity fields
    logo_url:  str | None = None
    power_rating:  int | None = None
    power_rating_global_ranking:  int | None = None
    power_rating_league_ranking:  int | None = None
    power_rating_region_ranking:  int | None = None
    league_level_unit_id:  int | None = None
    league_level_unit_name:  str | None = None
    cup_name:  str | None = None
    cup_level:  int | None = None
    still_in_cup: bool = False
    number_of_victories:  int | None = None
    number_of_undefeated:  int | None = None
    _players: list["CHPPPlayer"] = field(default_factory=list)
    _SOURCE_FILE: str = "teamdetails"

    def players(self) -> list["CHPPPlayer"]:
        """Return list of players (lazy loaded).

        Returns:
            List of CHPPPlayer instances

        Note:
            Populated by CHPP.team() method when fetching team data
        """
        return self._players

    def __getitem__(self, key: str) -> Any:
        """Support dict-like access: team['name']."""
        return getattr(self, key)


@dataclass
class CHPPPlayer:
    """Player data from players endpoint.

    Attributes:
        player_id: Hattrick player ID
        first_name: Player first name
        last_name: Player last name
        nick_name: Player nickname (optional)
        age: Player age in years
        age_days: Additional days beyond age years
        tsi: Total Skill Index
        player_number: Jersey number
        form: Current form level (0-8)
        stamina: Stamina level (0-9)
        experience: Experience level (0-20)
        loyalty: Loyalty level (0-20)
        keeper: Goalkeeping skill (0-20)
        defender: Defending skill (0-20)
        playmaker: Playmaking skill (0-20)
        winger: Winger skill (0-20)
        passing: Passing skill (0-20)
        scorer: Scoring skill (0-20)
        set_pieces: Set pieces skill (0-20)
        specialty: Player specialty (0-8, optional)
        injury_level: Injury severity (-1 for none, 0-6)
        statement: Player statement text
        owner_notes: Manager's notes about player
        transfer_listed: Whether player is on transfer list
        _SOURCE_FILE: CHPP file name (for compatibility)
    """

    player_id: int
    first_name: str
    last_name: str
    nick_name:  str | None
    age: int
    age_days: int
    tsi: int
    player_number: int
    form: int
    stamina: int
    experience: int
    loyalty: int
    # 7 Core Skills
    keeper: int
    defender: int
    playmaker: int
    winger: int
    passing: int
    scorer: int
    set_pieces: int
    # Additional attributes
    specialty: int = 0  # 0 = no specialty
    category_id:  int | None = None
    arrival_date:  datetime | None = None  # DateTime object from parsed API string
    cards: int = 0
    agreeability:  str | None = None
    aggressiveness:  str | None = None
    honesty:  str | None = None
    country_id:  int | None = None
    salary:  int | None = None
    caps: int = 0
    caps_u20: int = 0
    career_goals: int = 0
    career_hattricks: int = 0
    league_goals: int = 0
    cup_goals: int = 0
    friendlies_goals: int = 0
    matches_current_team: int = 0
    goals_current_team: int = 0
    assists_current_team: int = 0
    career_assists: int = 0
    national_team_id:  int | None = None
    mother_club_bonus: int = 0
    leadership: int = 0
    injury_level: int = 0
    statement:  str | None = None
    owner_notes:  str | None = None
    transfer_listed: bool = False
    transfer_details:  TransferDetails | None = None
    _SOURCE_FILE: str = "players"

    @property
    def id(self) -> int:
        """Alias for player_id to match pychpp interface."""
        return self.player_id

    @property
    def number(self) -> int:
        """Alias for player_number to match pychpp interface."""
        return self.player_number

    def __getitem__(self, key: str) -> Any:
        """Support dict-like access: player['scorer']."""
        return getattr(self, key)


@dataclass
class CHPPMatch:
    """Match data from matches endpoint.

    Attributes:
        ht_id: Hattrick match ID
        datetime: Match date and time
        home_team_id: Home team ID
        home_team_name: Home team name
        away_team_id: Away team ID
        away_team_name: Away team name
        home_goals: Goals scored by home team
        away_goals: Goals scored by away team
        matchtype: Match type ID (league, cup, friendly, etc.)
        context_id: Context ID (league/cup ID)
        rule_id: Rule ID (region/rule set)
        cup_level: Cup level if cup match
        cup_level_index: Cup level index if cup match
        _SOURCE_FILE: CHPP file name (for compatibility)
    """

    ht_id: int
    datetime:  str | None
    home_team_id: int
    home_team_name: str
    away_team_id: int
    away_team_name: str
    home_goals:  int | None = None
    away_goals:  int | None = None
    matchtype:  int | None = None
    context_id:  int | None = None
    rule_id:  int | None = None
    cup_level:  int | None = None
    cup_level_index:  int | None = None
    _SOURCE_FILE: str = "matches"

    def __getitem__(self, key: str) -> Any:
        """Support dict-like access: match['ht_id']."""
        return getattr(self, key)


@dataclass
class CHPPMatchDetails:
    """Enhanced match details with comprehensive statistics from CHPP matchdetails endpoint.

    Attributes:
        ht_id: Hattrick match ID
        possession_first_half_home: Home team possession % in first half
        possession_first_half_away: Away team possession % in first half
        possession_second_half_home: Home team possession % in second half
        possession_second_half_away: Away team possession % in second half
        home_team_chances_left: Home team chances on left side
        home_team_chances_center: Home team chances in center
        home_team_chances_right: Home team chances on right side
        home_team_chances_special: Home team special event chances
        home_team_chances_other: Home team other chances
        away_team_chances_left: Away team chances on left side
        away_team_chances_center: Away team chances in center
        away_team_chances_right: Away team chances on right side
        away_team_chances_special: Away team special event chances
        away_team_chances_other: Away team other chances
        home_team_rating: Home team midfield rating
        away_team_rating: Away team midfield rating
        attendance: Match attendance
        weather: Weather conditions ID
        referee_name: Referee full name
        referee_country: Referee country
        scorers: List of goal scorers with details
        bookings: List of bookings (yellow/red cards)
        injuries: List of injuries during match
    """

    ht_id: int
    possession_first_half_home: int | None = None
    possession_first_half_away: int | None = None
    possession_second_half_home: int | None = None
    possession_second_half_away: int | None = None
    home_team_chances_left: int | None = None
    home_team_chances_center: int | None = None
    home_team_chances_right: int | None = None
    home_team_chances_special: int | None = None
    home_team_chances_other: int | None = None
    away_team_chances_left: int | None = None
    away_team_chances_center: int | None = None
    away_team_chances_right: int | None = None
    away_team_chances_special: int | None = None
    away_team_chances_other: int | None = None
    # Ratings - midfield (primary)
    home_team_rating: float | None = None
    away_team_rating: float | None = None
    # Ratings - defense by position
    home_team_rating_right_def: float | None = None
    home_team_rating_mid_def: float | None = None
    home_team_rating_left_def: float | None = None
    away_team_rating_right_def: float | None = None
    away_team_rating_mid_def: float | None = None
    away_team_rating_left_def: float | None = None
    # Ratings - attack by position
    home_team_rating_right_att: float | None = None
    home_team_rating_mid_att: float | None = None
    home_team_rating_left_att: float | None = None
    away_team_rating_right_att: float | None = None
    away_team_rating_mid_att: float | None = None
    away_team_rating_left_att: float | None = None
    # Set pieces
    home_team_rating_set_pieces_def: float | None = None
    home_team_rating_set_pieces_att: float | None = None
    away_team_rating_set_pieces_def: float | None = None
    away_team_rating_set_pieces_att: float | None = None
    # Arena
    attendance: int | None = None
    arena_capacity_terraces: int | None = None
    arena_capacity_basic: int | None = None
    arena_capacity_roof: int | None = None
    arena_capacity_vip: int | None = None
    weather_id: int | None = None
    added_minutes: int | None = None
    # Match officials
    referee_id: int | None = None
    referee_name: str = ""
    referee_country_id: int | None = None
    referee_country: str = ""
    referee_team_id: int | None = None
    referee_team_name: str = ""
    # Team details
    home_team_dress_uri: str = ""
    away_team_dress_uri: str = ""
    home_team_attitude: int | None = None
    away_team_attitude: int | None = None
    home_team_tactic_type: int | None = None
    home_team_tactic_skill: int | None = None
    away_team_tactic_type: int | None = None
    away_team_tactic_skill: int | None = None
    # Match events
    scorers: list = field(default_factory=list)
    bookings: list = field(default_factory=list)
    injuries: list = field(default_factory=list)

    def __getitem__(self, key: str) -> Any:
        """Support dict-like access."""
        return getattr(self, key)


@dataclass
class CHPPMatchLineupPlayer:
    """Player in match lineup with ratings and position.

    Attributes:
        player_id: Hattrick player ID
        name: Player full name
        rating_stars: Player match rating in stars
        rating_stars_eom: End of match rating
        role_id: Position role ID (100=GK, 101=RB, etc.)
        behaviour: Player behaviour setting
        minutes_played: Minutes played in match
        substituted_in: Minute substituted in (if applicable)
        substituted_out: Minute substituted out (if applicable)
    """

    player_id: int
    name: str
    rating_stars: float = 0.0
    rating_stars_eom: float = 0.0
    role_id: int = 0
    behaviour: int = 0
    minutes_played: int = 0
    substituted_in: int | None = None
    substituted_out: int | None = None

    def __getitem__(self, key: str) -> Any:
        """Support dict-like access."""
        return getattr(self, key)


@dataclass
class CHPPMatchLineup:
    """Complete match lineup with formations and player data.

    Attributes:
        ht_id: Hattrick match ID
        home_team_formation: Home team formation (e.g., "4-4-2")
        away_team_formation: Away team formation
        home_team_players: List of home team players with ratings
        away_team_players: List of away team players with ratings
        home_team_tactic: Home team tactical setup
        away_team_tactic: Away team tactical setup
    """

    ht_id: int
    home_team_formation: str = ""
    away_team_formation: str = ""
    home_team_players: list[CHPPMatchLineupPlayer] = field(default_factory=list)
    away_team_players: list[CHPPMatchLineupPlayer] = field(default_factory=list)
    home_team_tactic: str = ""
    away_team_tactic: str = ""

    def __getitem__(self, key: str) -> Any:
        """Support dict-like access."""
        return getattr(self, key)


@dataclass
class CHPPPlayerEvent:
    """Individual player event for career tracking.

    Attributes:
        player_id: Hattrick player ID
        match_id: Match where event occurred
        event_type: Type of event (goal, assist, card, injury)
        minute: Match minute when event occurred
        team_id: Team player was playing for
        opponent_team_id: Opponent team ID
        event_text: Description of the event
        season: Season when event occurred
        match_date: Date of the match
    """

    player_id: int
    match_id: int
    event_type: str
    minute: int
    team_id: int
    opponent_team_id: int = 0
    event_text: str = ""
    season: int = 0
    match_date: str = ""

    def __getitem__(self, key: str) -> Any:
        """Support dict-like access."""
        return getattr(self, key)
