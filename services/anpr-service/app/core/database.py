"""
Database initialization utilities for the ANPR service.
"""
from services.shared.database.session import engine
from services.shared.database.base import Base


def init_db() -> None:
    """
    Initialize database tables for the ANPR service.
    Import models to ensure they are registered with SQLAlchemy metadata
    before creating the tables.
    """
    # Import models to register them with the Base metadata
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Drop all ANPR service tables.
    """
    from app import models  # noqa: F401

    Base.metadata.drop_all(bind=engine)


