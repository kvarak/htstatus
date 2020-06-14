from app import db
from sqlalchemy.dialects.postgresql import JSON
import time

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
    return '<name {}>'.format(self.last_name)

class Usage(db.Model):
  __tablename__ = 'usage'

  user_id    = db.Column(db.Integer, primary_key = True)
  c_login    = db.Column(db.Integer, default = 0)
  c_team     = db.Column(db.Integer, default = 0)
  c_player   = db.Column(db.Integer, default = 0)
  c_matches  = db.Column(db.Integer, default = 0)
  c_training = db.Column(db.Integer, default = 0)
  c_update   = db.Column(db.Integer, default = 0)
  last_login = db.Column(db.DateTime)
  last_usage = db.Column(db.DateTime)

  def __init__(self, user_id, c_login = 1, c_team = 0, c_player = 0, c_matches = 0, c_training = 0, c_update = 0):
    self.user_id = user_id
    self.c_login = c_login
    self.c_team = c_team
    self.c_player = c_player
    self.c_matches = c_matches
    self.c_training = c_training
    self.c_update = c_update
    self.last_login = time.strftime('%Y-%m-%d %H:%M:%S')
    self.last_usage = time.strftime('%Y-%m-%d %H:%M:%S')

  def __repr__(self):
    return '<id {}>'.format(self.user_id)

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
    self.last_usage = time.strftime('%Y-%m-%d %H:%M:%S')
