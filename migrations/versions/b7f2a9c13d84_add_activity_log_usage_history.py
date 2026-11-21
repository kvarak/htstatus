"""Add activity_log table for daily usage history

Revision ID: b7f2a9c13d84
Revises: 94fbf8655cfa
Create Date: 2026-11-21 21:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7f2a9c13d84'
down_revision = '94fbf8655cfa'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'activity_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('activity', sa.String(length=50), nullable=False),
        sa.Column('day', sa.Date(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.ht_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'user_id', 'activity', 'day',
            name='uq_activity_log_user_activity_day'
        ),
    )
    op.create_index(
        op.f('ix_activity_log_user_id'), 'activity_log', ['user_id'], unique=False
    )


def downgrade():
    op.drop_index(op.f('ix_activity_log_user_id'), table_name='activity_log')
    op.drop_table('activity_log')
