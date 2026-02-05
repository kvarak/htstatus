#!/usr/bin/env python3
"""
Clean Historical Matches - Give All Teams a Clean Slate

Purpose: Remove all matches older than 2024 to align with CHPP's 2-season limitation
and eliminate confusing historical data from inactive team periods.

Background: CHPP API only allows downloading ~2 seasons of match data. Having
historical data from 2005 mixed with current data creates user confusion when
teams were inactive for years and then reactivated with different names.

This script:
1. Creates a safety backup of match data
2. Removes all matches before 2024-01-01
3. Keeps recent matches (2024-2026) that align with CHPP download capability
4. Provides detailed logging and rollback capability

Safety: Non-destructive operation with backup and rollback support.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add app directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


from app.factory import create_app
from models import Match, db


def create_backup():
    """Create a backup of match data before cleanup."""
    print("=== CREATING BACKUP ===")

    app = create_app()
    with app.app_context():
        # Get all matches with metadata
        matches = Match.query.order_by(Match.datetime).all()

        backup_data = {
            'backup_timestamp': datetime.now().isoformat(),
            'total_matches': len(matches),
            'script_version': '1.0',
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

    # Save backup file with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"scripts/database/backups/matches_backup_{timestamp}.json"

    # Ensure backup directory exists
    os.makedirs(os.path.dirname(backup_file), exist_ok=True)

    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2)

    print(f"✅ Backup created: {backup_file}")
    print(f"   Total matches backed up: {backup_data['total_matches']}")

    return backup_file

def analyze_cleanup_impact():
    """Analyze what will be deleted and what will be kept."""
    print("\n=== ANALYZING CLEANUP IMPACT ===")

    app = create_app()
    with app.app_context():
        cutoff_date = '2024-01-01'

        # Count matches to delete
        old_matches = Match.query.filter(Match.datetime < cutoff_date).all()
        recent_matches = Match.query.filter(Match.datetime >= cutoff_date).all()

        print(f"Cutoff date: {cutoff_date}")
        print(f"Matches to DELETE: {len(old_matches)} (pre-2024)")
        print(f"Matches to KEEP: {len(recent_matches)} (2024-2026)")

        # Show year breakdown of what gets deleted
        years_to_delete = {}
        for match in old_matches:
            year = match.datetime.year if match.datetime else 'Unknown'
            years_to_delete[year] = years_to_delete.get(year, 0) + 1

        print("\nDeletion breakdown by year:")
        for year, count in sorted(years_to_delete.items()):
            print(f"  {year}: {count} matches")

        # Show sample of what gets deleted
        print("\nSample matches to be deleted (showing first 5):")
        for match in old_matches[:5]:
            date_str = match.datetime.strftime('%Y-%m-%d') if match.datetime else 'No date'
            print(f"  {date_str}: {match.home_team_name} vs {match.away_team_name}")

        if len(old_matches) > 5:
            print(f"  ... and {len(old_matches) - 5} more")

        return len(old_matches), len(recent_matches)

def perform_cleanup():
    """Perform the actual cleanup operation."""
    print("\n=== PERFORMING CLEANUP ===")

    app = create_app()
    with app.app_context():
        cutoff_date = '2024-01-01'

        # Delete old matches
        old_matches = Match.query.filter(Match.datetime < cutoff_date)
        deleted_count = old_matches.count()

        print(f"Deleting {deleted_count} matches older than {cutoff_date}...")

        # Use ORM for safe bulk delete (table name is 'match', not 'matches')
        deleted_count = old_matches.count()
        old_matches.delete()

        db.session.commit()

        print(f"✅ Successfully deleted {deleted_count} matches")
        # Verify cleanup
        remaining_old = Match.query.filter(Match.datetime < cutoff_date).count()
        remaining_recent = Match.query.filter(Match.datetime >= cutoff_date).count()

        print("Verification:")
        print(f"  Remaining old matches (should be 0): {remaining_old}")
        print(f"  Remaining recent matches: {remaining_recent}")

        if remaining_old > 0:
            print("⚠️  WARNING: Some old matches still remain!")
            return False
        else:
            print("✅ Cleanup completed successfully!")
            return True

def create_rollback_script(backup_file):
    """Create a rollback script for emergency recovery."""
    rollback_script = f"""#!/usr/bin/env python3
