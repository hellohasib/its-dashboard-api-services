"""
Authentication and authorization dependencies
"""
from .auth import (
    get_current_user,
    get_current_active_user,
    require_permission,
    require_role,
    require_superuser,
    require_admin_or_superuser,
)

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "require_permission",
    "require_role",
    "require_superuser",
    "require_admin_or_superuser",
]

