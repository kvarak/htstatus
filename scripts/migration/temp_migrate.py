#!/usr/bin/env python3
"""
HTStatus Quick Migration Utility

Simple database migration script for development and debugging.
Created during INFRA-011 troubleshooting for authentication system restoration.

Usage:
    python scripts/migration/temp_migrate.py

Features:
    - Quick and simple migration execution
    - Minimal setup for emergency scenarios
    - Direct Flask-Migrate integration

Warning:
    This is a simplified version of apply_migrations.py without error handling.
    Use apply_migrations.py for production or safer migration operations.

Related Scripts:
    scripts/database/apply_migrations.py  # Full-featured migration utility

Related Commands:
    make db-upgrade     # Standard migration command (recommended)
    make db-migrate     # Generate new migrations

Author: HTStatus Development Team
Created: January 13, 2026 (INFRA-011 authentication fix)
"""

from app.factory import create_app

app = create_app()
app.app_context().push()
from flask_migrate import upgrade

upgrade()
print("Database migrations completed successfully!")
