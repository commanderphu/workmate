"""final unified head

Revision ID: final_unified_head
Revises: 9f515e58cfaf, dff97d9f27d8
Create Date: 2025-10-16 23:20:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "final_unified_head"
down_revision = ("9f515e58cfaf", "dff97d9f27d8")
branch_labels = None
depends_on = None


def upgrade():
    print("✅ Final unified head migration applied — schema fully merged.")


def downgrade():
    print("⚠️ Downgrade not supported for unified head.")
