"""add training_week table (FEAT-035 training log; additive only)

Revision ID: d64f54235eb8
Revises: d090b5ccb65f
Create Date: 2026-11-01 15:11:58.815459

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd64f54235eb8'
down_revision = 'd090b5ccb65f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('training_week',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.Column('training_date', sa.Date(), nullable=False),
    sa.Column('training_type', sa.Integer(), nullable=True),
    sa.Column('intensity', sa.Integer(), nullable=True),
    sa.Column('stamina_share', sa.Integer(), nullable=True),
    sa.Column('trainer_id', sa.Integer(), nullable=True),
    sa.Column('trainer_name', sa.String(length=100), nullable=True),
    sa.Column('planned', sa.Boolean(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('team_id', 'training_date')
    )
    op.create_index(op.f('ix_training_week_team_id'), 'training_week', ['team_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_training_week_team_id'), table_name='training_week')
    op.drop_table('training_week')
