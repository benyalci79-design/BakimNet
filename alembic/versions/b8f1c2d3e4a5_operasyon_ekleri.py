"""Add operational tables and fields."""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b8f1c2d3e4a5"
down_revision: Union[str, Sequence[str], None] = "7616e0c72982"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("problem_reports", sa.Column("photo_url", sa.String(length=255), nullable=True))
    op.create_table(
        "spare_parts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("stock_quantity", sa.Integer(), nullable=False),
        sa.Column("critical_level", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "part_usages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("work_order_id", sa.Integer(), nullable=False),
        sa.Column("spare_part_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"]),
        sa.ForeignKeyConstraint(["spare_part_id"], ["spare_parts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "work_order_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("work_order_id", sa.Integer(), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=False),
        sa.Column("old_status", sa.String(length=30), nullable=True),
        sa.Column("new_status", sa.String(length=30), nullable=False),
        sa.Column("changed_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"]),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("work_order_history")
    op.drop_table("part_usages")
    op.drop_table("spare_parts")
    op.drop_column("problem_reports", "photo_url")
    op.drop_column("users", "is_active")
