from __future__ import annotations

# --- add project root to sys.path ---
import os, sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
# ------------------------------------

from logging.config import fileConfig
import configparser

from alembic import context
from sqlalchemy import engine_from_config, pool

# === load .env (DATABASE_URL) ===
from dotenv import load_dotenv
load_dotenv()

# === import your models for autogenerate ===
from db.models import *  # noqa: F401,F403

config = context.config

# --- safe logging config (handle minimal alembic.ini) ---
if config.config_file_name:
    cp = configparser.ConfigParser()
    cp.read(config.config_file_name)
    has_logging = cp.has_section("formatters") and cp.has_section("handlers") and cp.has_section("loggers")
    if has_logging:
        fileConfig(config.config_file_name, disable_existing_loggers=False)

# --- set SQLAlchemy URL from .env ---
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL is not set in .env")
config.set_main_option("sqlalchemy.url", database_url)

# metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
