#!/usr/bin/env python3
"""
Create all database tables using SQLAlchemy.

Usage:
    uv run python scripts/create_tables.py

Environment:
    This script requires the UV-managed Python environment.
    Always use 'uv run' to ensure correct dependency resolution.
"""

from dotenv import load_dotenv

from app.factory import create_app, db

load_dotenv()

# Create Flask app
app = create_app()

# Create all tables within app context
with app.app_context():
    print("Creating all database tables...")
    db.create_all()
    print("All tables created successfully!")

    # Verify tables were created
    from sqlalchemy import inspect

    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\nCreated {len(tables)} tables:")
    for table in sorted(tables):
        print(f"  - {table}")