# EMERGENCY ROLLBACK SCRIPT
# Generated by clean_historical_matches.py
#
# Usage: python scripts/database/rollback_match_cleanup.py
#
# This script restores matches from backup: {backup_file}

import sys
import json
from pathlib import Path
from datetime import datetime

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models import Match, db
from app.factory import create_app

def rollback_matches():
    print("=== EMERGENCY MATCH ROLLBACK ===")
    print("Backup file: {backup_file}")

    # Load backup
    with open('{backup_file}', 'r') as f:
        backup_data = json.load(f)

    app = create_app()
    with app.app_context():
        print(f"Restoring {{backup_data['total_matches']}} matches...")

        # Clear existing matches (if any)
        existing_count = Match.query.count()
        if existing_count > 0:
            print(f"Clearing {{existing_count}} existing matches...")
            Match.query.delete()

        # Restore matches from backup
        restored_count = 0
        for match_data in backup_data['matches']:
            match = Match(
                ht_id=match_data['ht_id'],
                home_team_id=match_data['home_team_id'],
                home_team_name=match_data['home_team_name'],
                away_team_id=match_data['away_team_id'],
                away_team_name=match_data['away_team_name'],
                datetime=datetime.fromisoformat(match_data['datetime']) if match_data['datetime'] else None,
                matchtype=match_data['matchtype'],
                context_id=match_data['context_id'],
                rule_id=match_data['rule_id'],
                cup_level=match_data['cup_level'],
                cup_level_index=match_data['cup_level_index'],
                home_goals=match_data['home_goals'],
                away_goals=match_data['away_goals']
            )
            db.session.add(match)
            restored_count += 1

            if restored_count % 50 == 0:
                print(f"  Progress: {{restored_count}}/{{backup_data['total_matches']}} matches restored...")

        db.session.commit()

        final_count = Match.query.count()
        print(f"✅ Rollback completed!")
        print(f"   Expected matches: {{backup_data['total_matches']}}")
        print(f"   Actual matches: {{final_count}}")

if __name__ == "__main__":
    rollback_matches()
"""

    rollback_file = "scripts/database/rollback_match_cleanup.py"
    with open(rollback_file, 'w') as f:
        f.write(rollback_script)

    print(f"✅ Rollback script created: {rollback_file}")
    return rollback_file

def main():
    """Main cleanup process."""
    print("=" * 60)
    print("HISTORICAL MATCHES CLEANUP")
    print("=" * 60)
    print("Purpose: Remove pre-2024 matches to give all teams a clean slate")
    print("Scope: Aligns with CHPP's 2-season download limitation")
    print("Safety: Full backup and rollback capability provided")
    print("=" * 60)

    try:
        # Step 1: Analyze impact
        old_count, recent_count = analyze_cleanup_impact()

        if old_count == 0:
            print("\n✅ No old matches to clean up! Database is already clean.")
            return

        # Step 2: Confirm operation
        print("\nThis operation will:")
        print(f"  ❌ DELETE {old_count} historical matches (pre-2024)")
        print(f"  ✅ KEEP {recent_count} recent matches (2024-2026)")
        print("  💾 CREATE full backup for rollback capability")

        response = input("\nProceed with cleanup? (yes/no): ").lower().strip()
        if response not in ['yes', 'y']:
            print("❌ Operation cancelled by user.")
            return

        # Step 3: Create backup
        backup_file = create_backup()

        # Step 4: Create rollback script
        rollback_file = create_rollback_script(backup_file)

        # Step 5: Perform cleanup
        success = perform_cleanup()

        if success:
            print("\n🎉 CLEANUP COMPLETED SUCCESSFULLY!")
            print("   All teams now have a clean slate with recent matches only")
            print(f"   Backup available: {backup_file}")
            print(f"   Emergency rollback: python {rollback_file}")
        else:
            print("\n❌ CLEANUP FAILED!")
            print("   Check the error messages above")
            print(f"   Backup available for rollback: {backup_file}")

    except Exception as e:
        print(f"\n💥 ERROR during cleanup: {e}")
        print("   Operation may be partially completed")
        print("   Use rollback script if needed")
        raise

if __name__ == "__main__":
    main()
