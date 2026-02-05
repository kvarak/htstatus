#!/usr/bin/env python3
"""
Audit ALL data in the database to understand what's there
"""
import sys
from pathlib import Path

from app.factory import create_app
from models import Group, Match, MatchPlay, Players, PlayerSetting, User, db

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def audit_all_data():
    """Audit all data in database"""
    app = create_app()

    with app.app_context():
        print('=== COMPLETE DATABASE AUDIT ===')

        # Users table
        users = User.query.all()
        print(f'\n--- USERS ({len(users)}) ---')
        for user in users:
            print(f'  User {user.ht_id}: {user.username}')

        # Teams (unique team_ids from players)
        teams = db.session.query(Players.team_id).distinct().all()
        team_ids = [t[0] for t in teams]
        print(f'\n--- TEAMS ({len(team_ids)}) ---')
        for team_id in team_ids:
            player_count = Players.query.filter_by(team_id=team_id).count()
            print(f'  Team {team_id}: {player_count} players')

        # All players
        total_players = Players.query.count()
        print(f'\n--- PLAYERS (Total: {total_players}) ---')
        if total_players <= 20:  # Show details if not too many
            players = Players.query.all()
            for player in players:
                print(f'  Player {player.ht_id}: {player.name} (Team {player.team_id})')
        else:
            # Show by team
            for team_id in team_ids:
                count = Players.query.filter_by(team_id=team_id).count()
                print(f'  Team {team_id}: {count} players')

        # Groups
        total_groups = Group.query.count()
        print(f'\n--- GROUPS (Total: {total_groups}) ---')
        groups_by_user = db.session.query(Group.user_id, db.func.count(Group.id)).group_by(Group.user_id).all()
        for user_id, count in groups_by_user:
            print(f'  User {user_id}: {count} groups')

        # Player Settings
        total_settings = PlayerSetting.query.count()
        print(f'\n--- PLAYER SETTINGS (Total: {total_settings}) ---')
        settings_by_user = db.session.query(PlayerSetting.user_id, db.func.count(PlayerSetting.id)).group_by(PlayerSetting.user_id).all()
        for user_id, count in settings_by_user:
            print(f'  User {user_id}: {count} player settings')

        # Matches
        total_matches = Match.query.count()
        print(f'\n--- MATCHES (Total: {total_matches}) ---')
        if total_matches > 0:
            matches_by_team = db.session.query(Match.home_team_id, db.func.count(Match.ht_id)).group_by(Match.home_team_id).all()
            for team_id, count in matches_by_team:
                print(f'  Team {team_id} (home): {count} matches')

            # Also show actual match details for debugging
            all_matches = Match.query.limit(10).all()
            for match in all_matches:
                print(f'    Match {match.ht_id}: {match.home_team_name} vs {match.away_team_name} (Teams: {match.home_team_id} vs {match.away_team_id})')

        # MatchPlay
        total_matchplay = MatchPlay.query.count()
        print(f'\n--- MATCHPLAY (Total: {total_matchplay}) ---')

        print('\n=== SUMMARY ===')
        print(f'Users: {len(users)}')
        print(f'Teams: {len(team_ids)}')
        print(f'Players: {total_players}')
        print(f'Groups: {total_groups}')
        print(f'Settings: {total_settings}')
        print(f'Matches: {total_matches}')
        print(f'MatchPlay: {total_matchplay}')

if __name__ == "__main__":
    audit_all_data()
