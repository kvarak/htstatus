#!/usr/bin/env python3
"""
Enhanced database cleanup script for specific user and team data
Improved to handle historical player records, orphaned data, and comprehensive cleanup
Used for testing default groups functionality on fresh user data
"""
import sys
from pathlib import Path

import psycopg2

# Add project root to path to import config
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def read_config():
    """Read database configuration from config.py"""
    try:
        # Import the config module directly
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", project_root / "config.py")
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)

        # Get the config class and instantiate it
        config_obj = config_module.Config()
        return config_obj.SQLALCHEMY_DATABASE_URI

    except Exception as e:
        print(f"Error reading config: {e}")
        return None


def parse_database_url(url):
    """Parse PostgreSQL URL into connection parameters"""
    # Format: postgresql://user:password@host:port/database
    if not url.startswith('postgresql://'):
        raise ValueError("Invalid DATABASE_URL format")

    url = url.replace('postgresql://', '')

    if '@' in url:
        credentials, host_part = url.split('@', 1)
        if ':' in credentials:
            user, password = credentials.split(':', 1)
        else:
            user, password = credentials, ''
    else:
        user, password, host_part = '', '', url

    if '/' in host_part:
        host_port, database = host_part.split('/', 1)
        if ':' in host_port:
            host, port = host_port.split(':', 1)
            port = int(port)
        else:
            host, port = host_port, 5432
    else:
        host, port, database = host_part, 5432, ''

    return {
        'host': host,
        'port': port,
        'database': database,
        'user': user,
        'password': password
    }


