"""add comment to documents

Revision ID: 39113ceebce3
Revises: 538e9cd8a84e
Create Date: 2025-10-14 17:31:14.063132

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39113ceebce3'
down_revision: Union[str, Sequence[str], None] = '538e9cd8a84e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('documents', sa.Column('comment', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('documents', 'comment')

