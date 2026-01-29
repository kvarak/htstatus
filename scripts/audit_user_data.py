#!/usr/bin/env python3
"""
Audit all data for a specific user and team
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.factory import create_app
from models import *


def audit_user_data(user_id, team_id):
    """Audit all data for specific user and team"""
    app = create_app()

    with app.app_context():
        print('=== USER DATA AUDIT ===')

        # Users table
        user = User.query.filter_by(ht_id=user_id).first()
        if user:
            print(f'User found: {user.username}')
        else:
            print('No user record found')

        # Players for team
        players = Players.query.filter_by(team_id=team_id).count()
        print(f'Players for team {team_id}: {players}')

        # Groups for user
        groups = Group.query.filter_by(user_id=user_id).count()
        print(f'Groups for user {user_id}: {groups}')

        # Player settings for user
        settings = PlayerSetting.query.filter_by(user_id=user_id).count()
        print(f'Player settings for user {user_id}: {settings}')

        # Check Match table for home/away team
        home_matches = Match.query.filter_by(home_team_id=team_id).count()
        away_matches = Match.query.filter_by(away_team_id=team_id).count()
        print(f'Matches as home team: {home_matches}')
        print(f'Matches as away team: {away_matches}')

        # Check MatchPlay for players from this team - get player IDs first
        team_players = Players.query.filter_by(team_id=team_id).all()
        player_ids = [p.ht_id for p in team_players]

        if player_ids:
            matchplay_count = MatchPlay.query.filter(MatchPlay.player_id.in_(player_ids)).count()
            print(f'MatchPlay records for team players: {matchplay_count}')
        else:
            print('MatchPlay records for team players: 0')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python audit_user_data.py <user_id> <team_id>")
        sys.exit(1)

    user_id = int(sys.argv[1])
    team_id = int(sys.argv[2])

    audit_user_data(user_id, team_id)
