import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from alembic import context

# Add backend dir to path so we can import our modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv()

from config import config as app_config
from db.base import Base
# Import all models so Base.metadata knows about them
import db.models  # noqa: F401

alembic_config = context.config

# Override sqlalchemy.url from our .env config
db_url = app_config.database_url
# Alembic needs sync driver: aiosqlite -> pysqlite, asyncpg -> psycopg2
if "aiosqlite" in db_url:
    db_url = db_url.replace("sqlite+aiosqlite", "sqlite")
elif "asyncpg" in db_url:
    db_url = db_url.replace("postgresql+asyncpg", "postgresql")
alembic_config.set_main_option("sqlalchemy.url", db_url)

if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = alembic_config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        alembic_config.get_section(alembic_config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # Required for SQLite ALTER support
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
