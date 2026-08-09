"""add user_enrollments table

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-09
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "bad0d87cf919"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_enrollments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("user_enrollments")
