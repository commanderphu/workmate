"""use unified enums for documents

Revision ID: aa503c802de3
Revises: ee0f1b78c49b
Create Date: 2025-10-14 10:38:04.810373
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "aa503c802de3"
down_revision: Union[str, Sequence[str], None] = "ee0f1b78c49b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema — unify document_type ENUM safely."""
    conn = op.get_bind()

    # ===========================
    # 🧩 Create ENUM if missing
    # ===========================
    existing_types = [
        r[0]
        for r in conn.execute(text("SELECT typname FROM pg_type WHERE typtype = 'e';"))
    ]

    if "documenttype" not in existing_types:
        conn.execute(
            text(
                """
                CREATE TYPE documenttype AS ENUM (
                    'bewerbung',
                    'krankenkasse',
                    'urlaub_bescheinigung',
                    'attest',
                    'urlaubsantrag',
                    'fehlzeit',
                    'sonstige'
                );
                """
            )
        )
        print("🧱 Created ENUM: documenttype")
    else:
        print("⚠️  ENUM documenttype already exists — skipping.")

    # ===========================
    # 🧠 Cast column safely
    # ===========================
    op.execute(
        text(
            """
            ALTER TABLE documents
            ALTER COLUMN document_type
            TYPE documenttype
            USING document_type::text::documenttype;
            """
        )
    )
    print("✅ Converted documents.document_type → ENUM(documenttype)")


def downgrade() -> None:
    """Downgrade schema — revert document_type back to VARCHAR."""
    op.execute(
        text(
            """
            ALTER TABLE documents
            ALTER COLUMN document_type
            TYPE VARCHAR(50)
            USING document_type::text;
            """
        )
    )
    print("↩️  Reverted documents.document_type to VARCHAR(50)")
