#!/usr/bin/env python3
"""
HTStatus Production Error Log Checker

Check production errors logged in the database for debugging and monitoring.
Part of INFRA-085 simplified crash detection system.

Usage:
    uv run python scripts/database/check_errors.py --help
    uv run python scripts/database/check_errors.py --count
    uv run python scripts/database/check_errors.py --recent 10
    uv run python scripts/database/check_errors.py --last-24h
    uv run python scripts/database/check_errors.py --details <error_id>

Environment:
    This script requires the UV-managed Python environment.
    Always use 'uv run' to ensure correct dependency resolution.

Features:
    - Check production error counts and summaries
    - View recent errors with context information
    - Show detailed stack traces for specific errors
    - Filter by time period (last 24 hours)

Related Scripts:
    - apply_migrations.py: Database migration management
    - test_db_connection.py: Database connectivity testing

Author: HTStatus Development Team
Created: February 1, 2026 (INFRA-085 crash detection)
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path to import config
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def read_config():
    """Read database configuration from config.py"""
    try:
        # Import the config module directly
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", project_root / "config.py")
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)

        # Get the config class and instantiate it
        config_obj = config_module.Config()
        return config_obj.SQLALCHEMY_DATABASE_URI

    except Exception as e:
        print(f"Error reading config: {e}")
        return None

def get_database_connection():
    """Get database connection using same pattern as other database scripts"""
    import psycopg2

    database_url = read_config()
    if not database_url:
        raise Exception("Could not read database configuration")

    # Parse PostgreSQL URL into connection parameters
    if not database_url.startswith('postgresql://'):
        raise ValueError("Invalid DATABASE_URL format")

    url = database_url.replace('postgresql://', '')

    if '@' in url:
        credentials, host_part = url.split('@', 1)
        if ':' in credentials:
            user, password = credentials.split(':', 1)
        else:
            user, password = credentials, ''
    else:
        user, password, host_part = '', '', url

    if '/' in host_part:
        host_info, dbname = host_part.split('/', 1)
    else:
        host_info, dbname = host_part, 'postgres'

    if ':' in host_info:
        host, port = host_info.split(':', 1)
        port = int(port)
    else:
        host, port = host_info, 5432

    # Connect to database
    connection = psycopg2.connect(
        host=host,
        port=port,
        database=dbname,
        user=user,
        password=password
    )

    return connection

def format_error_summary(error_row):
    """Format error for summary display."""
    error_id, timestamp, error_type, message, user_id, request_path = error_row[:6]
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    user_info = f"User {user_id}" if user_id else "Anonymous"
    path_info = request_path or "Unknown path"
    message_preview = (message[:50] + "...") if message and len(message) > 50 else (message or "No message")

    return f"[{timestamp_str}] {error_type} | {user_info} | {path_info} | {message_preview}"

def format_error_details(error_row):
    """Format error for detailed display."""
    error_id, timestamp, error_type, message, stack_trace, user_id, request_path, request_method, user_agent, environment = error_row

    lines = [
        f"Error ID: {error_id}",
        f"Timestamp: {timestamp}",
        f"Type: {error_type}",
        f"User ID: {user_id or 'Anonymous'}",
        f"Request: {request_method or 'UNKNOWN'} {request_path or 'Unknown path'}",
        f"User Agent: {user_agent or 'Unknown'}",
        f"Environment: {environment}",
        "",
        "Message:",
        message or "No message",
        "",
    ]

    if stack_trace:
        lines.extend([
            "Stack Trace:",
            stack_trace,
        ])

    return "\n".join(lines)

def show_error_count():
    """Show error counts by type and recent activity."""
    try:
        conn = get_database_connection()
        cur = conn.cursor()

        print("📊 Error Count Summary")
        print("=" * 50)

        # Total errors
        cur.execute("SELECT COUNT(*) FROM error_log")
        total_errors = cur.fetchone()[0]
        print(f"Total errors logged: {total_errors}")

        if total_errors == 0:
            print("🎉 No errors found! System is healthy.")
            cur.close()
            conn.close()
            return

        # Errors by type
        cur.execute("""
            SELECT error_type, COUNT(*) as count
            FROM error_log
            GROUP BY error_type
            ORDER BY count DESC
        """)
        error_types = cur.fetchall()

        print("\nErrors by type:")
        for error_type, count in error_types:
            print(f"  {error_type}: {count}")

        # Recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        cur.execute("""
            SELECT COUNT(*) FROM error_log
            WHERE timestamp >= %s
        """, (yesterday,))
        recent_errors = cur.fetchone()[0]
        print(f"\nErrors in last 24 hours: {recent_errors}")

        # Latest error
        cur.execute("""
            SELECT timestamp, error_type FROM error_log
            ORDER BY timestamp DESC LIMIT 1
        """)
        latest_error = cur.fetchone()
        if latest_error:
            print(f"Latest error: {latest_error[0]} ({latest_error[1]})")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")

def show_recent_errors(limit=10):
    """Show recent errors."""
    try:
        conn = get_database_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, timestamp, error_type, message, user_id, request_path
            FROM error_log
            ORDER BY timestamp DESC
            LIMIT %s
        """, (limit,))

        errors = cur.fetchall()

        if not errors:
            print("🎉 No errors found! System is healthy.")
        else:
            print(f"📋 Last {len(errors)} Errors")
            print("=" * 80)

            for error in errors:
                print(format_error_summary(error))

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")

def show_last_24h():
    """Show errors from the last 24 hours."""
    try:
        conn = get_database_connection()
        cur = conn.cursor()

        yesterday = datetime.utcnow() - timedelta(days=1)
        cur.execute("""
            SELECT id, timestamp, error_type, message, user_id, request_path
            FROM error_log
            WHERE timestamp >= %s
            ORDER BY timestamp DESC
        """, (yesterday,))

        errors = cur.fetchall()

        if not errors:
            print("🎉 No errors in the last 24 hours! System is healthy.")
        else:
            print(f"⚠️  {len(errors)} Errors in Last 24 Hours")
            print("=" * 80)

            for error in errors:
                print(format_error_summary(error))

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")

def show_error_details(error_id):
    """Show detailed information for a specific error."""
    try:
        conn = get_database_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, timestamp, error_type, message, stack_trace,
                   user_id, request_path, request_method, user_agent, environment
            FROM error_log
            WHERE id = %s
        """, (error_id,))

        error = cur.fetchone()

        if not error:
            print(f"❌ Error ID {error_id} not found.")
        else:
            print("🔍 Error Details")
            print("=" * 80)
            print(format_error_details(error))

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Check production errors logged in the database",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--count",
        action="store_true",
        help="Show error count summary"
    )

    parser.add_argument(
        "--recent",
        type=int,
        metavar="N",
        help="Show N most recent errors (default: 10)"
    )

    parser.add_argument(
        "--last-24h",
        action="store_true",
        help="Show errors from last 24 hours"
    )

    parser.add_argument(
        "--details",
        type=int,
        metavar="ERROR_ID",
        help="Show detailed information for specific error ID"
    )

    args = parser.parse_args()

    # If no arguments provided, show recent errors
    if not any([args.count, args.recent is not None, args.last_24h, args.details is not None]):
        args.recent = 10

    try:
        if args.count:
            show_error_count()
        elif args.recent is not None:
            show_recent_errors(args.recent)
        elif args.last_24h:
            show_last_24h()
        elif args.details is not None:
            show_error_details(args.details)

    except Exception as e:
        print(f"❌ Error checking database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
