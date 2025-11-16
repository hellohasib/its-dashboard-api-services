"""
ANPR Service - License Plate Recognition Data Handling
"""

from .api import api_router  # noqa: F401
from . import models  # noqa: F401
from .core import init_db  # noqa: F401

__all__ = ["api_router", "init_db", "models"]

