"""Flask application factory for HT Status application."""

import importlib.util
import pkgutil

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Python 3.14 removed pkgutil.get_loader; add a minimal shim for Flask/werkzeug
if not hasattr(pkgutil, "get_loader"):

    def _get_loader(name):
        spec = importlib.util.find_spec(name)
        return spec.loader if spec else None

    pkgutil.get_loader = _get_loader  # type: ignore[attr-defined]

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_object=None, include_routes=True):
    """Create and configure the Flask application.

    Args:
        config_object: Configuration object or class name to use.
                      If None, uses default Config.
        include_routes: Whether to include routes (False for testing).

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)

    # Load configuration
    if config_object is None:
        from config import Config

        config_object = Config

    app.config.from_object(config_object)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models after db is initialized to avoid circular imports

    # Add custom Jinja filters
    @app.template_filter("format_age")
    def format_age(age_string):
        """Format age from '44 years and 55 days' to '44 y 55 d'"""
        if not age_string:
            return "N/A"
        import re

        # Extract years and days from the age string
        match = re.search(r"(\d+) years?.*?(\d+) days?", str(age_string))
        if match:
            years, days = match.groups()
            return f"{years} y {days} d"
        return str(age_string)

    # Set up routes only if requested (allows testing without complex routes)
    if include_routes:
        setup_routes(app, db)

    # Register error handlers for production monitoring
    from app.error_handlers import register_error_handlers
    register_error_handlers(app)

    # Display configuration status after everything is set up
    with app.app_context():
        _display_startup_status()

    return app


def setup_routes(app_instance, db_instance):
    """Set up routes with the app and db instances using Blueprint pattern."""
    # Initialize utils module with app and db instances
    from app.utils import initialize_utils

    initialize_utils(
        app_instance, db_instance, app_instance.config.get("DEBUG_LEVEL", 0)
    )

    # Import and initialize blueprint modules
    from app.routes_bp import initialize_routes as init_routes_bp

    init_routes_bp(app_instance, db_instance)

    # Import blueprint functions and blueprints
    from app.blueprints.auth import auth_bp, setup_auth_blueprint
    from app.blueprints.feedback import feedback_bp, setup_feedback_blueprint
    from app.blueprints.main import (
        main_bp,
        setup_main_blueprint,
    )
    from app.blueprints.matches import (
        matches_bp,
        setup_matches_blueprint,
    )
    from app.blueprints.player import player_bp, setup_player_blueprint
    from app.blueprints.stats import (
        setup_stats_blueprint,
        stats_bp,
    )
    from app.blueprints.team import setup_team_blueprint, team_bp
    from app.blueprints.training import setup_training_blueprint, training_bp

    # Import constants
    from app.constants import (
        ALL_COLUMNS,
        CALC_COLUMNS,
        DEFAULT_COLUMNS,
        DEFAULT_GROUP_ORDER,
        HT_MATCH_BEHAVIOUR,
        HT_MATCH_ROLE,
        HT_MATCH_TYPE,
        TRACE_COLUMNS,
    )

    # Get version info using shared utility
    from app.utils import get_version_info
    version_info = get_version_info()
    version = version_info["version"]
    fullversion = version_info["fullversion"]

    # Setup blueprint dependencies
    setup_auth_blueprint(
        app_instance,
        db_instance,
        app_instance.config.get("CONSUMER_KEY", "dev_key"),
        app_instance.config.get("CONSUMER_SECRETS", "dev_secret"),
    )

    setup_feedback_blueprint(app_instance, db_instance)

    setup_main_blueprint(db_instance, DEFAULT_COLUMNS, ALL_COLUMNS, DEFAULT_GROUP_ORDER)

    setup_player_blueprint(
        db_instance, DEFAULT_COLUMNS, CALC_COLUMNS, TRACE_COLUMNS, DEFAULT_GROUP_ORDER
    )

    setup_team_blueprint(
        app_instance,
        db_instance,
        app_instance.config.get("CONSUMER_KEY", "dev_key"),
        app_instance.config.get("CONSUMER_SECRETS", "dev_secret"),
        version,
        fullversion,
    )

    setup_matches_blueprint(
        db_instance, HT_MATCH_TYPE, HT_MATCH_ROLE, HT_MATCH_BEHAVIOUR
    )

    setup_stats_blueprint(db_instance)

    setup_training_blueprint(db_instance, TRACE_COLUMNS)

    # Register blueprints with Flask
    app_instance.register_blueprint(main_bp)
    app_instance.register_blueprint(auth_bp)
    app_instance.register_blueprint(feedback_bp)
    app_instance.register_blueprint(player_bp)
    app_instance.register_blueprint(team_bp)
    app_instance.register_blueprint(matches_bp)
    app_instance.register_blueprint(stats_bp)
    app_instance.register_blueprint(training_bp)


def _display_startup_status():
    """Display application configuration status at startup.

    Shows the current CHPP client configuration, database migration status,
    and other relevant configuration details for operational awareness.
    """
    # Configuration constants for consistent formatting
    SEPARATOR_WIDTH = 60
    STATUS_PREFIX = "  "

    separator = "=" * SEPARATOR_WIDTH

    # Get CHPP client status
    chpp_status = "✅ Using Custom CHPP Client (app.chpp)"

    # Get database migration status
    db_status = _get_database_migration_status()

    print(f"\n{separator}")
    print("Configuration Status:")
    print(f"{STATUS_PREFIX}{chpp_status}")
    print(f"{STATUS_PREFIX}{db_status}")
    print(f"{separator}\n")


def _get_database_migration_status():
    """Get current database migration status for startup display.

    Returns:
        str: Formatted database status message
    """
    try:
        from flask import current_app

        # Ensure we're in app context
        if not current_app:
            return "🔄 Database: Status check requires app context"

        from sqlalchemy import text

        from app import db

        # Check if database is accessible
        with db.engine.connect() as connection:
            # Check if alembic_version table exists
            result = connection.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'alembic_version'
            """))

            if result.fetchone() is None:
                # No alembic_version table = fresh database with tables created via db.create_all()
                return "✅ Database: Schema ready (created via db.create_all())"

            # Get current migration version
            result = connection.execute(text("SELECT version_num FROM alembic_version"))
            current_version = result.fetchone()

            if current_version is None:
                return "🔄 Database: No migrations applied"

            version = current_version[0]
            version_short = version[:8] if version else "unknown"

            # Try to get migration file name for more info
            try:
                import os
                migrations_dir = "migrations/versions"
                if os.path.exists(migrations_dir):
                    for filename in os.listdir(migrations_dir):
                        if filename.startswith(version_short):
                            # Extract meaningful name from filename
                            name_part = filename.replace(version_short + '_', '').replace('.py', '')
                            if name_part and name_part != '_':
                                return f"✅ Database: {version_short} ({name_part.replace('_', ' ')})"
                            break
            except Exception:
                pass

            return f"✅ Database: Migration {version_short}"

    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg:
            return "🔄 Database: Tables not created"
        elif "connection" in error_msg.lower():
            return "❌ Database: Connection failed"
        elif "Working outside of application" in error_msg:
            return "🔄 Database: Checking after app startup..."
