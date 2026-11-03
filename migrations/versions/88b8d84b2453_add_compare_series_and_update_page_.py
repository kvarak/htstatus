"""add compare, series and update page visit counters

Revision ID: 88b8d84b2453
Revises: 91f33075aad8
Create Date: 2026-11-03 17:29:05.339992

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88b8d84b2453'
down_revision = '91f33075aad8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('c_compare', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('c_series', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('c_update_page', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('users', 'c_update_page')
    op.drop_column('users', 'c_series')
    op.drop_column('users', 'c_compare')
