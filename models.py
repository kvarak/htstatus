from app import db
from sqlalchemy.dialects.postgresql import JSON
import time

class Usage(db.Model):
  __tablename__ = 'usage'

  user_id    = db.Column(db.Integer, primary_key = True)
  c_login    = db.Column(db.Integer)
  c_team     = db.Column(db.Integer)
  c_player   = db.Column(db.Integer)
  c_matches  = db.Column(db.Integer)
  c_training = db.Column(db.Integer)
  last_login = db.Column(db.DateTime)
  last_usage = db.Column(db.DateTime)

  def __init__(self, user_id, c_login = 1, c_team = 0, c_player = 0, c_matches = 0, c_training = 0):
    self.user_id = user_id
    self.c_login = c_login
    self.c_team = c_team
    self.c_player = c_player
    self.c_matches = c_matches
    self.c_training = c_training
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
