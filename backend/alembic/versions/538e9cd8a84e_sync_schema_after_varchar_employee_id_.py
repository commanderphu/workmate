"""sync schema after varchar employee_id migration

Revision ID: 538e9cd8a84e
Revises: 7e02891eff18
Create Date: 2025-10-14 14:53:03.439272
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "538e9cd8a84e"
down_revision: Union[str, Sequence[str], None] = "994efb5b6a6d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # --- documents ---
    op.alter_column(
        "documents", "employee_id", existing_type=sa.VARCHAR(length=64), nullable=False
    )

    # 🛡️ Sicherstellen, dass der Index nur erstellt wird, wenn er nicht existiert
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_documents_employee_id ON documents (employee_id)"
    )

    # --- reminders ---
    op.alter_column(
        "reminders",
        "due_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
    )
    op.alter_column(
        "reminders",
        "reminder_time",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
    )
    op.alter_column("reminders", "status", existing_type=sa.TEXT(), nullable=False)

    # --- cleanup old unused indexes ---
    op.drop_index("ix_reminders_due_at", table_name="reminders", if_exists=True)
    op.drop_index(
        "ix_sick_leaves_document_id", table_name="sick_leaves", if_exists=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    # --- recreate dropped indexes ---
    op.create_index(
        "ix_sick_leaves_document_id", "sick_leaves", ["document_id"], unique=False
    )
    op.create_index("ix_reminders_due_at", "reminders", ["due_at"], unique=False)

    op.alter_column("reminders", "status", existing_type=sa.TEXT(), nullable=True)
    op.alter_column(
        "reminders",
        "reminder_time",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
    )
    op.alter_column(
        "reminders",
        "due_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
    )

    # --- documents ---
    op.drop_index(op.f("ix_documents_employee_id"), table_name="documents")
    op.alter_column(
        "documents", "employee_id", existing_type=sa.VARCHAR(length=64), nullable=True
    )
