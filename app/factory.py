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

    # Set up routes only if requested (allows testing without complex routes)
    if include_routes:
        setup_routes(app, db)

    return app


def setup_routes(app_instance, db_instance):
    """Set up routes with the app and db instances using Blueprint pattern."""
    # Initialize legacy routes module for helper functions and constants
    import app.routes as routes_module
    routes_module.app = app_instance
    routes_module.db = db_instance
    routes_module.initialize_routes()

    # Import and initialize blueprint modules
    from app.routes_bp import initialize_routes as init_routes_bp
    init_routes_bp(app_instance, db_instance)

    # Import blueprint functions
    from app.blueprints.auth import setup_auth_blueprint, login, logout
    from app.blueprints.main import setup_main_blueprint, index, settings, admin
    from app.blueprints.player import setup_player_blueprint, player
    from app.blueprints.team import setup_team_blueprint, team, update
    from app.blueprints.matches import setup_matches_blueprint, matches, stats
    from app.blueprints.training import setup_training_blueprint, training

    # Setup authentication blueprint
    setup_auth_blueprint(
        app_instance,
        db_instance,
        app_instance.config.get('CONSUMER_KEY', 'dev_key'),
        app_instance.config.get('CONSUMER_SECRETS', 'dev_secret')
    )

    # Setup main blueprint
    setup_main_blueprint(
        db_instance,
        routes_module.defaultcolumns,
        routes_module.allcolumns,
        routes_module.default_group_order
    )

    # Setup player blueprint
    setup_player_blueprint(
        db_instance,
        routes_module.defaultcolumns,
        routes_module.calccolumns,
        routes_module.tracecolumns,
        routes_module.default_group_order
    )

    # Setup team blueprint
    setup_team_blueprint(
        app_instance,
        db_instance,
        app_instance.config.get('CONSUMER_KEY', 'dev_key'),
        app_instance.config.get('CONSUMER_SECRETS', 'dev_secret'),
        routes_module.version,
        routes_module.fullversion
    )

    # Setup matches blueprint
    setup_matches_blueprint(
        db_instance,
        routes_module.HTmatchtype,
        routes_module.HTmatchrole,
        routes_module.HTmatchbehaviour
    )

    # Setup training blueprint
    setup_training_blueprint(
        db_instance,
        routes_module.tracecolumns
    )

    # Manually register all route functions (bypassing failed decorators)
    # This is necessary because @app.route decorators failed during import when app=None
    app_instance.add_url_rule('/', 'index', index, methods=['GET'])
    app_instance.add_url_rule('/index', 'index', index, methods=['GET'])
    app_instance.add_url_rule('/settings', 'settings', settings, methods=['GET', 'POST'])
    app_instance.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
    app_instance.add_url_rule('/logout', 'logout', logout, methods=['GET'])
    app_instance.add_url_rule('/update', 'update', update, methods=['GET'])
    app_instance.add_url_rule('/debug', 'admin', admin, methods=['GET', 'POST'])
    app_instance.add_url_rule('/team', 'team', team, methods=['GET'])
    app_instance.add_url_rule('/player', 'player', player, methods=['GET', 'POST'])
    app_instance.add_url_rule('/matches', 'matches', matches, methods=['GET', 'POST'])
    app_instance.add_url_rule('/stats', 'stats', stats, methods=['GET'])
    app_instance.add_url_rule('/training', 'training', training, methods=['GET'])
