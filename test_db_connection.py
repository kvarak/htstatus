#!/usr/bin/env python
"""Test database connection with the Flask app configuration."""

from dotenv import load_dotenv
load_dotenv()

from app.factory import create_app
from app.factory import db
import os

print(f"Environment variables:")
print(f"  POSTGRES_USER: {os.environ.get('POSTGRES_USER')}")
print(f"  POSTGRES_PASSWORD: {os.environ.get('POSTGRES_PASSWORD')}")
print(f"  POSTGRES_HOST: {os.environ.get('POSTGRES_HOST')}")
print(f"  POSTGRES_PORT: {os.environ.get('POSTGRES_PORT')}")
print(f"  POSTGRES_DB: {os.environ.get('POSTGRES_DB')}")

app = create_app()
print(f"\nDatabase URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    try:
        result = db.session.execute(db.text("SELECT 1")).scalar()
        print(f"\nDatabase connection successful! Result: {result}")
    except Exception as e:
        print(f"\nDatabase connection failed: {e}")
