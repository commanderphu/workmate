"""post-uuid-fix

Revision ID: 7e02891eff18
Revises: 5eacbb5b7100
Create Date: 2025-10-14 14:46:41.837602
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7e02891eff18"
down_revision: Union[str, Sequence[str], None] = "5eacbb5b7100"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with proper UUID casting."""
    # documents
    op.alter_column(
        "documents",
        "employee_id",
        existing_type=sa.VARCHAR(length=64),
        nullable=False,
    )

    # ✅ Statt create_index → sicherer SQL-Befehl
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_documents_employee_id ON documents (employee_id)"
    )

    # reminders
    op.drop_constraint(
        "fk_reminders_employee_id_employees", "reminders", type_="foreignkey"
    )
    op.alter_column(
        "reminders",
        "employee_id",
        existing_type=sa.VARCHAR(length=64),
        type_=sa.UUID(),
        existing_nullable=False,
        postgresql_using="employee_id::uuid",
    )
    op.create_foreign_key(
        None, "reminders", "employees", ["employee_id"], ["id"], ondelete="CASCADE"
    )

    # sick_leaves
    op.drop_constraint(
        "fk_sick_leaves_employee_id_employees", "sick_leaves", type_="foreignkey"
    )
    op.alter_column(
        "sick_leaves",
        "employee_id",
        existing_type=sa.VARCHAR(length=64),
        type_=sa.UUID(),
        existing_nullable=False,
        postgresql_using="employee_id::uuid",
    )
    op.create_foreign_key(
        None, "sick_leaves", "employees", ["employee_id"], ["id"], ondelete="CASCADE"
    )

    # time_entries
    op.drop_constraint(
        "fk_time_entries_employee_id_employees", "time_entries", type_="foreignkey"
    )
    op.alter_column(
        "time_entries",
        "employee_id",
        existing_type=sa.VARCHAR(length=64),
        type_=sa.UUID(),
        existing_nullable=False,
        postgresql_using="employee_id::uuid",
    )
    op.create_foreign_key(
        None, "time_entries", "employees", ["employee_id"], ["id"], ondelete="CASCADE"
    )

    # vacation_requests
    op.drop_constraint(
        "fk_vacation_requests_employee_id_employees",
        "vacation_requests",
        type_="foreignkey",
    )
    op.alter_column(
        "vacation_requests",
        "employee_id",
        existing_type=sa.VARCHAR(length=64),
        type_=sa.UUID(),
        existing_nullable=False,
        postgresql_using="employee_id::uuid",
    )
    op.create_foreign_key(
        None,
        "vacation_requests",
        "employees",
        ["employee_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema (reverse UUID fix)."""
    op.drop_constraint(None, "vacation_requests", type_="foreignkey")
    op.create_foreign_key(
        "fk_vacation_requests_employee_id_employees",
        "vacation_requests",
        "employees",
        ["employee_id"],
        ["employee_id"],
        ondelete="CASCADE",
    )
    op.alter_column(
        "vacation_requests",
        "employee_id",
        existing_type=sa.UUID(),
        type_=sa.VARCHAR(length=64),
        existing_nullable=False,
    )

    op.drop_constraint(None, "time_entries", type_="foreignkey")
    op.create_foreign_key(
        "fk_time_entries_employee_id_employees",
        "time_entries",
        "employees",
        ["employee_id"],
        ["employee_id"],
        ondelete="CASCADE",
    )
    op.alter_column(
        "time_entries",
        "employee_id",
        existing_type=sa.UUID(),
        type_=sa.VARCHAR(length=64),
        existing_nullable=False,
    )

    op.drop_constraint(None, "sick_leaves", type_="foreignkey")
    op.create_foreign_key(
        "fk_sick_leaves_employee_id_employees",
        "sick_leaves",
        "employees",
        ["employee_id"],
        ["employee_id"],
        ondelete="CASCADE",
    )
    op.alter_column(
        "sick_leaves",
        "employee_id",
        existing_type=sa.UUID(),
        type_=sa.VARCHAR(length=64),
        existing_nullable=False,
    )

    op.drop_constraint(None, "reminders", type_="foreignkey")
    op.create_foreign_key(
        "fk_reminders_employee_id_employees",
        "reminders",
        "employees",
        ["employee_id"],
        ["employee_id"],
        ondelete="CASCADE",
    )
    op.alter_column(
        "reminders",
        "employee_id",
        existing_type=sa.UUID(),
        type_=sa.VARCHAR(length=64),
        existing_nullable=False,
    )

    op.execute("DROP INDEX IF EXISTS ix_documents_employee_id")
    op.alter_column(
        "documents",
        "employee_id",
        existing_type=sa.VARCHAR(length=64),
        nullable=True,
    )
