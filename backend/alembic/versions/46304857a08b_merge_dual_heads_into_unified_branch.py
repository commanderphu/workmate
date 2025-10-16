"""merge dual heads into unified branch

Revision ID: 46304857a08b
Revises: 9f515e58cfaf, dff97d9f27d8
Create Date: 2025-10-16 21:12:26.318807
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "46304857a08b"
down_revision: Union[str, Sequence[str], None] = ("9f515e58cfaf", "dff97d9f27d8")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    print("✅ Unified Alembic head — all migrations merged successfully.")


def downgrade() -> None:
    print("⚠️ Downgrade not supported for unified head.")
