import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# 👉 deine SQLAlchemy Base + Models importieren
from app.database import Base
from app import models  # noqa: F401  (stellt sicher, dass alle Tabellen registriert sind)

# Alembic Config
config = context.config

# Logging aus alembic.ini aktivieren
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ⚠️ DB-URL aus Umgebungsvariable nehmen (Compose setzt DATABASE_URL):
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", ""))

# 👇 wichtig für autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,  # Typänderungen erkennen
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Typänderungen erkennen
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
