#!/usr/bin/env python3
"""
Database cleanup script for specific user and team data
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
        host_port, database = host_part.rsplit('/', 1)
    else:
        host_port, database = host_part, ''

    if ':' in host_port:
        host, port = host_port.rsplit(':', 1)
        port = int(port)
    else:
        host, port = host_port, 5432

    return {
        'host': host,
        'port': port,
        'database': database,
        'user': user,
        'password': password
    }

def cleanup_user_data(user_id, team_id):
    """Clean up all data for specified user and team"""

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

        print(f"Starting cleanup for user {user_id} and team {team_id}")

        # Step 1: Count current data
        cur.execute("SELECT COUNT(*) FROM players WHERE team_id = %s", (team_id,))
        player_count = cur.fetchone()[0]
        print(f"Found {player_count} players in team {team_id}")

        cur.execute("SELECT COUNT(*) FROM playergroup WHERE user_id = %s", (user_id,))
        group_count = cur.fetchone()[0]
        print(f"Found {group_count} groups for user {user_id}")

        cur.execute("SELECT COUNT(*) FROM users WHERE ht_id = %s", (user_id,))
        user_count = cur.fetchone()[0]
        print(f"Found {user_count} user records for user {user_id}")

        cur.execute("SELECT COUNT(*) FROM match WHERE home_team_id = %s OR away_team_id = %s", (team_id, team_id))
        match_count = cur.fetchone()[0]
        print(f"Found {match_count} matches involving team {team_id}")

        # Get player IDs for MatchPlay cleanup
        cur.execute("SELECT ht_id FROM players WHERE team_id = %s", (team_id,))
        player_ids = [row[0] for row in cur.fetchall()]

        matchplay_count = 0
        if player_ids:
            # Create placeholders for IN clause
            placeholders = ','.join(['%s'] * len(player_ids))
            cur.execute(f"SELECT COUNT(*) FROM matchplay WHERE player_id IN ({placeholders})", player_ids)
            matchplay_count = cur.fetchone()[0]
        print(f"Found {matchplay_count} matchplay records for team players")

        # Step 2: Delete MatchPlay records for team players (must be first due to foreign keys)
        deleted_matchplay = 0
        if player_ids:
            print("Removing matchplay records for team players...")
            placeholders = ','.join(['%s'] * len(player_ids))
            cur.execute(f"DELETE FROM matchplay WHERE player_id IN ({placeholders})", player_ids)
            deleted_matchplay = cur.rowcount
            print(f"Deleted {deleted_matchplay} matchplay records")

        # Step 3: Delete match records involving this team
        print("Removing matches involving team...")
        cur.execute("DELETE FROM match WHERE home_team_id = %s OR away_team_id = %s", (team_id, team_id))
        deleted_matches = cur.rowcount
        print(f"Deleted {deleted_matches} match records")

        # Step 4: Delete player settings associations
        print("Removing all player settings for user...")
        cur.execute("DELETE FROM playersetting WHERE user_id = %s", (user_id,))
        deleted_associations = cur.rowcount
        print(f"Deleted {deleted_associations} player settings for user {user_id}")

        # Step 5: Delete groups for user
        print("Removing user groups...")
        cur.execute("DELETE FROM playergroup WHERE user_id = %s", (user_id,))
        deleted_groups = cur.rowcount
        print(f"Deleted {deleted_groups} groups")

        # Step 6: Delete players for team
        print("Removing team players...")
        cur.execute("DELETE FROM players WHERE team_id = %s", (team_id,))
        deleted_players = cur.rowcount
        print(f"Deleted {deleted_players} players")

        # Step 7: Delete the user record itself
        print("Removing user record...")
        cur.execute("DELETE FROM users WHERE ht_id = %s", (user_id,))
        deleted_user = cur.rowcount
        print(f"Deleted {deleted_user} user record")

        # Confirm changes
        print("\nCleanup Summary:")
        print(f"- Deleted {deleted_matchplay} matchplay records")
        print(f"- Deleted {deleted_matches} match records")
        print(f"- Deleted {deleted_associations} player settings")
        print(f"- Deleted {deleted_groups} groups for user {user_id}")
        print(f"- Deleted {deleted_players} players for team {team_id}")
        print(f"- Deleted {deleted_user} user record")

        # Ask for confirmation
        response = input("\nDo you want to commit these changes? (yes/no): ").lower()
        if response == 'yes':
            conn.commit()
            print("✅ Changes committed successfully!")

            # Verify cleanup
            cur.execute("SELECT COUNT(*) FROM players WHERE team_id = %s", (team_id,))
            remaining_players = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM playergroup WHERE user_id = %s", (user_id,))
            remaining_groups = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM users WHERE ht_id = %s", (user_id,))
            remaining_users = cur.fetchone()[0]

            print(f"Verification - Remaining: {remaining_players} players, {remaining_groups} groups, {remaining_users} users")
            return False

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    except Exception as e:
        print(f"Error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cleanup_user_data.py <user_id> <team_id>")
        print("Example: python cleanup_user_data.py 182085 9838")
        sys.exit(1)

    try:
        user_id = int(sys.argv[1])
        team_id = int(sys.argv[2])
    except ValueError:
        print("Error: user_id and team_id must be integers")
        sys.exit(1)

    print("🗑️  Database Cleanup Script")
    print(f"User ID: {user_id}")
    print(f"Team ID: {team_id}")
    print()

    success = cleanup_user_data(user_id, team_id)
    sys.exit(0 if success else 1)
