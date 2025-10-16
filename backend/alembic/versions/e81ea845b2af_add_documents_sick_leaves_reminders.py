"""add documents, sick_leaves, reminders

Revision ID: e81ea845b2af
Revises: 57065dc124a9
Create Date: 2025-10-09 14:58:25.439566
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e81ea845b2af"
down_revision: Union[str, Sequence[str], None] = "57065dc124a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with safe ENUM creation."""
    conn = op.get_bind()
    existing_types = [
        r[0]
        for r in conn.execute(text("SELECT typname FROM pg_type WHERE typtype='e'"))
    ]

    # ---- ENUMS ----
    if "documentstatus" not in existing_types:
        conn.execute(
            text(
                "CREATE TYPE documentstatus AS ENUM ('pending', 'received', 'processed');"
            )
        )
        print("🧱 Created ENUM: documentstatus")
    else:
        print("⚠️ ENUM documentstatus already exists — skipping")

    if "vacationstatus" not in existing_types:
        conn.execute(
            text(
                "CREATE TYPE vacationstatus AS ENUM ('pending', 'approved', 'rejected');"
            )
        )
        print("🧱 Created ENUM: vacationstatus")
    else:
        print("⚠️ ENUM vacationstatus already exists — skipping")

    # ---- TABLES ----
    op.create_table(
        "documents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("employee_id", sa.UUID(), nullable=False),
        sa.Column("document_type", sa.String(length=50), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("file_url", sa.Text(), nullable=True),
        sa.Column("is_original_required", sa.Boolean(), nullable=False),
        # ✅ fix: use postgresql.ENUM to *reference*, not recreate
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "received",
                "processed",
                name="documentstatus",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("upload_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "vacation_requests",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("employee_id", sa.UUID(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        # ✅ same fix
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "approved",
                "rejected",
                name="vacationstatus",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("representative", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ---- Other tables ----
    op.create_table(
        "reminders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("employee_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("reminder_time", sa.DateTime(), nullable=True),
        sa.Column("status", sa.Text(), nullable=True),
        sa.Column("linked_to", sa.Text(), nullable=True),
        sa.Column(
            "created",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "time_entries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("employee_id", sa.UUID(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "sick_leaves",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("employee_id", sa.UUID(), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("sick_leaves")
    op.drop_table("time_entries")
    op.drop_table("reminders")
    op.drop_table("vacation_requests")
    op.drop_table("documents")
