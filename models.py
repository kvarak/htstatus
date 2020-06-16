from app import db
from sqlalchemy.dialects.postgresql import JSON
import time

# --------------------------------------------------------------------------------

class User(db.Model):
  __tablename__ = 'users'

  ht_id       = db.Column(db.Integer, primary_key = True)
  ht_user     = db.Column(db.String(100), unique = True)
  username    = db.Column(db.String(100), unique = True)
  password    = db.Column(db.String(100))
  access_key  = db.Column(db.String(100))
  access_secret = db.Column(db.String(100))
  c_login     = db.Column(db.Integer, default = 1)
  c_team      = db.Column(db.Integer, default = 0)
  c_player    = db.Column(db.Integer, default = 0)
  c_matches   = db.Column(db.Integer, default = 0)
  c_training  = db.Column(db.Integer, default = 0)
  c_update    = db.Column(db.Integer, default = 0)
  last_login  = db.Column(db.DateTime)
  last_update = db.Column(db.DateTime)
  last_usage  = db.Column(db.DateTime)
  created     = db.Column(db.DateTime)

  def __init__(self, ht_id, ht_user, username, password, access_key, access_secret):
    self.ht_id       = ht_id
    self.ht_user     = ht_user
    self.username    = username
    self.password    = password
    self.access_key  = access_key
    self.access_secret = access_secret
    self.c_login     = 1
    self.c_team      = 0
    self.c_player    = 0
    self.c_matches   = 0
    self.c_training  = 0
    self.c_update    = 0
    self.last_login  = time.strftime('%Y-%m-%d %H:%M:%S')
    self.last_update = time.strftime('%Y-%m-%d %H:%M:%S')
    self.last_usage  = time.strftime('%Y-%m-%d %H:%M:%S')
    self.created     = time.strftime('%Y-%m-%d %H:%M:%S')

  def __repr__(self):
    return '<id {}>'.format(self.username)

  def claimUser(self, username, password, access_key, access_secret):
    self.username    = username
    self.password    = password
    self.access_key  = access_key
    self.access_secret = access_secret
    self.c_login    += 1
    self.last_login  = time.strftime('%Y-%m-%d %H:%M:%S')
    self.last_usage  = time.strftime('%Y-%m-%d %H:%M:%S')

  def login(self):
    self.c_login += 1
    self.last_login = time.strftime('%Y-%m-%d %H:%M:%S')
    self.last_usage = time.strftime('%Y-%m-%d %H:%M:%S')

  def player(self):
    self.c_player += 1
    self.last_usage = time.strftime('%Y-%m-%d %H:%M:%S')

  def matches(self):
    self.c_matches += 1
    self.last_usage = time.strftime('%Y-%m-%d %H:%M:%S')

  def team(self):
    self.c_team = self.c_team + 1
    self.last_usage = time.strftime('%Y-%m-%d %H:%M:%S')

  def training(self):
    self.c_training += 1
    self.last_usage = time.strftime('%Y-%m-%d %H:%M:%S')

  def updatedata(self):
    self.c_update += 1
    self.last_update = time.strftime('%Y-%m-%d %H:%M:%S')
    self.last_usage  = time.strftime('%Y-%m-%d %H:%M:%S')

# --------------------------------------------------------------------------------

