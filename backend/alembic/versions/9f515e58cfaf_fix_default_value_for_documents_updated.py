"""Fix default value for documents.updated

Revision ID: 9f515e58cfaf
Revises: add_audit_logs_table
Create Date: 2025-10-15 15:52:05.129905

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f515e58cfaf'
down_revision: Union[str, Sequence[str], None] = 'add_audit_logs_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("documents", "updated",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("CURRENT_TIMESTAMP")
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
