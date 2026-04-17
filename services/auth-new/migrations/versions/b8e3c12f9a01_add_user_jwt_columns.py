"""add user jwt token columns

Revision ID: b8e3c12f9a01
Revises: 982163127e21
Create Date: 2026-03-28

"""
from alembic import op
import sqlalchemy as sa


revision = "b8e3c12f9a01"
down_revision = "982163127e21"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("access_jwt", sa.Text(), nullable=True),
        )
        batch_op.add_column(
            sa.Column("refresh_jwt", sa.Text(), nullable=True),
        )


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("refresh_jwt")
        batch_op.drop_column("access_jwt")
