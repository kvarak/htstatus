"""add match_position_minutes table (FEAT-036 who got trained; additive only)

Revision ID: 91f33075aad8
Revises: d64f54235eb8
Create Date: 2026-11-01 15:27:34.423180

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91f33075aad8'
down_revision = 'd64f54235eb8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('match_position_minutes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('match_id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('minutes', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('match_id', 'team_id', 'player_id', 'role_id')
    )
    op.create_index(op.f('ix_match_position_minutes_match_id'), 'match_position_minutes', ['match_id'], unique=False)
    op.create_index(op.f('ix_match_position_minutes_team_id'), 'match_position_minutes', ['team_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_match_position_minutes_team_id'), table_name='match_position_minutes')
    op.drop_index(op.f('ix_match_position_minutes_match_id'), table_name='match_position_minutes')
    op.drop_table('match_position_minutes')
