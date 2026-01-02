#!/usr/bin/env python
"""Apply database migrations programmatically."""

from dotenv import load_dotenv

load_dotenv()

from alembic import command
from alembic.config import Config as AlembicConfig

from app.factory import create_app

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
