#!/usr/bin/env python3
"""
Database Restore Utility

Restores a complete PostgreSQL database from backup file.
Part of INFRA-033: Database Protection Enhancement.

Usage:
    uv run python scripts/database/restore_database.py BACKUP_FILE [--target-db TARGET]

Environment:
    Requires DATABASE_URL in environment (loaded from .env)
    Uses PostgreSQL psql for database restoration

Author: HTStatus Development Team
Created: February 6, 2026 (INFRA-033 Database Protection)
"""

import os
import subprocess
import sys
from pathlib import Path

import click
from dotenv import load_dotenv


def parse_database_url(database_url):
    """Parse DATABASE_URL into connection components."""
    # Example: postgresql://user:password@host:port/database
    if not database_url.startswith('postgresql://'):
        raise ValueError(f"Invalid DATABASE_URL format: {database_url}")

    # Remove postgresql:// prefix
    url_part = database_url[13:]

    # Split into auth@host/database
    if '@' not in url_part:
        raise ValueError("Invalid DATABASE_URL format: missing auth")

    auth_part, host_db_part = url_part.split('@', 1)

    # Parse auth (user:password)
    if ':' in auth_part:
        user, password = auth_part.split(':', 1)
    else:
        user, password = auth_part, None

    # Parse host and database
    if '/' not in host_db_part:
        raise ValueError("Invalid DATABASE_URL format: missing database")

    host_port, database = host_db_part.split('/', 1)

    # Parse host and port
    if ':' in host_port:
        host, port = host_port.split(':', 1)
    else:
        host, port = host_port, '5432'

    return {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }


def confirm_restore(backup_file: str, target_db: str) -> bool:
    """Confirm restoration with user."""
    print("⚠️  WARNING: Database restoration will OVERWRITE existing data!")
    print(f"   Backup file: {backup_file}")
    print(f"   Target database: {target_db}")
    print()

    response = input("Are you sure you want to continue? Type 'yes' to confirm: ").strip().lower()
    return response == 'yes'


def restore_database_backup(backup_file: str, target_db: str = None) -> bool:
    """Restore database from backup file using psql."""
    print("=== RESTORING DATABASE BACKUP ===")

    # Validate backup file
    backup_path = Path(backup_file)
    if not backup_path.exists():
        print(f"❌ ERROR: Backup file does not exist: {backup_file}")
        return False

    if not backup_path.is_file():
        print(f"❌ ERROR: Backup path is not a file: {backup_file}")
        return False

    backup_size = backup_path.stat().st_size
    if backup_size == 0:
        print(f"❌ ERROR: Backup file is empty: {backup_file}")
        return False

    print(f"Backup file: {backup_file}")
    print(f"Backup size: {backup_size:,} bytes ({backup_size / 1024 / 1024:.1f} MB)")

    # Load environment variables
    load_dotenv()
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        return False

    try:
        db_config = parse_database_url(database_url)

        # Use target database if specified, otherwise use configured database
        if target_db:
            db_config['database'] = target_db

        print(f"Target: {db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

    except ValueError as e:
        print(f"❌ ERROR: {e}")
        return False

    # Confirm restoration
    if not confirm_restore(str(backup_path), db_config['database']):
        print("❌ Restoration cancelled by user")
        return False

    # Prepare psql command
    cmd = [
        'psql',
        '--host', db_config['host'],
        '--port', db_config['port'],
        '--username', db_config['user'],
        '--no-password',  # Use PGPASSWORD environment variable
        '--dbname', 'postgres',  # Connect to postgres database to create target DB
        '--file', str(backup_path),
        '--quiet',
        '--variable', 'ON_ERROR_STOP=1'  # Stop on first error
    ]

    # Set environment for psql
    env = os.environ.copy()
    if db_config['password']:
        env['PGPASSWORD'] = db_config['password']

    print(f"Restoring to database: {db_config['database']}")
    print(f"Command: {' '.join(cmd[:6])} ... [details hidden]")

    try:
        # Run psql restore
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )

        print("✅ Database restored successfully!")
        print(f"   Target database: {db_config['database']}")
        print(f"   Restored from: {backup_file}")

        if result.stdout:
            print("Restore output:")
            print(result.stdout)

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: psql restore failed with exit code {e.returncode}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if e.stdout:
            print(f"Standard output: {e.stdout}")
        return False

    except Exception as e:
        print(f"❌ ERROR: Unexpected error during restore: {e}")
        return False


@click.command()
@click.argument('backup_file', type=click.Path(exists=True))
@click.option('--target-db', help='Target database name (defaults to configured database)')
def main(backup_file, target_db):
    """Restore database from backup file.

    BACKUP_FILE: Path to the backup file to restore from
    """
    success = restore_database_backup(backup_file, target_db)
    if success:
        print("\n🎉 Database restoration completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Database restoration failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
