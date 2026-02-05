import pickle
import time
from datetime import datetime

from app import db

# --------------------------------------------------------------------------------


class MatchPlay(db.Model):
    __tablename__ = "matchplay"

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    first_name = db.Column(db.String(100), nullable=False)
    nick_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer)
    rating_stars = db.Column(db.Float)
    rating_stars_eom = db.Column(db.Float)
    behaviour = db.Column(db.Integer)

    def __init__(self, matchdata):
        self.match_id = matchdata["match_id"]
        self.player_id = matchdata["player_id"]
        self.datetime = matchdata["datetime"]
        self.first_name = matchdata["first_name"]
        self.nick_name = matchdata["nick_name"]
        self.last_name = matchdata["last_name"]
        self.role_id = matchdata["role_id"]
        self.rating_stars = matchdata["rating_stars"]
        self.rating_stars_eom = matchdata["rating_stars_eom"]
        self.behaviour = matchdata["behaviour"]

    def __repr__(self):
        return f"{self.first_name} {self.last_name}: {self.rating_stars}/{self.rating_stars_eom}"


# --------------------------------------------------------------------------------


class Match(db.Model):
    __tablename__ = "match"

    ht_id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, nullable=False)
    home_team_name = db.Column(db.String(100), nullable=False)
    away_team_id = db.Column(db.Integer, nullable=False)
    away_team_name = db.Column(db.String(100), nullable=False)
    datetime = db.Column(db.DateTime)
    matchtype = db.Column(db.Integer)
    context_id = db.Column(db.Integer)
    rule_id = db.Column(db.Integer)
    cup_level = db.Column(db.Integer)
    cup_level_index = db.Column(db.Integer)
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)

    # Enhanced analytics fields from CHPP matchdetails (nullable for backward compatibility)
    # Possession - stored by half as CHPP provides (at Match level, not inside teams)
    possession_first_half_home = db.Column(db.Integer, nullable=True)
    possession_first_half_away = db.Column(db.Integer, nullable=True)
    possession_second_half_home = db.Column(db.Integer, nullable=True)
    possession_second_half_away = db.Column(db.Integer, nullable=True)

    # Chances breakdown (CHPP v3.1, March 2022 - inside HomeTeam/AwayTeam)
    home_team_chances_left = db.Column(db.Integer, nullable=True)
    home_team_chances_center = db.Column(db.Integer, nullable=True)
    home_team_chances_right = db.Column(db.Integer, nullable=True)
    home_team_chances_special = db.Column(db.Integer, nullable=True)
    home_team_chances_other = db.Column(db.Integer, nullable=True)
    away_team_chances_left = db.Column(db.Integer, nullable=True)
    away_team_chances_center = db.Column(db.Integer, nullable=True)
    away_team_chances_right = db.Column(db.Integer, nullable=True)
    away_team_chances_special = db.Column(db.Integer, nullable=True)
    away_team_chances_other = db.Column(db.Integer, nullable=True)

    # Team ratings - midfield (primary overall rating)
    home_team_rating = db.Column(db.Float, nullable=True)
    away_team_rating = db.Column(db.Float, nullable=True)

    # Team ratings - defense by position
    home_team_rating_right_def = db.Column(db.Float, nullable=True)
    home_team_rating_mid_def = db.Column(db.Float, nullable=True)
    home_team_rating_left_def = db.Column(db.Float, nullable=True)
    away_team_rating_right_def = db.Column(db.Float, nullable=True)
    away_team_rating_mid_def = db.Column(db.Float, nullable=True)
    away_team_rating_left_def = db.Column(db.Float, nullable=True)

    # Team ratings - attack by position
    home_team_rating_right_att = db.Column(db.Float, nullable=True)
    home_team_rating_mid_att = db.Column(db.Float, nullable=True)
    home_team_rating_left_att = db.Column(db.Float, nullable=True)
    away_team_rating_right_att = db.Column(db.Float, nullable=True)
    away_team_rating_mid_att = db.Column(db.Float, nullable=True)
    away_team_rating_left_att = db.Column(db.Float, nullable=True)

    # Set pieces ratings
    home_team_rating_set_pieces_def = db.Column(db.Float, nullable=True)
    home_team_rating_set_pieces_att = db.Column(db.Float, nullable=True)
    away_team_rating_set_pieces_def = db.Column(db.Float, nullable=True)
    away_team_rating_set_pieces_att = db.Column(db.Float, nullable=True)

    # Arena data
    attendance = db.Column(db.Integer, nullable=True)
    arena_capacity_terraces = db.Column(db.Integer, nullable=True)
    arena_capacity_basic = db.Column(db.Integer, nullable=True)
    arena_capacity_roof = db.Column(db.Integer, nullable=True)
    arena_capacity_vip = db.Column(db.Integer, nullable=True)
    weather_id = db.Column(db.Integer, nullable=True)
    added_minutes = db.Column(db.Integer, nullable=True)

    # Match officials
    referee_id = db.Column(db.Integer, nullable=True)
    referee_name = db.Column(db.String(100), nullable=True)
    referee_country_id = db.Column(db.Integer, nullable=True)
    referee_country = db.Column(db.String(50), nullable=True)
    referee_team_id = db.Column(db.Integer, nullable=True)
    referee_team_name = db.Column(db.String(100), nullable=True)

    # Team details
    home_team_dress_uri = db.Column(db.String(200), nullable=True)
    away_team_dress_uri = db.Column(db.String(200), nullable=True)
    home_team_attitude = db.Column(db.Integer, nullable=True)
    away_team_attitude = db.Column(db.Integer, nullable=True)
    home_team_tactic_type = db.Column(db.Integer, nullable=True)
    home_team_tactic_skill = db.Column(db.Integer, nullable=True)
    away_team_tactic_type = db.Column(db.Integer, nullable=True)
    away_team_tactic_skill = db.Column(db.Integer, nullable=True)

    # Formation data from matchlineup
    home_team_formation = db.Column(db.String(20), nullable=True)
    away_team_formation = db.Column(db.String(20), nullable=True)
    home_team_tactic = db.Column(db.String(50), nullable=True)
    away_team_tactic = db.Column(db.String(50), nullable=True)

    def __init__(self, matchdata):
        self.ht_id = matchdata["ht_id"]
        self.home_team_id = matchdata["home_team_id"]
        self.home_team_name = matchdata["home_team_name"]
        self.away_team_id = matchdata["away_team_id"]
        self.away_team_name = matchdata["away_team_name"]
        self.datetime = matchdata["datetime"]
        self.matchtype = matchdata["matchtype"]
        self.context_id = matchdata["context_id"]
        self.rule_id = matchdata["rule_id"]
        self.cup_level = matchdata["cup_level"]
        self.cup_level_index = matchdata["cup_level_index"]
        self.home_goals = matchdata["home_goals"]
        self.away_goals = matchdata["away_goals"]

        # Enhanced analytics (optional fields)
        self.possession_first_half_home = matchdata.get("possession_first_half_home")
        self.possession_first_half_away = matchdata.get("possession_first_half_away")
        self.possession_second_half_home = matchdata.get("possession_second_half_home")
        self.possession_second_half_away = matchdata.get("possession_second_half_away")
        self.home_team_chances_left = matchdata.get("home_team_chances_left")
        self.home_team_chances_center = matchdata.get("home_team_chances_center")
        self.home_team_chances_right = matchdata.get("home_team_chances_right")
        self.home_team_chances_special = matchdata.get("home_team_chances_special")
        self.home_team_chances_other = matchdata.get("home_team_chances_other")
        self.away_team_chances_left = matchdata.get("away_team_chances_left")
        self.away_team_chances_center = matchdata.get("away_team_chances_center")
        self.away_team_chances_right = matchdata.get("away_team_chances_right")
        self.away_team_chances_special = matchdata.get("away_team_chances_special")
        self.away_team_chances_other = matchdata.get("away_team_chances_other")
        self.home_team_rating = matchdata.get("home_team_rating")
        self.away_team_rating = matchdata.get("away_team_rating")
        self.home_team_rating_right_def = matchdata.get("home_team_rating_right_def")
        self.home_team_rating_mid_def = matchdata.get("home_team_rating_mid_def")
        self.home_team_rating_left_def = matchdata.get("home_team_rating_left_def")
        self.away_team_rating_right_def = matchdata.get("away_team_rating_right_def")
        self.away_team_rating_mid_def = matchdata.get("away_team_rating_mid_def")
        self.away_team_rating_left_def = matchdata.get("away_team_rating_left_def")
        self.home_team_rating_right_att = matchdata.get("home_team_rating_right_att")
        self.home_team_rating_mid_att = matchdata.get("home_team_rating_mid_att")
        self.home_team_rating_left_att = matchdata.get("home_team_rating_left_att")
        self.away_team_rating_right_att = matchdata.get("away_team_rating_right_att")
        self.away_team_rating_mid_att = matchdata.get("away_team_rating_mid_att")
        self.away_team_rating_left_att = matchdata.get("away_team_rating_left_att")
        self.home_team_rating_set_pieces_def = matchdata.get("home_team_rating_set_pieces_def")
        self.home_team_rating_set_pieces_att = matchdata.get("home_team_rating_set_pieces_att")
        self.away_team_rating_set_pieces_def = matchdata.get("away_team_rating_set_pieces_def")
        self.away_team_rating_set_pieces_att = matchdata.get("away_team_rating_set_pieces_att")
        self.attendance = matchdata.get("attendance")
        self.arena_capacity_terraces = matchdata.get("arena_capacity_terraces")
        self.arena_capacity_basic = matchdata.get("arena_capacity_basic")
        self.arena_capacity_roof = matchdata.get("arena_capacity_roof")
        self.arena_capacity_vip = matchdata.get("arena_capacity_vip")
        self.weather_id = matchdata.get("weather_id")
        self.added_minutes = matchdata.get("added_minutes")
        self.referee_id = matchdata.get("referee_id")
        self.referee_name = matchdata.get("referee_name")
        self.referee_country_id = matchdata.get("referee_country_id")
        self.referee_country = matchdata.get("referee_country")
        self.referee_team_id = matchdata.get("referee_team_id")
        self.referee_team_name = matchdata.get("referee_team_name")
        self.home_team_dress_uri = matchdata.get("home_team_dress_uri")
        self.away_team_dress_uri = matchdata.get("away_team_dress_uri")
        self.home_team_attitude = matchdata.get("home_team_attitude")
        self.away_team_attitude = matchdata.get("away_team_attitude")
        self.home_team_tactic_type = matchdata.get("home_team_tactic_type")
        self.home_team_tactic_skill = matchdata.get("home_team_tactic_skill")
        self.away_team_tactic_type = matchdata.get("away_team_tactic_type")
        self.away_team_tactic_skill = matchdata.get("away_team_tactic_skill")
        self.home_team_formation = matchdata.get("home_team_formation")
        self.away_team_formation = matchdata.get("away_team_formation")
        self.home_team_tactic = matchdata.get("home_team_tactic")
        self.away_team_tactic = matchdata.get("away_team_tactic")

    @property
    def home_team_possession(self):
        """Calculate average possession for home team from both halves."""
        if (self.possession_first_half_home is not None and
            self.possession_second_half_home is not None):
            return (self.possession_first_half_home + self.possession_second_half_home) / 2
        return None

    @property
    def away_team_possession(self):
        """Calculate average possession for away team from both halves."""
        if (self.possession_first_half_away is not None and
            self.possession_second_half_away is not None):
            return (self.possession_first_half_away + self.possession_second_half_away) / 2
        return None

    @property
    def home_team_total_chances(self):
        """Calculate total chances for home team (sum of all chance types)."""
        chances = [
            self.home_team_chances_left,
            self.home_team_chances_center,
            self.home_team_chances_right,
            self.home_team_chances_special,
            self.home_team_chances_other
        ]
        if all(c is not None for c in chances):
            return sum(chances)
        return None

    @property
    def away_team_total_chances(self):
        """Calculate total chances for away team (sum of all chance types)."""
        chances = [
            self.away_team_chances_left,
            self.away_team_chances_center,
            self.away_team_chances_right,
            self.away_team_chances_special,
            self.away_team_chances_other
        ]
        if all(c is not None for c in chances):
            return sum(chances)
        return None

    def has_enhanced_data(self):
        """Check if this match has enhanced analytics data.

        Returns True if ANY enhanced field is available.
        Note: CHPP added NrOfChances in v3.1 (March 2022).
        """
        return (self.possession_first_half_home is not None or
                self.home_team_chances_left is not None or
                self.attendance is not None or
                self.home_team_formation or  # Empty string is falsy
                self.home_team_rating is not None)

    def __repr__(self):
        return f"{self.home_team_name} - {self.away_team_name}: {self.ht_id}"


