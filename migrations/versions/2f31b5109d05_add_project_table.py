"""Add project table

Revision ID: 2f31b5109d05
Revises: 
Create Date: 2026-01-06 15:49:20.631941

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2f31b5109d05'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column(
        'role',
        'code',
        existing_type=sa.VARCHAR(length=50),
        nullable=False
    )

    op.create_unique_constraint(
        'uq_role_name',
        'role',
        ['name']
    )

    op.create_unique_constraint(
        'uq_role_code',
        'role',
        ['code']
    )


    # ### end Alembic commands ###


def downgrade():
    op.drop_constraint('uq_role_code', 'role', type_='unique')
    op.drop_constraint('uq_role_name', 'role', type_='unique')

    op.alter_column(
        'role',
        'code',
        existing_type=sa.VARCHAR(length=50),
        nullable=True
    )


    # ### end Alembic commands ###
