"""merge orphan branch f123456789ab into main

Revision ID: d01249af0338
Revises: f123456789ab, 994efb5b6a6d
Create Date: 2025-10-14 13:33:28.356782

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd01249af0338'
down_revision: Union[str, Sequence[str], None] = ('f123456789ab', '994efb5b6a6d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
