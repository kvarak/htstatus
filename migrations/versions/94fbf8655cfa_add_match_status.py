"""add match status

Revision ID: 94fbf8655cfa
Revises: 88b8d84b2453
Create Date: 2026-11-03 17:35:30.889079

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94fbf8655cfa'
down_revision = '88b8d84b2453'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('match', sa.Column('status', sa.String(length=20), nullable=True))


def downgrade():
    op.drop_column('match', 'status')
