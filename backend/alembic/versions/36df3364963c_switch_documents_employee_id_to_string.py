"""convert employee_id from UUID → String(20)"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic
revision = "f123456789ab"
down_revision = "dff97d9f27d8"
branch_labels = None
depends_on = None


def upgrade():
    # 1️⃣ Temporäre Spalte anlegen
    op.add_column("documents", sa.Column("employee_id_str", sa.String(length=20), nullable=True))

    # 2️⃣ Bestehende UUID-Werte als Text übertragen
    op.execute("UPDATE documents SET employee_id_str = employee_id::text")

    # 3️⃣ ForeignKey vorbereiten (auf employee_id in employees)
    op.create_foreign_key(
        "fk_documents_employee_id_str_employees",
        "documents", "employees",
        ["employee_id_str"], ["employee_id"],
        ondelete="CASCADE",
    )

    # 4️⃣ Alte Spalte & Constraint entfernen
    op.drop_constraint("documents_employee_id_fkey", "documents", type_="foreignkey")
    op.drop_column("documents", "employee_id")

    # 5️⃣ Umbenennen auf employee_id
    op.alter_column("documents", "employee_id_str", new_column_name="employee_id")


def downgrade():
    # Rückmigration: String → UUID
    op.add_column(
        "documents",
        sa.Column("employee_id_uuid", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.execute("UPDATE documents SET employee_id_uuid = employee_id::uuid")

    op.drop_constraint("fk_documents_employee_id_str_employees", "documents", type_="foreignkey")
    op.drop_column("documents", "employee_id")

    op.alter_column("documents", "employee_id_uuid", new_column_name="employee_id")

    op.create_foreign_key(
        "documents_employee_id_fkey",
        "documents", "employees",
        ["employee_id"], ["id"],
        ondelete="CASCADE",
    )