# --------------------------------------------------------------------------------


class PlayerSetting(db.Model):
    __tablename__ = "playersetting"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.ht_id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("playergroup.id"))
    player_id = db.Column(db.Integer, nullable=False)

    def __init__(self, player_id, user_id, group_id):
        self.user_id = user_id
        self.player_id = player_id
        self.group_id = group_id

    def __repr__(self):
        return f"<{self.player_id} {self.group_id}>"


# --------------------------------------------------------------------------------


class Group(db.Model):
    __tablename__ = "playergroup"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.ht_id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    order = db.Column(db.Integer)
    textcolor = db.Column(db.String(100))
    bgcolor = db.Column(db.String(100))

    def __init__(self, user_id, name, order, textcolor, bgcolor):
        self.user_id = user_id
        self.name = name
        self.order = order
        self.textcolor = textcolor
        self.bgcolor = bgcolor

    def __repr__(self):
        return f"<{self.name} {self.order}>"


# --------------------------------------------------------------------------------


class User(db.Model):
    __tablename__ = "users"

    ht_id = db.Column(db.Integer, primary_key=True, unique=True)
    ht_user = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255))  # Increased from 100 to 255 for modern hashing
    access_key = db.Column(db.String(100))
    access_secret = db.Column(db.String(100))
    c_login = db.Column(db.Integer, default=1)
    c_team = db.Column(db.Integer, default=0)
    c_player = db.Column(db.Integer, default=0)
    c_matches = db.Column(db.Integer, default=0)
    c_matches_archive = db.Column(db.Integer, default=0)
    c_training = db.Column(db.Integer, default=0)
    c_update = db.Column(db.Integer, default=0)
    c_settings = db.Column(db.Integer, default=0)
    c_changes = db.Column(db.Integer, default=0)
    c_feedback = db.Column(db.Integer, default=0)
    c_formation = db.Column(db.Integer, default=0)
    c_stats = db.Column(db.Integer, default=0)
    # Tour-specific tracking
    c_welcome_complete = db.Column(db.Integer, default=0)  # Welcome tour completions
    c_welcome_skip = db.Column(db.Integer, default=0)      # Welcome tour skips
    c_welcome_help = db.Column(db.Integer, default=0)      # Welcome tour help clicks
    c_player_complete = db.Column(db.Integer, default=0)   # Player management tour completions
    c_player_skip = db.Column(db.Integer, default=0)       # Player management tour skips
    c_player_help = db.Column(db.Integer, default=0)       # Player management tour help clicks
    c_update_complete = db.Column(db.Integer, default=0)   # Data update tour completions
    c_update_skip = db.Column(db.Integer, default=0)       # Data update tour skips
    c_update_help = db.Column(db.Integer, default=0)       # Data update tour help clicks
    c_tutorial_reset = db.Column(db.Integer, default=0)    # Tutorial progress resets
    last_login = db.Column(db.DateTime)
    last_update = db.Column(db.DateTime)
    last_usage = db.Column(db.DateTime)
    last_matches_archive = db.Column(db.DateTime)
    created = db.Column(db.DateTime)
    role = db.Column(db.String(100))
    player_columns = db.Column(db.PickleType())

    def __init__(self, ht_id, ht_user, username, password, access_key, access_secret):
        self.ht_id = ht_id
        self.ht_user = ht_user
        self.username = username
        self.password = password
        self.access_key = access_key
        self.access_secret = access_secret
        self.c_login = 1
        self.c_team = 0
        self.c_player = 0
        self.c_matches = 0
        self.c_matches_archive = 0
        self.c_training = 0
        self.c_update = 0
        # Initialize tour-specific counters
        self.c_welcome_complete = 0
        self.c_welcome_skip = 0
        self.c_welcome_help = 0
        self.c_player_complete = 0
        self.c_player_skip = 0
        self.c_player_help = 0
        self.c_update_complete = 0
        self.c_update_skip = 0
        self.c_update_help = 0
        self.c_tutorial_reset = 0
        self.last_login = time.strftime("%Y-%m-%d %H:%M:%S")
        self.last_update = time.strftime("%Y-%m-%d %H:%M:%S")
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")
        self.created = time.strftime("%Y-%m-%d %H:%M:%S")
        self.role = ""
        self.player_columns = pickle.dumps([])

    def __repr__(self):
        return f"<id {self.username}>"

    def getRole(self):
        return f"{self.role}"

    def setRole(self, newrole):
        self.role = newrole

    def is_admin(self):
        """Check if user is admin (hardcoded user 182085 + role check)."""
        return self.ht_id == 182085 or self.role == "admin"

    def claimUser(self, username, password, access_key, access_secret):
        self.username = username
        self.password = password
        self.access_key = access_key
        self.access_secret = access_secret
        self.c_login = (self.c_login or 0) + 1
        self.last_login = time.strftime("%Y-%m-%d %H:%M:%S")
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def login(self):
        self.c_login = (self.c_login or 0) + 1
        self.last_login = time.strftime("%Y-%m-%d %H:%M:%S")
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def player(self):
        self.c_player = (self.c_player or 0) + 1
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def matches(self):
        self.c_matches = (self.c_matches or 0) + 1
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def matches_archive(self):
        self.c_matches_archive = (self.c_matches_archive or 0) + 1
        self.last_matches_archive = time.strftime("%Y-%m-%d %H:%M:%S")
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def team(self):
        self.c_team = (self.c_team or 0) + 1
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def training(self):
        self.c_training = (self.c_training or 0) + 1
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def updatedata(self):
        self.c_update = (self.c_update or 0) + 1
        self.last_update = time.strftime("%Y-%m-%d %H:%M:%S")
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def settings(self):
        self.c_settings = (self.c_settings or 0) + 1
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def changes(self):
        self.c_changes = (self.c_changes or 0) + 1
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def feedback(self):
        self.c_feedback = (self.c_feedback or 0) + 1
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def formation(self):
        self.c_formation = (self.c_formation or 0) + 1
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def stats(self):
        self.c_stats = (self.c_stats or 0) + 1
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def updateColumns(self, cols):
        pcols = pickle.dumps(cols)
        self.player_columns = pcols

    def getColumns(self):
        try:
            pcols = pickle.loads(self.player_columns)
            return pcols
        except Exception:
            return []


