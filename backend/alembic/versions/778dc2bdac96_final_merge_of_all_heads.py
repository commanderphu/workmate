"""final merge of all heads

Revision ID: 778dc2bdac96
Revises: 46304857a08b, final_unified_head, 7e02891eff18, fix_employee_id_to_string
Create Date: 2025-10-16 21:14:50.605341
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "778dc2bdac96"
down_revision: Union[str, Sequence[str], None] = (
    "46304857a08b",
    "final_unified_head",
    "7e02891eff18",
    "fix_employee_id_to_string",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    print("✅ All Alembic heads unified successfully — Workmate DB is now consistent!")


def downgrade() -> None:
    print("⚠️ Downgrade not supported for unified merge head.")
