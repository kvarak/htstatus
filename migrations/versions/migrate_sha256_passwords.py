"""Migrate SHA256 password hashes to Werkzeug 3.x compatibility

Revision ID: migrate_sha256_pwd
Revises: pwd_field_werkzeug3x
Create Date: 2026-01-22 10:45:00

This migration addresses the critical backward compatibility issue where existing users
with SHA256 password hashes cannot authenticate after upgrading to Werkzeug 3.x.

Werkzeug 3.x removed support for generating SHA256 hashes and cannot verify them.
This migration:

1. Identifies users with old SHA256 password hashes (format: sha256$...)
2. Marks these passwords as requiring re-authentication
3. Preserves their OAuth tokens so they can still access the system
4. Forces password reset on next login to get modern scrypt hash

Users will need to:
- Use their existing OAuth flow (if tokens are valid)
- Or reset their password to get a new scrypt-based hash

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'migrate_sha256_pwd'
down_revision = 'pwd_field_werkzeug3x'
branch_labels = None
depends_on = None


def upgrade():
    """Migrate users with SHA256 password hashes for Werkzeug 3.x compatibility."""

    # Get connection to execute SQL
    connection = op.get_bind()

    # Find users with SHA256 password hashes (format: sha256$...)
    result = connection.execute(
        sa.text("SELECT ht_id, username, password FROM users WHERE password LIKE 'sha256$%'")
    )

    sha256_users = result.fetchall()

    if sha256_users:
        print(f"Found {len(sha256_users)} users with SHA256 password hashes requiring migration")

        # Mark SHA256 passwords as requiring reset by prefixing with 'MIGRATION_REQUIRED:'
        # This allows us to detect them and force password reset while preserving the original hash
        for user in sha256_users:
            connection.execute(
                sa.text("UPDATE users SET password = :new_password WHERE ht_id = :ht_id"),
                {
                    'new_password': f'MIGRATION_REQUIRED:{user.password}',
                    'ht_id': user.ht_id
                }
            )
            print(f"Marked user {user.username} (ID: {user.ht_id}) for password migration")

        print(f"Migration complete. {len(sha256_users)} users will need to reset passwords.")
        print("Users can still authenticate via OAuth if they have valid tokens.")

    else:
        print("No users with SHA256 password hashes found. No migration needed.")


def downgrade():
    """Restore SHA256 password hashes (WARNING: will break authentication in Werkzeug 3.x)."""

    connection = op.get_bind()

    # Find users with migration markers and restore original SHA256 hashes
    result = connection.execute(
        sa.text("SELECT ht_id, username, password FROM users WHERE password LIKE 'MIGRATION_REQUIRED:sha256$%'")
    )

    migrated_users = result.fetchall()

    if migrated_users:
        print(f"Restoring {len(migrated_users)} SHA256 password hashes")

        for user in migrated_users:
            # Remove the MIGRATION_REQUIRED: prefix
            original_password = user.password.replace('MIGRATION_REQUIRED:', '')
            connection.execute(
                sa.text("UPDATE users SET password = :password WHERE ht_id = :ht_id"),
                {
                    'password': original_password,
                    'ht_id': user.ht_id
                }
            )
            print(f"Restored SHA256 hash for user {user.username} (ID: {user.ht_id})")

        print("WARNING: These users will not be able to authenticate with Werkzeug 3.x!")
        print("This downgrade should only be used if reverting to Werkzeug 2.x")

    else:
        print("No migrated SHA256 users found to restore.")
