#!/usr/bin/env python3
"""
HTStatus Database Connection Validator

Test PostgreSQL database connectivity with detailed diagnostics.
Created during INFRA-011 troubleshooting for authentication system restoration.

Usage:
    python scripts/database/test_db_connection.py

Features:
    - Tests direct psycopg2 connection bypassing SQLAlchemy
    - Parses connection string and validates components
    - Provides detailed error diagnostics for troubleshooting
    - Shows current user and database information on success

Troubleshooting:
    - "role does not exist": Check PostgreSQL user setup
    - "password authentication failed": Verify .env credentials
    - "connection refused": Check if PostgreSQL service is running
    - "port 5432 already in use": Stop local PostgreSQL service

Common Issues:
    - macOS: Conflicting brew postgresql services
    - Docker: Services not started with 'make services'
    - Environment: Missing or incorrect .env configuration

Related Commands:
    make services       # Start Docker PostgreSQL
    make config-validate # Check environment configuration

Author: HTStatus Development Team
Created: January 13, 2026 (INFRA-011 authentication fix)
"""

import psycopg2
from config import Config

config = Config()
conn_string = config.SQLALCHEMY_DATABASE_URI
print(f"Testing connection to: {conn_string}")

try:
    # Parse the connection string manually to test with psycopg2 directly
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', conn_string)
    if match:
        user, password, host, port, database = match.groups()
        print(f"Parsed - User: {user}, Host: {host}, Port: {port}, Database: {database}")

        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        cursor = conn.cursor()
        cursor.execute("SELECT current_user, current_database();")
        result = cursor.fetchone()
        print(f"SUCCESS: Connected as user '{result[0]}' to database '{result[1]}'")
        conn.close()
    else:
        print("Could not parse connection string")

except Exception as e:
    print(f"ERROR: {e}")