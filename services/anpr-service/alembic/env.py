"""
Alembic environment configuration for ANPR service
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Add parent directories to path to import shared modules
# Go up from: alembic/env.py -> anpr-service -> services -> traffic-system-backend
current_dir = os.path.dirname(os.path.abspath(__file__))  # alembic/
anpr_service_dir = os.path.dirname(current_dir)  # anpr-service/
services_dir = os.path.dirname(anpr_service_dir)  # services/
root_dir = os.path.dirname(services_dir)  # traffic-system-backend/

# Add root directory to path so we can import 'services.shared'
sys.path.insert(0, root_dir)
# Also add anpr-service directory so we can import 'app.models'
sys.path.insert(0, anpr_service_dir)

from services.shared.database.base import Base
from services.shared.database.session import DATABASE_URL

# Import ANPR service models to register metadata
from app import models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import ANPR models here when created
# from app.models.camera import Camera
# from app.models.lpr_detection import LPRDetection

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
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
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

