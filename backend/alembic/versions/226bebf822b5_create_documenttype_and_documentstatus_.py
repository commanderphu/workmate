"""create documenttype and documentstatus enums"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = "abcdef_create_documenttype_and_documentstatus_enums"
down_revision = "ee0f1b78c49b"
branch_labels = None
depends_on = None


def upgrade():
    # 🔹 Neue Enum-Typen in PostgreSQL erstellen
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'documenttype') THEN
                CREATE TYPE documenttype AS ENUM (
                    'bewerbung', 'krankenkasse', 'urlaub_bescheinigung',
                    'attest', 'urlaubsantrag', 'fehlzeit', 'sonstige'
                );
            END IF;

            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'documentstatus') THEN
                CREATE TYPE documentstatus AS ENUM (
                    'pending', 'approved', 'rejected'
                );
            END IF;
        END$$;
    """)

    # 🔹 Spalte in documents aktualisieren (falls vorher String war)
    op.alter_column(
        "documents",
        "document_type",
        type_=sa.Enum(
            "bewerbung", "krankenkasse", "urlaub_bescheinigung",
            "attest", "urlaubsantrag", "fehlzeit", "sonstige",
            name="documenttype"
        ),
        postgresql_using="document_type::text::documenttype",
    )

    op.alter_column(
        "documents",
        "status",
        type_=sa.Enum("pending", "approved", "rejected", name="documentstatus"),
        postgresql_using="status::text::documentstatus",
    )


def downgrade():
    # 🔹 Zurück auf Text, bevor Enum gelöscht wird
    op.alter_column("documents", "document_type", type_=sa.Text)
    op.alter_column("documents", "status", type_=sa.Text)

    # 🔹 Typen löschen (nur wenn leer)
    op.execute("DROP TYPE IF EXISTS documenttype CASCADE;")
    op.execute("DROP TYPE IF EXISTS documentstatus CASCADE;")
