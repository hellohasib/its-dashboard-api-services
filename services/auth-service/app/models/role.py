from __future__ import annotations

"""
Role Model
"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship
from services.shared.database.base import BaseModel, Base
from .user_role import UserRole
from .role_service_access import RoleServiceAccess

if TYPE_CHECKING:
    from .user import User
    from .permission import Permission
    from .service import Service


class Role(BaseModel):
    """Role model for RBAC"""
    __tablename__ = "roles"

    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)  # System roles cannot be deleted

    # Relationships
    users = relationship(
        "User",
        secondary="user_roles",
        primaryjoin=lambda: Role.id == UserRole.role_id,
        secondaryjoin=lambda: UserRole.user_id == Base.metadata.tables["users"].c.id,
        back_populates="roles",
        lazy="selectin"
    )
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin"
    )
    service_access_links = relationship(
        "RoleServiceAccess",
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    services = relationship(
        "Service",
        secondary="role_service_accesses",
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"

