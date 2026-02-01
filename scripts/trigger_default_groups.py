#!/usr/bin/env python3
"""
Trigger default groups creation for an existing user
"""
import sys
from pathlib import Path

from app.factory import create_app
from app.utils import create_default_groups

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def trigger_groups_for_user(user_id):
    """Trigger default group creation for specific user"""
    app = create_app()

    with app.app_context():
        print(f"🎯 Triggering default groups creation for user {user_id}")

        try:
            create_default_groups(user_id)
            print("✅ Default groups created successfully!")
        except Exception as e:
            print(f"❌ Error creating default groups: {e}")
            return False

    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: uv run python trigger_default_groups.py <user_id>")
        print("Example: uv run python trigger_default_groups.py 182085")
        sys.exit(1)

    try:
        user_id = int(sys.argv[1])
    except ValueError:
        print("Error: user_id must be an integer")
        sys.exit(1)

    success = trigger_groups_for_user(user_id)
    sys.exit(0 if success else 1)
