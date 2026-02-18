import os
from sqlalchemy import create_engine
from alembic import context
from database import Base  # Stelle sicher, dass Base importiert wird!

target_metadata = Base.metadata

# ✅ Supabase-Datenbank-URL aus der Umgebung holen
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "❌ ERROR: DATABASE_URL is not set!"
        "Make sure it is configured in your environment."
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
target_metadata = Base.metadata

config = context.config


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
