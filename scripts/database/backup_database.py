#!/usr/bin/env python3
"""
Complete Database Backup Utility

Creates a full PostgreSQL dump backup for database protection.
Part of INFRA-033: Database Protection Enhancement.

Usage:
    uv run python scripts/database/backup_database.py [--output-dir PATH]

Environment:
    Requires DATABASE_URL in environment (loaded from .env)
    Uses PostgreSQL pg_dump for complete database backup

Author: HTStatus Development Team
Created: February 6, 2026 (INFRA-033 Database Protection)
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import click

# Add the current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from db_utils import load_database_config


def create_database_backup(output_dir: str = None) -> str:
    """Create a complete database backup using pg_dump."""
    print("=== CREATING DATABASE BACKUP ===")

    try:
        db_config = load_database_config()
        print(f"Database: {db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
    except ValueError as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)

    # Set output directory
    if not output_dir:
        output_dir = Path(__file__).parent / "backups"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(exist_ok=True)

    # Create backup filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = output_dir / f"htstatus_full_backup_{timestamp}.sql"

    # Prepare pg_dump command
    cmd = [
        'pg_dump',
        '--host', db_config['host'],
        '--port', db_config['port'],
        '--username', db_config['user'],
        '--no-password',  # Use PGPASSWORD environment variable
        '--verbose',
        '--clean',        # Add DROP statements
        '--create',       # Add CREATE DATABASE statement
        '--if-exists',    # Add IF EXISTS to DROP statements
        '--format=plain', # Plain SQL format
        '--file', str(backup_file),
        db_config['database']
    ]

    # Set environment for pg_dump
    env = os.environ.copy()
    if db_config['password']:
        env['PGPASSWORD'] = db_config['password']

    print(f"Creating backup: {backup_file}")
    print(f"Command: {' '.join(cmd[:8])} ... [password hidden]")

    try:
        # Run pg_dump
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )

        # Check if backup file was created and has content
        if backup_file.exists() and backup_file.stat().st_size > 0:
            backup_size = backup_file.stat().st_size
            print(f"✅ Backup created successfully: {backup_file}")
            print(f"   Size: {backup_size:,} bytes ({backup_size / 1024 / 1024:.1f} MB)")

            # Show backup info
            print(f"   Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Database: {db_config['database']}")
            print(f"   Host: {db_config['host']}")

            return str(backup_file)
        else:
            print("❌ ERROR: Backup file was not created or is empty")
            if result.stderr:
                print(f"pg_dump error: {result.stderr}")
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: pg_dump failed with exit code {e.returncode}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if e.stdout:
            print(f"Standard output: {e.stdout}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: Unexpected error during backup: {e}")
        sys.exit(1)


@click.command()
@click.option('--output-dir', help='Output directory for backup file')
def main(output_dir):
    """Create a complete database backup."""
    backup_file = create_database_backup(output_dir)
    print(f"\n🎉 Database backup completed: {backup_file}")


if __name__ == '__main__':
    main()
