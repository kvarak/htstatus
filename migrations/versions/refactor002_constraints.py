"""Add nullable=False constraints for REFACTOR-002 type system consolidation

Revision ID: refactor002_constraints
Revises: migrate_sha256_pwd
Create Date: 2026-01-28 07:15:00

This migration adds NOT NULL constraints to database columns that correspond to
SQLAlchemy model fields updated with nullable=False during REFACTOR-002 type
system consolidation work.

PRODUCTION SAFETY:
- This migration is designed to work safely with existing production data
- Fields being constrained should not have NULL values in production
- If NULL values exist, the migration will fail safely before making changes
- Reversible via downgrade() method

Fields being updated to NOT NULL:
- User: ht_user, username (core user identity fields)
- Match: home_team_name, away_team_name (required match data)
- MatchPlay: first_name, last_name (required player data)
- PlayerSetting: user_id, player_id (required foreign keys)
- PlayerGroup: user_id, name (required group data)
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'refactor002_constraints'
down_revision = 'migrate_sha256_pwd'
branch_labels = None
depends_on = None


def upgrade():
    """Add NOT NULL constraints to fields that should not be nullable."""

    # Check for NULL values before adding constraints
    connection = op.get_bind()

    # Define tables and columns to check/update
    constraints_to_add = [
        ('users', 'ht_user', 'User ht_user field'),
        ('users', 'username', 'User username field'),
        ('match', 'home_team_name', 'Match home_team_name field'),
        ('match', 'away_team_name', 'Match away_team_name field'),
        ('matchplay', 'first_name', 'MatchPlay first_name field'),
        ('matchplay', 'last_name', 'MatchPlay last_name field'),
        ('playersetting', 'user_id', 'PlayerSetting user_id field'),
        ('playersetting', 'player_id', 'PlayerSetting player_id field'),
        ('playergroup', 'user_id', 'PlayerGroup user_id field'),
        ('playergroup', 'name', 'PlayerGroup name field'),
    ]

    # Check for NULL values first
    null_found = False
    for table_name, column_name, description in constraints_to_add:
        try:
            result = connection.execute(sa.text(f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NULL"))
            null_count = result.scalar()
            if null_count > 0:
                print(f"WARNING: Found {null_count} NULL values in {table_name}.{column_name}")
                null_found = True
        except Exception as e:
            print(f"Could not check {table_name}.{column_name}: {e}")

    if null_found:
        raise Exception("Migration aborted: NULL values found in fields that need NOT NULL constraints. Please clean data first.")

    # Apply NOT NULL constraints
    try:
        # Users table
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.alter_column('ht_user',
                existing_type=sa.String(length=50),
                nullable=False)
            batch_op.alter_column('username',
                existing_type=sa.String(length=100),
                nullable=False)

        # Match table
        with op.batch_alter_table('match', schema=None) as batch_op:
            batch_op.alter_column('home_team_name',
                existing_type=sa.String(length=100),
                nullable=False)
            batch_op.alter_column('away_team_name',
                existing_type=sa.String(length=100),
                nullable=False)

        # MatchPlay table
        with op.batch_alter_table('matchplay', schema=None) as batch_op:
            batch_op.alter_column('first_name',
                existing_type=sa.String(length=50),
                nullable=False)
            batch_op.alter_column('last_name',
                existing_type=sa.String(length=50),
                nullable=False)

        # PlayerSetting table
        with op.batch_alter_table('playersetting', schema=None) as batch_op:
            batch_op.alter_column('user_id',
                existing_type=sa.Integer(),
                nullable=False)
            batch_op.alter_column('player_id',
                existing_type=sa.Integer(),
                nullable=False)

        # PlayerGroup table
        with op.batch_alter_table('playergroup', schema=None) as batch_op:
            batch_op.alter_column('user_id',
                existing_type=sa.Integer(),
                nullable=False)
            batch_op.alter_column('name',
                existing_type=sa.String(length=100),
                nullable=False)

    except Exception as e:
        raise Exception(f"Migration failed during constraint addition: {e}")


def downgrade():
    """Remove NOT NULL constraints (reverse the migration)."""

    try:
        # Reverse Users table changes
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.alter_column('ht_user',
                existing_type=sa.String(length=50),
                nullable=True)
            batch_op.alter_column('username',
                existing_type=sa.String(length=100),
                nullable=True)

        # Reverse Match table changes
        with op.batch_alter_table('match', schema=None) as batch_op:
            batch_op.alter_column('home_team_name',
                existing_type=sa.String(length=100),
                nullable=True)
            batch_op.alter_column('away_team_name',
                existing_type=sa.String(length=100),
                nullable=True)

        # Reverse MatchPlay table changes
        with op.batch_alter_table('matchplay', schema=None) as batch_op:
            batch_op.alter_column('first_name',
                existing_type=sa.String(length=50),
                nullable=True)
            batch_op.alter_column('last_name',
                existing_type=sa.String(length=50),
                nullable=True)

        # Reverse PlayerSetting table changes
        with op.batch_alter_table('playersetting', schema=None) as batch_op:
            batch_op.alter_column('user_id',
                existing_type=sa.Integer(),
                nullable=True)
            batch_op.alter_column('player_id',
                existing_type=sa.Integer(),
                nullable=True)

        # Reverse PlayerGroup table changes
        with op.batch_alter_table('playergroup', schema=None) as batch_op:
            batch_op.alter_column('user_id',
                existing_type=sa.Integer(),
                nullable=True)
            batch_op.alter_column('name',
                existing_type=sa.String(length=100),
                nullable=True)

    except Exception as e:
        raise Exception(f"Downgrade failed: {e}")