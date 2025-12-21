"""Flask application factory for HT Status application."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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
    import models

    # Set up routes only if requested (allows testing without complex routes)
    if include_routes:
        setup_routes(app, db)

    return app


def setup_routes(app_instance, db_instance):
    """Set up routes with the app and db instances."""
    # Import routes and set the global variables
    from app import routes
    routes.app = app_instance
    routes.db = db_instance
    # Initialize routes module
    routes.initialize_routes()