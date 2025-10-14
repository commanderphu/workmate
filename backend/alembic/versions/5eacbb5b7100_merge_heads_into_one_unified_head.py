"""merge heads into one unified head

Revision ID: 5eacbb5b7100
Revises: fix_employee_id_to_string, d01249af0338
Create Date: 2025-10-14 14:46:07.038960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5eacbb5b7100'
down_revision: Union[str, Sequence[str], None] = ('fix_employee_id_to_string', 'd01249af0338')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
