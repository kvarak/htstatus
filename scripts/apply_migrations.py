#!/usr/bin/env python3
"""
Apply database migrations programmatically.

Usage:
    uv run python scripts/apply_migrations.py

Environment:
    This script requires the UV-managed Python environment.
    Always use 'uv run' to ensure correct dependency resolution.

Note:
    Prefer 'make db-upgrade' for standard migration operations.
"""

from alembic import command
from alembic.config import Config as AlembicConfig
from dotenv import load_dotenv

from app.factory import create_app

load_dotenv()

# Create Flask app
app = create_app()

# Create Alembic config
alembic_cfg = AlembicConfig("migrations/alembic.ini")
alembic_cfg.set_main_option("script_location", "migrations")

# Run migrations within app context
with app.app_context():
    print("Applying database migrations...")
    command.upgrade(alembic_cfg, "head")
    print("Migrations applied successfully!")
