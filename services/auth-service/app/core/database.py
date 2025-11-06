"""
Database initialization for auth service
"""
from services.shared.database.session import engine
from services.shared.database.base import Base
from app.models import *  # Import all models to register them


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all tables - USE WITH CAUTION"""
    Base.metadata.drop_all(bind=engine)

