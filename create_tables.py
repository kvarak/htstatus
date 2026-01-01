#!/usr/bin/env python
"""Create all database tables using SQLAlchemy."""

from dotenv import load_dotenv

load_dotenv()

from app.factory import create_app, db

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
