"""
Alembic environment configuration
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Add parent directories to path to import shared modules
# Go up from: alembic/env.py -> auth-service -> services -> traffic-system-backend
current_dir = os.path.dirname(os.path.abspath(__file__))  # alembic/
auth_service_dir = os.path.dirname(current_dir)  # auth-service/
services_dir = os.path.dirname(auth_service_dir)  # services/
root_dir = os.path.dirname(services_dir)  # traffic-system-backend/

# Add root directory to path so we can import 'services.shared'
sys.path.insert(0, root_dir)
# Also add auth-service directory so we can import 'app.models'
sys.path.insert(0, auth_service_dir)

# Import shared database base
from services.shared.database.base import Base
from services.shared.database.session import DATABASE_URL

# this is the Alembic Config object
config = context.config

# Get database URL - construct from environment variables or alembic.ini
from urllib.parse import quote_plus
import os

# Check if DB_PASS environment variable is explicitly set
db_pass_env = os.getenv("DB_PASS", "")

if db_pass_env:
    # Use environment variables - URL-encode password properly
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "its_dashboard")
    db_user = os.getenv("DB_USER", "root")
    encoded_pass = quote_plus(db_pass_env)
    db_url = f"mysql+pymysql://{db_user}:{encoded_pass}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    config.attributes['sqlalchemy.url'] = db_url
    print("Using database URL from environment variables")
else:
    # Read from alembic.ini config file
    try:
        # Get alembic section from config
        alembic_section = config.get_section("alembic") or {}
        
        # Read individual components (with fallbacks)
        db_host = alembic_section.get("db_host", "localhost")
        db_port = alembic_section.get("db_port", "3306")
        db_name = alembic_section.get("db_name", "its_dashboard")
        db_user = alembic_section.get("db_user", "traffic_db_user")
        db_password = alembic_section.get("db_password", "")
        
        if db_password:
            # URL-encode the password from ini file
            encoded_pass = quote_plus(db_password)
            db_url = f"mysql+pymysql://{db_user}:{encoded_pass}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
            config.attributes['sqlalchemy.url'] = db_url
            print("Using database URL from alembic.ini configuration")
        else:
            # Fallback to sqlalchemy.url if individual components not found
            db_url_from_config = config.get_main_option("sqlalchemy.url")
            if db_url_from_config:
                config.attributes['sqlalchemy.url'] = db_url_from_config
                print("Using database URL from alembic.ini (fallback)")
            else:
                raise ValueError("No password found in alembic.ini. Please set db_password or use environment variables")
    except Exception as e:
        # Final fallback - try to read sqlalchemy.url directly
        db_url_from_config = config.get_main_option("sqlalchemy.url")
        if db_url_from_config:
            config.attributes['sqlalchemy.url'] = db_url_from_config
            print(f"Using database URL from alembic.ini sqlalchemy.url (warning: {e})")
        else:
            raise ValueError(f"Failed to configure database URL. Error: {e}. Please set DB_PASS environment variable or fix alembic.ini configuration.")

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models here so Alembic can detect them
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.refresh_token import RefreshToken
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission

# Set target metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.attributes.get("sqlalchemy.url") or config.get_main_option("sqlalchemy.url")
    if not url:
        raise ValueError("No database URL configured for offline migrations")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Inject custom URL into config section to avoid interpolation issues
    section = config.get_section(config.config_ini_section, {}).copy()
    db_url_override = config.attributes.get("sqlalchemy.url")
    if db_url_override:
        section["sqlalchemy.url"] = db_url_override

    connectable = engine_from_config(
        section,
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

