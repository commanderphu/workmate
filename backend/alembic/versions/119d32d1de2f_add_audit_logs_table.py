"""add audit_logs table

Revision ID: 119d32d1de2f
Revises: 39113ceebce3
Create Date: 2025-10-14 19:15:03.734316

"""
from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers
revision = "add_audit_logs_table"
down_revision = "39113ceebce3"

def upgrade():
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID, primary_key=True, default=uuid.uuid4),
        sa.Column("user_email", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource", sa.String(255), nullable=False),
        sa.Column("details", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table("audit_logs")
