"""Add notifications."""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "c9d2e3f4a5b6"
down_revision: Union[str, Sequence[str], None] = "b8f1c2d3e4a5"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("notification_type", sa.String(length=50), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

def downgrade() -> None:
    op.drop_table("notifications")
