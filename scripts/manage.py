"""
Database migration management using Flask-Migrate.
Usage: flask db <command>
"""
from dotenv import load_dotenv

load_dotenv()  # Load environment variables before anything else

from flask_migrate import Migrate

from app.factory import create_app, db

# Create app instance
app = create_app()

# Initialize Flask-Migrate
migrate = Migrate(app, db)

if __name__ == '__main__':
    # For backwards compatibility, but prefer using: flask db upgrade
    print("Use 'flask db upgrade' to apply migrations")
    print("Use 'flask db migrate' to create new migrations")
