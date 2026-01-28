#!/usr/bin/env python3
"""
HTStatus Database Migration Utility

Apply database migrations safely using Alembic directly.
Created during INFRA-011 troubleshooting for authentication system restoration.

Usage:
    uv run python scripts/database/apply_migrations.py

Environment:
    This script requires the UV-managed Python environment.
    Always use 'uv run' to ensure correct dependency resolution.

Features:
    - Uses Alembic directly to avoid Flask app startup issues
    - Loads database configuration from environment variables
    - Provides clear success/failure feedback

Requirements:
    - Must be run from project root directory
    - Database connection must be properly configured in .env
    - Alembic must be installed in environment

Related Commands:
    make db-upgrade     # Standard migration command (recommended)
    make db-migrate     # Generate new migrations

Author: HTStatus Development Team
Created: January 13, 2026 (INFRA-011 authentication fix)
Updated: January 28, 2026 (Use Alembic directly to avoid Flask startup issues)
"""

import os
import sys
from pathlib import Path
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv

if __name__ == "__main__":
    # Ensure we're in the project root directory
    script_dir = Path(__file__).resolve().parent.parent.parent
    os.chdir(script_dir)

    # Load environment variables
    load_dotenv()

    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("Please ensure .env file contains DATABASE_URL")
        exit(1)

    print("Applying database migrations...")
    print(f"Database: {database_url.split('@')[1] if '@' in database_url else 'configured'}")

    try:
        # Configure Alembic
        alembic_cfg = Config('migrations/alembic.ini')
        alembic_cfg.set_main_option('sqlalchemy.url', database_url)

        # Run migrations to latest revision
        command.upgrade(alembic_cfg, 'head')

        print("✅ Database migrations completed successfully!")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        exit(1)
