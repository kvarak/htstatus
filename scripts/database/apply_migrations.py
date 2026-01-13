#!/usr/bin/env python3
"""
HTStatus Database Migration Utility

Apply database migrations safely with proper Flask application context.
Created during INFRA-011 troubleshooting for authentication system restoration.

Usage:
    python scripts/database/apply_migrations.py

Features:
    - Creates Flask app with routes disabled to avoid startup issues
    - Uses proper application context for migration safety
    - Provides clear success/failure feedback

Requirements:
    - Must be run from project root directory
    - Database connection must be properly configured in .env
    - Flask-Migrate must be installed in environment

Related Commands:
    make db-upgrade     # Standard migration command (recommended)
    make db-migrate     # Generate new migrations

Author: HTStatus Development Team
Created: January 13, 2026 (INFRA-011 authentication fix)
"""

import os
from app.factory import create_app, db
from flask_migrate import upgrade

if __name__ == "__main__":
    # Create app with routes disabled to avoid startup issues
    app = create_app(include_routes=False)
    with app.app_context():
        print("Applying database migrations...")
        upgrade()
        print("✅ Database migrations completed successfully!")