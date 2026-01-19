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
    # Import Blueprint routes and initialize
    from app.routes_bp import initialize_routes, main_bp

    # Initialize the routes module with app and db
    initialize_routes(app_instance, db_instance)

    # Register the Blueprint
    app_instance.register_blueprint(main_bp)

    # Import legacy routes module WITHOUT executing @app.route decorators
    # We'll manually register the route functions instead

    # Temporarily replace app.routes.app to prevent decorator failures during import
    import app.routes as routes_module

    # Set app and db instances
    routes_module.app = app_instance
    routes_module.db = db_instance

    # Call initialize_routes() to set up remaining module globals
    routes_module.initialize_routes()

    # Manually register all route functions (bypassing failed decorators)
    # This is necessary because @app.route decorators failed during import when app=None
    app_instance.add_url_rule('/', 'index', routes_module.index, methods=['GET'])
    app_instance.add_url_rule('/index', 'index', routes_module.index, methods=['GET'])
    app_instance.add_url_rule('/settings', 'settings', routes_module.settings, methods=['GET', 'POST'])
    app_instance.add_url_rule('/login', 'login', routes_module.login, methods=['GET', 'POST'])
    app_instance.add_url_rule('/logout', 'logout', routes_module.logout, methods=['GET'])
    app_instance.add_url_rule('/update', 'update', routes_module.update, methods=['GET'])
    app_instance.add_url_rule('/debug', 'admin', routes_module.admin, methods=['GET', 'POST'])
    app_instance.add_url_rule('/team', 'team', routes_module.team, methods=['GET'])
    app_instance.add_url_rule('/player', 'player', routes_module.player, methods=['GET', 'POST'])
    app_instance.add_url_rule('/matches', 'matches', routes_module.matches, methods=['GET', 'POST'])
    app_instance.add_url_rule('/stats', 'stats', routes_module.stats, methods=['GET'])
    app_instance.add_url_rule('/training', 'training', routes_module.training, methods=['GET'])
