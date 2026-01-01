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