# --------------------------------------------------------------------------------


class Players(db.Model):
    __tablename__ = "players"

    ht_id = db.Column(db.Integer, primary_key=True)
    data_date = db.Column(db.DateTime, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    nick_name = db.Column(db.String)
    last_name = db.Column(db.String, nullable=False)
    number = db.Column(db.Integer)
    category_id = db.Column(db.Integer)
    owner_notes = db.Column(db.String)
    age_years = db.Column(db.Integer)
    age_days = db.Column(db.Integer)
    age = db.Column(db.String)
    next_birthday = db.Column(db.DateTime)
    arrival_date = db.Column(db.DateTime)
    form = db.Column(db.Integer)
    cards = db.Column(db.Integer)
    injury_level = db.Column(db.Integer)
    statement = db.Column(db.String)
    language = db.Column(db.String)
    language_id = db.Column(db.Integer)
    agreeability = db.Column(db.Integer)
    aggressiveness = db.Column(db.Integer)
    honesty = db.Column(db.Integer)
    experience = db.Column(db.Integer)
    loyalty = db.Column(db.Integer)
    specialty = db.Column(db.Integer)
    native_country_id = db.Column(db.Integer)
    native_league_id = db.Column(db.Integer)
    native_league_name = db.Column(db.String)
    tsi = db.Column(db.Integer)
    salary = db.Column(db.Integer)
    caps = db.Column(db.Integer)
    caps_u20 = db.Column(db.Integer)
    career_goals = db.Column(db.Integer)
    career_hattricks = db.Column(db.Integer)
    league_goals = db.Column(db.Integer)
    cup_goals = db.Column(db.Integer)
    friendly_goals = db.Column(db.Integer)
    current_team_matches = db.Column(db.Integer)
    current_team_goals = db.Column(db.Integer)
    national_team_id = db.Column(db.Integer)
    national_team_name = db.Column(db.String)
    is_transfer_listed = db.Column(db.Boolean)
    team_id = db.Column(db.Integer)
    stamina = db.Column(db.Integer)
    keeper = db.Column(db.Integer)
    defender = db.Column(db.Integer)
    playmaker = db.Column(db.Integer)
    winger = db.Column(db.Integer)
    passing = db.Column(db.Integer)
    scorer = db.Column(db.Integer)
    set_pieces = db.Column(db.Integer)
    owner = db.Column(db.Integer)
    old_owner = db.Column(db.Integer)
    mother_club_bonus = db.Column(db.Boolean)
    leadership = db.Column(db.Integer)

    def __init__(self, playerdata):
        self.ht_id = playerdata["ht_id"]
        self.data_date = time.strftime("%Y-%m-%d")
        self.first_name = playerdata["first_name"]
        self.nick_name = playerdata["nick_name"]
        self.last_name = playerdata["last_name"]
        self.number = playerdata["number"]
        self.category_id = playerdata["category_id"]
        self.owner_notes = playerdata["owner_notes"]
        self.age_years = playerdata["age_years"]
        self.age_days = playerdata["age_days"]
        self.age = str(playerdata["age"])
        self.next_birthday = playerdata["next_birthday"]
        self.arrival_date = playerdata["arrival_date"]
        self.form = playerdata["form"]
        self.cards = playerdata["cards"]
        self.injury_level = playerdata["injury_level"]
        self.statement = playerdata["statement"]
        self.language = playerdata["language"]
        self.language_id = playerdata["language_id"]
        self.agreeability = playerdata["agreeability"]
        self.aggressiveness = playerdata["aggressiveness"]
        self.honesty = playerdata["honesty"]
        self.experience = playerdata["experience"]
        self.loyalty = playerdata["loyalty"]
        self.specialty = playerdata["specialty"]
        self.native_country_id = playerdata["native_country_id"]
        self.native_league_id = playerdata["native_league_id"]
        self.native_league_name = playerdata["native_league_name"]
        self.tsi = playerdata["tsi"]
        self.salary = playerdata["salary"]
        self.caps = playerdata["caps"]
        self.caps_u20 = playerdata["caps_u20"]
        self.career_goals = playerdata["career_goals"]
        self.career_hattricks = playerdata["career_hattricks"]
        self.league_goals = playerdata["league_goals"]
        self.cup_goals = playerdata["cup_goals"]
        self.friendly_goals = playerdata["friendly_goals"]
        self.current_team_matches = playerdata["current_team_matches"]
        self.current_team_goals = playerdata["current_team_goals"]
        self.national_team_id = playerdata["national_team_id"]
        self.national_team_name = playerdata["national_team_name"]
        self.is_transfer_listed = bool(playerdata["is_transfer_listed"])
        self.team_id = playerdata["team_id"]
        self.stamina = int(playerdata["stamina"])
        self.keeper = int(playerdata["keeper"])
        self.defender = int(playerdata["defender"])
        self.playmaker = int(playerdata["playmaker"])
        self.winger = int(playerdata["winger"])
        self.passing = int(playerdata["passing"])
        self.scorer = int(playerdata["scorer"])
        self.set_pieces = int(playerdata["set_pieces"])
        self.owner = playerdata["owner"]
        self.old_owner = 0
        self.mother_club_bonus = bool(playerdata["mother_club_bonus"])
        self.leadership = int(playerdata["leadership"])

    def __repr__(self):
        ret = self.first_name + " " + self.last_name
        ret += " (" + str(self.ht_id) + ")"
        return ret

    def __iter__(self):
        ret = (
            ("ht_id", self.ht_id),
            ("data_date", self.data_date),
            ("first_name", self.first_name),
            ("nick_name", self.nick_name),
            ("last_name", self.last_name),
            ("number", self.number),
            ("category_id", self.category_id),
            ("owner_notes", self.owner_notes),
            ("age_years", self.age_years),
            ("age_days", self.age_days),
            ("age", self.age),
            ("next_birthday", self.next_birthday),
            ("arrival_date", self.arrival_date),
            ("form", self.form),
            ("cards", self.cards),
            ("injury_level", self.injury_level),
            ("statement", self.statement),
            ("language", self.language),
            ("language_id", self.language_id),
            ("agreeability", self.agreeability),
            ("aggressiveness", self.aggressiveness),
            ("honesty", self.honesty),
            ("experience", self.experience),
            ("loyalty", self.loyalty),
            ("specialty", self.specialty),
            ("native_country_id", self.native_country_id),
            ("native_league_id", self.native_league_id),
            ("native_league_name", self.native_league_name),
            ("tsi", self.tsi),
            ("salary", self.salary),
            ("caps", self.caps),
            ("caps_u20", self.caps_u20),
            ("career_goals", self.career_goals),
            ("career_hattricks", self.career_hattricks),
            ("league_goals", self.league_goals),
            ("cup_goals", self.cup_goals),
            ("friendly_goals", self.friendly_goals),
            ("current_team_matches", self.current_team_matches),
            ("current_team_goals", self.current_team_goals),
            ("national_team_id", self.national_team_id),
            ("national_team_name", self.national_team_name),
            ("is_transfer_listed", self.is_transfer_listed),
            ("team_id", self.team_id),
            ("stamina", self.stamina),
            ("keeper", self.keeper),
            ("defender", self.defender),
            ("playmaker", self.playmaker),
            ("winger", self.winger),
            ("passing", self.passing),
            ("scorer", self.scorer),
            ("set_pieces", self.set_pieces),
            ("owner", self.owner),
            ("old_owner", self.old_owner),
            ("mother_club_bonus", self.mother_club_bonus),
            ("leadership", self.leadership),
        )
        return iter(ret)


# --------------------------------------------------------------------------------


class Feedback(db.Model):
    """User feedback submissions for bugs, features, and ideas."""
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    feedback_type = db.Column(db.String(20), nullable=False)  # bug/feature/idea
    status = db.Column(db.String(20), default='open')  # open/planned/in-progress/completed/wont-do
    archived = db.Column(db.Boolean, default=False)  # separate archiving from status
    author_id = db.Column(db.Integer, db.ForeignKey('users.ht_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    vote_score = db.Column(db.Integer, default=0)  # cached vote total for performance

    # Relationships
    author = db.relationship('User', backref='feedback_submissions')
    comments = db.relationship('FeedbackComment', backref='feedback', cascade='all, delete-orphan')
    votes = db.relationship('FeedbackVote', backref='feedback', cascade='all, delete-orphan')

    def __init__(self, title, description, feedback_type, author_id, archived=False):
        self.title = title
        self.description = description
        self.feedback_type = feedback_type
        self.author_id = author_id
        self.archived = archived
        self.status = 'open'  # Set default status explicitly
        self.vote_score = 0   # Set default vote score explicitly

    def __repr__(self):
        return f"<Feedback {self.id}: {self.title[:50]}>"

    def update_vote_score(self):
        """Update cached vote score from actual votes."""
        up_votes = FeedbackVote.query.filter_by(feedback_id=self.id, vote_type='up').count()
        down_votes = FeedbackVote.query.filter_by(feedback_id=self.id, vote_type='down').count()
        self.vote_score = up_votes - down_votes
        db.session.commit()


class FeedbackComment(db.Model):
    """Comments on feedback items."""
    __tablename__ = "feedback_comment"

    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.ht_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    author = db.relationship('User', backref='feedback_comments')

    def __init__(self, feedback_id, author_id, content, is_admin=False):
        self.feedback_id = feedback_id
        self.author_id = author_id
        self.content = content
        self.is_admin = is_admin

    def __repr__(self):
        return f"<FeedbackComment {self.id} on Feedback {self.feedback_id}>"


class FeedbackVote(db.Model):
    """User votes on feedback items."""
    __tablename__ = "feedback_vote"

    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.ht_id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # up/down
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    user = db.relationship('User', backref='feedback_votes')

    # Constraint: one vote per user per feedback item
    __table_args__ = (db.UniqueConstraint('feedback_id', 'user_id', name='unique_user_vote'),)

    def __init__(self, feedback_id, user_id, vote_type):
        self.feedback_id = feedback_id
        self.user_id = user_id
        self.vote_type = vote_type

    def __repr__(self):
        return f"<FeedbackVote {self.vote_type} by User {self.user_id} on Feedback {self.feedback_id}>"


# --------------------------------------------------------------------------------


class Team(db.Model):
    """Model for team information including competition data."""

    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    ht_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    team_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.ht_id"), nullable=False)

    # Competition data - previously fetched via CHPP in stats route
    league_name = db.Column(db.String(200))
    league_level = db.Column(db.Integer)
    power_rating = db.Column(db.Integer)
    cup_still_in_cup = db.Column(db.Boolean)
    cup_cup_name = db.Column(db.String(200))
    cup_cup_round = db.Column(db.String(100))
    cup_cup_round_index = db.Column(db.Integer)
    dress_uri = db.Column(db.String(500))
    logo_url = db.Column(db.String(500))

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = db.relationship("User", backref="teams")

    def __init__(
        self,
        ht_id,
        team_name,
        user_id,
        league_name=None,
        league_level=None,
        power_rating=None,
        cup_still_in_cup=None,
        cup_cup_name=None,
        cup_cup_round=None,
        cup_cup_round_index=None,
        dress_uri=None,
        logo_url=None,
    ):
        self.ht_id = ht_id
        self.team_name = team_name
        self.user_id = user_id
        self.league_name = league_name
        self.league_level = league_level
        self.power_rating = power_rating
        self.cup_still_in_cup = cup_still_in_cup
        self.cup_cup_name = cup_cup_name
        self.cup_cup_round = cup_cup_round
        self.cup_cup_round_index = cup_cup_round_index
        self.dress_uri = dress_uri
        self.logo_url = logo_url

    def __repr__(self):
        return f"<Team {self.ht_id}: {self.team_name}>"

    @staticmethod
    def get_by_ht_id(ht_id):
        """Get team by Hattrick ID."""
        return Team.query.filter_by(ht_id=ht_id).first()

    def update_competition_data(
        self,
        league_name=None,
        league_level=None,
        power_rating=None,
        cup_still_in_cup=None,
        cup_cup_name=None,
        cup_cup_round=None,
        cup_cup_round_index=None,
        dress_uri=None,
        logo_url=None,
    ):
        """Update competition data for the team."""
        if league_name is not None:
            self.league_name = league_name
        if league_level is not None:
            self.league_level = league_level
        if power_rating is not None:
            self.power_rating = power_rating
        if cup_still_in_cup is not None:
            self.cup_still_in_cup = cup_still_in_cup
        if cup_cup_name is not None:
            self.cup_cup_name = cup_cup_name
        if cup_cup_round is not None:
            self.cup_cup_round = cup_cup_round
        if cup_cup_round_index is not None:
            self.cup_cup_round_index = cup_cup_round_index
        if dress_uri is not None:
            self.dress_uri = dress_uri
        if logo_url is not None:
            self.logo_url = logo_url

        self.updated = datetime.utcnow()
        db.session.commit()

# --------------------------------------------------------------------------------


class ErrorLog(db.Model):
    """Log production errors and crashes for debugging purposes."""

    __tablename__ = "error_log"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    error_type = db.Column(db.String(50), nullable=False)  # '500', '404', 'Exception'
    message = db.Column(db.Text)
    stack_trace = db.Column(db.Text)
    user_id = db.Column(db.Integer, nullable=True)  # From session if available
    request_path = db.Column(db.String(500))
    request_method = db.Column(db.String(10))
    user_agent = db.Column(db.String(500))
    environment = db.Column(db.String(50), default='production')

    def __init__(self, error_type, message=None, stack_trace=None, user_id=None,
                 request_path=None, request_method=None, user_agent=None, environment='production'):
        self.error_type = error_type
        self.message = message
        self.stack_trace = stack_trace
        self.user_id = user_id
        self.request_path = request_path
        self.request_method = request_method
        self.user_agent = user_agent
        self.environment = environment

    def __repr__(self):
        return f"<ErrorLog {self.error_type}: {self.message[:50]}... at {self.timestamp}>"

# --------------------------------------------------------------------------------


class TutorialAnalytics(db.Model):
    """Track tutorial usage analytics for debugging and optimization."""
    __tablename__ = "tutorial_analytics"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.ht_id'), nullable=True)  # Nullable for anonymous users
    session_id = db.Column(db.String(255), nullable=False)  # Browser session identifier
    event_type = db.Column(db.String(50), nullable=False)  # 'start', 'complete', 'skip', 'exit', 'help_click', 'reset'
    tour_id = db.Column(db.String(50), nullable=False)  # 'welcome', 'player-management', 'data-update'
    step_number = db.Column(db.Integer, nullable=True)  # Which step (for skips/exits)
    step_duration_seconds = db.Column(db.Float, nullable=True)  # Time spent on step
    total_duration_seconds = db.Column(db.Float, nullable=True)  # Total time in tour
    page_path = db.Column(db.String(255), nullable=False)  # URL path where event occurred
    user_agent = db.Column(db.Text, nullable=True)  # Browser info
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationship to User
    user = db.relationship('User', backref='tutorial_events', lazy=True)

    def __init__(self, session_id, event_type, tour_id, page_path, user_id=None,
                 step_number=None, step_duration_seconds=None, total_duration_seconds=None, user_agent=None):
        self.user_id = user_id
        self.session_id = session_id
        self.event_type = event_type
        self.tour_id = tour_id
        self.step_number = step_number
        self.step_duration_seconds = step_duration_seconds
        self.total_duration_seconds = total_duration_seconds
        self.page_path = page_path
        self.user_agent = user_agent

    def __repr__(self):
        return f"<TutorialAnalytics {self.event_type} {self.tour_id} by user {self.user_id} at {self.timestamp}>"

# --------------------------------------------------------------------------------
