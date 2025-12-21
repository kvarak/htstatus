#!/usr/bin/python3

import platform
import os

print("Python version " + platform.python_version())

# Use the factory pattern instead of direct Flask instantiation
from app.factory import create_app

# Set development environment
os.environ.setdefault('FLASK_ENV', 'development')

# Create app using factory pattern
app = create_app()

if __name__ == '__main__':
    # Use environment variables for host and port configuration
    host = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_RUN_PORT', '5000'))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'

    # Temporarily disable reloader for debugging
    app.run(host=host, port=port, debug=debug, use_reloader=False)


