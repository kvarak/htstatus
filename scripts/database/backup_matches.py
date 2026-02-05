#!/usr/bin/env python3
"""
Manual Match Data Backup Utility

Creates a backup of all match data for safety before database operations.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.factory import create_app
from models import Match


def create_match_backup():
    """Create a comprehensive backup of all match data."""
    print("=== CREATING MATCH BACKUP ===")

    app = create_app()
    with app.app_context():
        matches = Match.query.order_by(Match.datetime).all()

        backup_data = {
            'backup_timestamp': datetime.now().isoformat(),
            'total_matches': len(matches),
            'backup_type': 'manual',
            'matches': []
        }

        for match in matches:
            match_data = {
                'ht_id': match.ht_id,
                'home_team_id': match.home_team_id,
                'home_team_name': match.home_team_name,
                'away_team_id': match.away_team_id,
                'away_team_name': match.away_team_name,
                'datetime': match.datetime.isoformat() if match.datetime else None,
                'matchtype': match.matchtype,
                'context_id': match.context_id,
                'rule_id': match.rule_id,
                'cup_level': match.cup_level,
                'cup_level_index': match.cup_level_index,
                'home_goals': match.home_goals,
                'away_goals': match.away_goals
            }
            backup_data['matches'].append(match_data)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"scripts/database/backups/matches_manual_backup_{timestamp}.json"

    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2)

    print(f"✅ Manual backup created: {backup_file}")
    print(f"   Total matches: {backup_data['total_matches']}")

    return backup_file

if __name__ == "__main__":
    create_match_backup()
