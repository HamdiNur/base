"""add label to permission

Revision ID: 461e6b724078
Revises: 2d5248a26161
Create Date: 2026-01-13 16:13:03.972426
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '461e6b724078'
down_revision = '2d5248a26161'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "permission",
        sa.Column("label", sa.String(length=150), nullable=True)
    )


def downgrade():
    op.drop_column("permission", "label")