def cleanup_user_data(user_id, team_id):
    """Enhanced cleanup of all user data including historical and orphaned records"""
    database_url = read_config()
    if not database_url:
        print("Failed to read database configuration")
        return False

    try:
        db_params = parse_database_url(database_url)
        print(f"Connecting to database: {db_params['host']}:{db_params['port']}/{db_params['database']}")

        # Connect to database
        conn = psycopg2.connect(
            host=db_params['host'],
            port=db_params['port'],
            database=db_params['database'],
            user=db_params['user'],
            password=db_params['password']
        )

        conn.autocommit = False  # Use transaction
        cur = conn.cursor()

        print(f"🔍 Enhanced cleanup for user {user_id} and team {team_id}")
        print("="*60)

        # Step 1: Comprehensive data discovery
        print("DISCOVERY PHASE:")
        print("-" * 30)

        # Count current team players
        cur.execute("SELECT COUNT(*) FROM players WHERE team_id = %s", (team_id,))
        current_team_players_count = cur.fetchone()[0]
        print(f"Players in current team {team_id}: {current_team_players_count}")

        # Count user settings and extract player IDs
        cur.execute("SELECT COUNT(*) FROM playersetting WHERE user_id = %s", (user_id,))
        settings_count = cur.fetchone()[0]
        print(f"Player settings for user {user_id}: {settings_count}")

        # Get ALL player IDs that might be related to this user
        current_team_player_ids = []
        if current_team_players_count > 0:
            cur.execute("SELECT ht_id FROM players WHERE team_id = %s", (team_id,))
            current_team_player_ids = [row[0] for row in cur.fetchall()]

        settings_player_ids = []
        if settings_count > 0:
            cur.execute("SELECT DISTINCT player_id FROM playersetting WHERE user_id = %s", (user_id,))
            settings_player_ids = [row[0] for row in cur.fetchall()]

        # Combine all player IDs (deduplicated)
        all_related_player_ids = list(set(current_team_player_ids + settings_player_ids))
        print(f"Total unique player IDs to clean: {len(all_related_player_ids)}")

        # Count historical records for these players
        historical_player_records = 0
        if all_related_player_ids:
            placeholders = ','.join(['%s'] * len(all_related_player_ids))
            cur.execute(f"SELECT COUNT(*) FROM players WHERE ht_id IN ({placeholders})", all_related_player_ids)
            historical_player_records = cur.fetchone()[0]
        print(f"Historical player records (all dates): {historical_player_records}")

        # Count orphaned players (team_id = NULL)
        cur.execute("SELECT COUNT(*) FROM players WHERE team_id IS NULL")
        orphaned_players = cur.fetchone()[0]
        print(f"Orphaned players (team_id = NULL): {orphaned_players}")

        # Count other data
        cur.execute("SELECT COUNT(*) FROM playergroup WHERE user_id = %s", (user_id,))
        group_count = cur.fetchone()[0]
        print(f"Groups for user {user_id}: {group_count}")

        cur.execute("SELECT COUNT(*) FROM users WHERE ht_id = %s", (user_id,))
        user_count = cur.fetchone()[0]
        print(f"User records: {user_count}")

        cur.execute("SELECT COUNT(*) FROM match WHERE home_team_id = %s OR away_team_id = %s", (team_id, team_id))
        match_count = cur.fetchone()[0]
        print(f"Matches involving team {team_id}: {match_count}")

        # Count MatchPlay for all related players
        matchplay_count = 0
        if all_related_player_ids:
            placeholders = ','.join(['%s'] * len(all_related_player_ids))
            cur.execute(f"SELECT COUNT(*) FROM matchplay WHERE player_id IN ({placeholders})", all_related_player_ids)
            matchplay_count = cur.fetchone()[0]
        print(f"MatchPlay records for related players: {matchplay_count}")

        print("\n" + "="*60)
        print("CLEANUP OPERATIONS:")
        print("="*60)

        # Step 2: Delete MatchPlay records (must be first due to foreign keys)
        deleted_matchplay = 0
        if all_related_player_ids:
            print("🗑️  Removing MatchPlay records for ALL related players...")
            placeholders = ','.join(['%s'] * len(all_related_player_ids))
            cur.execute(f"DELETE FROM matchplay WHERE player_id IN ({placeholders})", all_related_player_ids)
            deleted_matchplay = cur.rowcount
            print(f"   Deleted {deleted_matchplay} MatchPlay records")

        # Step 3: Delete match records involving this team
        print("🗑️  Removing matches involving team...")
        cur.execute("DELETE FROM match WHERE home_team_id = %s OR away_team_id = %s", (team_id, team_id))
        deleted_matches = cur.rowcount
        print(f"   Deleted {deleted_matches} match records")

        # Step 4: Delete ALL player settings for this user
        print("🗑️  Removing ALL player settings for user...")
        cur.execute("DELETE FROM playersetting WHERE user_id = %s", (user_id,))
        deleted_settings = cur.rowcount
        print(f"   Deleted {deleted_settings} player settings")

        # Step 5: Delete ALL groups for user
        print("🗑️  Removing ALL user groups...")
        cur.execute("DELETE FROM playergroup WHERE user_id = %s", (user_id,))
        deleted_groups = cur.rowcount
        print(f"   Deleted {deleted_groups} groups")

        # Step 6: Delete ALL historical player records for related players
        print("🗑️  Removing ALL historical player records...")
        deleted_historical_players = 0
        if all_related_player_ids:
            placeholders = ','.join(['%s'] * len(all_related_player_ids))
            cur.execute(f"DELETE FROM players WHERE ht_id IN ({placeholders})", all_related_player_ids)
            deleted_historical_players = cur.rowcount
            print(f"   Deleted {deleted_historical_players} historical player records")

        # Step 7: Clean up orphaned players
        print("🗑️  Removing orphaned player records...")
        cur.execute("DELETE FROM players WHERE team_id IS NULL")
        deleted_orphaned = cur.rowcount
        print(f"   Deleted {deleted_orphaned} orphaned player records")

        # Step 8: Delete the user record itself
        print("🗑️  Removing user record...")
        cur.execute("DELETE FROM users WHERE ht_id = %s", (user_id,))
        deleted_user = cur.rowcount
        print(f"   Deleted {deleted_user} user record")

        # Summary
        print("\n" + "="*60)
        print("CLEANUP SUMMARY:")
        print("="*60)
        print(f"✅ MatchPlay records: {deleted_matchplay}")
        print(f"✅ Match records: {deleted_matches}")
        print(f"✅ Player settings: {deleted_settings}")
        print(f"✅ User groups: {deleted_groups}")
        print(f"✅ Historical players: {deleted_historical_players}")
        print(f"✅ Orphaned players: {deleted_orphaned}")
        print(f"✅ User records: {deleted_user}")

        # Ask for confirmation
        print("\n" + "⚠️  WARNING: This will permanently delete all the data listed above!")
        response = input("Do you want to commit these changes? (yes/no): ").lower()

        if response == 'yes':
            conn.commit()
            print("\n🎉 Changes committed successfully!")

            # Comprehensive verification
            print("\n" + "="*60)
            print("VERIFICATION:")
            print("="*60)

            # Check remaining data
            cur.execute("SELECT COUNT(*) FROM playersetting WHERE user_id = %s", (user_id,))
            remaining_settings = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM playergroup WHERE user_id = %s", (user_id,))
            remaining_groups = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM users WHERE ht_id = %s", (user_id,))
            remaining_users = cur.fetchone()[0]

            # Check remaining players
            remaining_players = 0
            if all_related_player_ids:
                placeholders = ','.join(['%s'] * len(all_related_player_ids))
                cur.execute(f"SELECT COUNT(*) FROM players WHERE ht_id IN ({placeholders})", all_related_player_ids)
                remaining_players = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM players WHERE team_id = %s", (team_id,))
            remaining_team_players = cur.fetchone()[0]

            print(f"Remaining player settings: {remaining_settings}")
            print(f"Remaining groups: {remaining_groups}")
            print(f"Remaining users: {remaining_users}")
            print(f"Remaining related players: {remaining_players}")
            print(f"Remaining team players: {remaining_team_players}")

            if all([remaining_settings == 0, remaining_groups == 0, remaining_users == 0,
                   remaining_players == 0, remaining_team_players == 0]):
                print("\n🎉 PERFECT! All user data has been completely removed.")
                print("✅ Ready for fresh user testing!")
            else:
                print("\n⚠️  Some data may still remain - check the counts above.")

            return True
        else:
            print("\n❌ Changes rolled back - no data was deleted.")
            conn.rollback()
            return False

    except psycopg2.Error as e:
        print(f"\n💥 Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    except Exception as e:
        print(f"\n💥 Error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Enhanced Database Cleanup Script")
        print("Usage: uv run python cleanup_user_data.py <user_id> <team_id>")
        print("Example: uv run python cleanup_user_data.py 182085 9838")
        print("\nThis script will remove:")
        print("- All player records (including historical)")
        print("- All user groups and settings")
        print("- All matches and matchplay data")
        print("- Orphaned player records")
        print("- The user record itself")
        sys.exit(1)

    try:
        user_id = int(sys.argv[1])
        team_id = int(sys.argv[2])
    except ValueError:
        print("Error: user_id and team_id must be integers")
        sys.exit(1)

    print("🗑️  Enhanced Database Cleanup Script")
    print(f"User ID: {user_id}")
    print(f"Team ID: {team_id}")
    print("="*40)
    print()

    success = cleanup_user_data(user_id, team_id)
    sys.exit(0 if success else 1)
