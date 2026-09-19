from logging.config import fileConfig

from alembic import context

from backend.core.config import settings
from backend.core.database import Base

# Import all models so Alembic can detect their tables
from backend.models.user import User
from backend.models.document import Document
from backend.models.question import Question


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use the database URL from our .env file
config.set_main_option("sqlalchemy.url", settings.database_url)

# SQLAlchemy metadata used by Alembic for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    url = settings.database_url

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""

    from sqlalchemy import engine_from_config
    from sqlalchemy import pool

    connectable = engine_from_config(
        configuration=config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()