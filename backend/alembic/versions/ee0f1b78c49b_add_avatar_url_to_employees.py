"""add avatar_url to employees

Revision ID: ee0f1b78c49b
Revises: e81ea845b2af
Create Date: 2025-10-14 04:52:15.665210
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "ee0f1b78c49b"
down_revision: Union[str, Sequence[str], None] = "e81ea845b2af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Spalte für Avatar hinzufügen
    op.add_column(
        "employees",
        sa.Column("avatar_url", sa.String(length=255), nullable=True),
    )

    # Sicheres Entfernen alter Indizes (falls vorhanden)
    conn = op.get_bind()
    inspector = inspect(conn)

    def safe_drop_index(index_name: str, table: str):
        indexes = [idx["name"] for idx in inspector.get_indexes(table)]
        if index_name in indexes:
            print(f"🗑️  Dropping existing index {index_name} on {table} …")
            op.drop_index(index_name, table_name=table)
        else:
            print(f"⚠️  Index {index_name} not found on {table} — skipping drop.")

    safe_drop_index("idx_sl_employee_id", "sick_leaves")
    safe_drop_index("idx_vr_employee_id", "vacation_requests")


def downgrade() -> None:
    """Downgrade schema."""
    # Alte Indizes wiederherstellen
    op.create_index(
        "idx_vr_employee_id", "vacation_requests", ["employee_id"], unique=False
    )
    op.create_index("idx_sl_employee_id", "sick_leaves", ["employee_id"], unique=False)

    # Avatar-Spalte wieder entfernen
    op.drop_column("employees", "avatar_url")