class Players(db.Model):
  __tablename__ = 'players'

  ht_id                = db.Column(db.Integer, primary_key = True)
  data_date            = db.Column(db.DateTime, primary_key = True)
  first_name           = db.Column(db.String)
  nick_name            = db.Column(db.String)
  last_name            = db.Column(db.String)
  number               = db.Column(db.Integer)
  category_id          = db.Column(db.Integer)
  owner_notes          = db.Column(db.String)
  age_years            = db.Column(db.Integer)
  age_days             = db.Column(db.Integer)
  age                  = db.Column(db.String)
  next_birthday        = db.Column(db.DateTime)
  arrival_date         = db.Column(db.DateTime)
  form                 = db.Column(db.Integer)
  cards                = db.Column(db.Integer)
  injury_level         = db.Column(db.Integer)
  statement            = db.Column(db.String)
  language             = db.Column(db.String)
  language_id          = db.Column(db.Integer)
  agreeability         = db.Column(db.Integer)
  aggressiveness       = db.Column(db.Integer)
  honesty              = db.Column(db.Integer)
  experience           = db.Column(db.Integer)
  loyalty              = db.Column(db.Integer)
  specialty            = db.Column(db.Integer)
  native_country_id    = db.Column(db.Integer)
  native_league_id     = db.Column(db.Integer)
  native_league_name   = db.Column(db.String)
  tsi                  = db.Column(db.Integer)
  salary               = db.Column(db.Integer)
  caps                 = db.Column(db.Integer)
  caps_u20             = db.Column(db.Integer)
  career_goals         = db.Column(db.Integer)
  career_hattricks     = db.Column(db.Integer)
  league_goals         = db.Column(db.Integer)
  cup_goals            = db.Column(db.Integer)
  friendly_goals       = db.Column(db.Integer)
  current_team_matches = db.Column(db.Integer)
  current_team_goals   = db.Column(db.Integer)
  national_team_id     = db.Column(db.Integer)
  national_team_name   = db.Column(db.String)
  is_transfer_listed   = db.Column(db.Boolean)
  team_id              = db.Column(db.Integer)
  stamina              = db.Column(db.Integer)
  keeper               = db.Column(db.Integer)
  defender             = db.Column(db.Integer)
  playmaker            = db.Column(db.Integer)
  winger               = db.Column(db.Integer)
  passing              = db.Column(db.Integer)
  scorer               = db.Column(db.Integer)
  set_pieces           = db.Column(db.Integer)
  owner                = db.Column(db.Integer)

  def __init__(self, playerdata):
    self.ht_id                = playerdata['ht_id']
    self.data_date            = time.strftime('%Y-%m-%d')
    self.first_name           = playerdata['first_name']
    self.nick_name            = playerdata['nick_name']
    self.last_name            = playerdata['last_name']
    self.number               = playerdata['number']
    self.category_id          = playerdata['category_id']
    self.owner_notes          = playerdata['owner_notes']
    self.age_years            = playerdata['age_years']
    self.age_days             = playerdata['age_days']
    self.age                  = str(playerdata['age'])
    self.next_birthday        = playerdata['next_birthday']
    self.arrival_date         = playerdata['arrival_date']
    self.form                 = playerdata['form']
    self.cards                = playerdata['cards']
    self.injury_level         = playerdata['injury_level']
    self.statement            = playerdata['statement']
    self.language             = playerdata['language']
    self.language_id          = playerdata['language_id']
    self.agreeability         = playerdata['agreeability']
    self.aggressiveness       = playerdata['aggressiveness']
    self.honesty              = playerdata['honesty']
    self.experience           = playerdata['experience']
    self.loyalty              = playerdata['loyalty']
    self.specialty            = playerdata['specialty']
    self.native_country_id    = playerdata['native_country_id']
    self.native_league_id     = playerdata['native_league_id']
    self.native_league_name   = playerdata['native_league_name']
    self.tsi                  = playerdata['tsi']
    self.salary               = playerdata['salary']
    self.caps                 = playerdata['caps']
    self.caps_u20             = playerdata['caps_u20']
    self.career_goals         = playerdata['career_goals']
    self.career_hattricks     = playerdata['career_hattricks']
    self.league_goals         = playerdata['league_goals']
    self.cup_goals            = playerdata['cup_goals']
    self.friendly_goals       = playerdata['friendly_goals']
    self.current_team_matches = playerdata['current_team_matches']
    self.current_team_goals   = playerdata['current_team_goals']
    self.national_team_id     = playerdata['national_team_id']
    self.national_team_name   = playerdata['national_team_name']
    self.is_transfer_listed   = playerdata['is_transfer_listed']
    self.team_id              = playerdata['team_id']
    self.stamina              = int(playerdata['stamina'])
    self.keeper               = int(playerdata['keeper'])
    self.defender             = int(playerdata['defender'])
    self.playmaker            = int(playerdata['playmaker'])
    self.winger               = int(playerdata['winger'])
    self.passing              = int(playerdata['passing'])
    self.scorer               = int(playerdata['scorer'])
    self.set_pieces           = int(playerdata['set_pieces'])
    self.owner                = playerdata['owner']

  def __repr__(self):
    ret = "<name " + self.first_name
    return ret

  def __iter__(self):
    ret = (("ht_id", self.ht_id),
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
            ("owner", self.owner))
    return iter(ret)

# --------------------------------------------------------------------------------
