#!/usr/bin/env python3
"""
Database Utility Functions

Shared utilities for database scripts to eliminate code duplication.
Created as part of REFACTOR-034: Database Script Consolidation.

Author: HTStatus Development Team
"""

import os

from dotenv import load_dotenv


def parse_database_url(database_url):
    """Parse DATABASE_URL into connection components."""
    # Example: postgresql://user:password@host:port/database
    if not database_url.startswith('postgresql://'):
        raise ValueError(f"Invalid DATABASE_URL format: {database_url}")

    # Remove postgresql:// prefix
    url_part = database_url[13:]

    # Split into auth@host/database
    if '@' not in url_part:
        raise ValueError("Invalid DATABASE_URL format: missing auth")

    auth_part, host_db_part = url_part.split('@', 1)

    # Parse auth (user:password)
    if ':' in auth_part:
        user, password = auth_part.split(':', 1)
    else:
        user, password = auth_part, None

    # Parse host and database
    if '/' not in host_db_part:
        raise ValueError("Invalid DATABASE_URL format: missing database")

    host_port, database = host_db_part.split('/', 1)

    # Parse host and port
    if ':' in host_port:
        host, port = host_port.split(':', 1)
    else:
        host, port = host_port, '5432'

    return {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }


def load_database_config():
    """Load DATABASE_URL from environment and parse it."""
    load_dotenv()
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    return parse_database_url(database_url)
