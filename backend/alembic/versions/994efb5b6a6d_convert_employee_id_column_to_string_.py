"""
✅ FINALIZED MIGRATION
This migration converts employee_id from UUID → VARCHAR(64)
and links documents.employee_id → employees.employee_id (KIT-ID).
Do NOT modify or re-run. 15.10.2025 — Joshua Phu Bein
"""


from alembic import op
import sqlalchemy as sa

revision = "994efb5b6a6d"
down_revision = "e81ea845b2af"
branch_labels = None
depends_on = None


def upgrade():
    # 1️⃣ Neue Spalte mit ausreichender Länge
    op.add_column("documents", sa.Column("employee_id_str", sa.String(length=64), nullable=True))

    # 2️⃣ Business-ID übernehmen (KIT-0001 usw.)
    op.execute("""
        UPDATE documents d
        SET employee_id_str = e.employee_id
        FROM employees e
        WHERE e.id = d.employee_id;
    """)

    # 3️⃣ ForeignKey anpassen
    op.drop_constraint("documents_employee_id_fkey", "documents", type_="foreignkey")
    op.create_foreign_key(
        "fk_documents_employee_id_str_employees",
        "documents", "employees",
        ["employee_id_str"], ["employee_id"],
        ondelete="CASCADE",
    )

    # 4️⃣ Alte Spalte entfernen und umbenennen
    op.drop_column("documents", "employee_id")
    op.alter_column("documents", "employee_id_str", new_column_name="employee_id")


def downgrade():
    # 1️⃣ UUID-Spalte wiederherstellen
    op.add_column("documents", sa.Column("employee_id_uuid", sa.dialects.postgresql.UUID(), nullable=True))

    # 2️⃣ UUID aus employees anhand der KIT-ID rekonstruieren
    op.execute("""
        UPDATE documents d
        SET employee_id_uuid = e.id
        FROM employees e
        WHERE e.employee_id = d.employee_id;
    """)

    # 3️⃣ Constraints & Spalten zurücksetzen
    op.drop_constraint("fk_documents_employee_id_str_employees", "documents", type_="foreignkey")
    op.drop_column("documents", "employee_id")
    op.alter_column("documents", "employee_id_uuid", new_column_name="employee_id")

    op.create_foreign_key(
        "documents_employee_id_fkey",
        "documents", "employees",
        ["employee_id"], ["id"],
        ondelete="CASCADE",
    )
