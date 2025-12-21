"""HT Status Flask Application Package."""

import os
from app.factory import create_app, db

# Create application instance for backward compatibility
# Only include routes for production/development (not testing)
include_routes = os.environ.get('FLASK_ENV') != 'testing'
app = create_app(include_routes=include_routes)

# Make db available at module level for existing code
__all__ = ['app', 'db']
