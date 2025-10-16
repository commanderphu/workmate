"""Merge documenttype branches

Revision ID: dff97d9f27d8
Revises: abcdef_create_documenttype_and_documentstatus_enums, aa503c802de3
Create Date: 2025-10-14 11:03:37.781074

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dff97d9f27d8"
down_revision: Union[str, Sequence[str], None] = "aa503c802de3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
