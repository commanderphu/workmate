"""init employees schema

Revision ID: 57065dc124a9
Revises: 7bb9506e931d
Create Date: 2025-10-09 14:24:07.426443
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "57065dc124a9"
down_revision = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("employee_id", sa.String(length=32), nullable=False),
        sa.Column("department", sa.String(length=120)),
        sa.Column("position", sa.String(length=120)),
        sa.Column("start_date", sa.Date()),
        sa.Column("vacation_days_total", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("vacation_days_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("employee_id", name="uq_employees_employee_id"),
    )
    op.create_index("ix_employees_employee_id", "employees", ["employee_id"], unique=True)

def downgrade() -> None:
    op.drop_index("ix_employees_employee_id", table_name="employees")
    op.drop_table("employees")
