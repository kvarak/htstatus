import pickle
import time

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
    c_training = db.Column(db.Integer, default=0)
    c_update = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime)
    last_update = db.Column(db.DateTime)
    last_usage = db.Column(db.DateTime)
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
        self.c_training = 0
        self.c_update = 0
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
        self.c_login += 1
        self.last_login = time.strftime("%Y-%m-%d %H:%M:%S")
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def login(self):
        self.c_login += 1
        self.last_login = time.strftime("%Y-%m-%d %H:%M:%S")
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def player(self):
        self.c_player += 1
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def matches(self):
        self.c_matches += 1
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def team(self):
        self.c_team = self.c_team + 1
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def training(self):
        self.c_training += 1
        self.last_usage = time.strftime("%Y-%m-%d %H:%M:%S")

    def updatedata(self):
        self.c_update += 1
        self.last_update = time.strftime("%Y-%m-%d %H:%M:%S")
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
