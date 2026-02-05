#!/usr/bin/env python
"""Quick script to query match data from database."""
import sys

from sqlalchemy import text

from app.factory import create_app

if len(sys.argv) < 2:
    print("Usage: python query_match_data.py <match_id>")
    sys.exit(1)

match_id = int(sys.argv[1])

app = create_app()
with app.app_context():
    from models import db
    result = db.session.execute(text("SELECT * FROM match WHERE ht_id = :match_id"), {"match_id": match_id})
    row = result.fetchone()

    if not row:
        print(f"Match {match_id} not found")
        sys.exit(1)

    # Print all columns
    print(f"\n{'='*80}")
    print(f"SELECT * FROM match WHERE ht_id = {match_id}")
    print(f"{'='*80}")
    for key, value in row._mapping.items():
        print(f"{key:30s} = {value}")
