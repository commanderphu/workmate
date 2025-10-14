"""Convert employee_id columns in all tables from UUID → String(64)"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "fix_employee_id_to_string"
down_revision = "994efb5b6a6d"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    tables = [
        "sick_leaves",
        "vacation_requests",
        "reminders",
        "time_entries",
    ]

    for table in tables:
        print(f"🔧 Migrating {table}...")

        # 1️⃣ Drop existing FK if found
        fks = inspector.get_foreign_keys(table)
        for fk in fks:
            if fk.get("constrained_columns") == ["employee_id"]:
                op.drop_constraint(fk["name"], table, type_="foreignkey")

        # 2️⃣ Add temporary new column
        tmp_col = "employee_id_str"
        op.add_column(table, sa.Column(tmp_col, sa.String(length=64), nullable=True))

        # 3️⃣ Copy old UUID data as text
        op.execute(f"UPDATE {table} SET {tmp_col} = employee_id::text")

        # 4️⃣ Drop old column
        op.drop_column(table, "employee_id")

        # 5️⃣ Rename temp column → employee_id
        op.alter_column(table, tmp_col, new_column_name="employee_id")

        # 6️⃣ Add new FK to employees(employee_id)
        op.create_foreign_key(
            f"fk_{table}_employee_id_employees",
            table,
            "employees",
            ["employee_id"],
            ["employee_id"],
            ondelete="CASCADE",
        )


def downgrade():
    pass
