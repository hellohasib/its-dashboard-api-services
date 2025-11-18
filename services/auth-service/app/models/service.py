"""
Service model representing logical services accessible via roles.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship

from services.shared.database.base import BaseModel

if TYPE_CHECKING:
    from .role import Role
    from .role_service_access import RoleServiceAccess


class Service(BaseModel):
    """Service definition that can be assigned to roles."""

    __tablename__ = "services"

    name = Column(String(150), unique=True, nullable=False, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    roles = relationship(
        "Role",
        secondary="role_service_accesses",
        back_populates="services",
        lazy="selectin",
    )
    role_accesses = relationship(
        "RoleServiceAccess",
        back_populates="service",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Service(id={self.id}, key={self.key})>"


