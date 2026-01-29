#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.factory import create_app
from models import *

app = create_app()
with app.app_context():
    print('=== YOUR USER/TEAM ANALYSIS ===')

    # Check your user
    user = User.query.filter_by(ht_id=182085).first()
    if user:
        print(f'Your user found: {user.username}')

    # Check for players with your team_id
    players_with_team = Players.query.filter_by(team_id=9838).all()
    print(f'Players with team_id=9838: {len(players_with_team)}')

    # Check for players with None team_id that might be yours
    players_no_team = Players.query.filter_by(team_id=None).count()
    print(f'Players with team_id=None: {players_no_team}')

    # Check if any players are associated with your user through PlayerSetting
    your_settings = PlayerSetting.query.filter_by(user_id=182085).all()
    print(f'Your player settings: {len(your_settings)}')

    if your_settings:
        player_ids = [s.player_id for s in your_settings]
        your_players = Players.query.filter(Players.ht_id.in_(player_ids)).all()
        print(f'Your actual players: {len(your_players)}')
        if your_players:
            team_ids = set([p.team_id for p in your_players[:5]])
            print(f'Sample player team_ids: {team_ids}')
