"""
Association model mapping roles to services with access metadata.
"""
from __future__ import annotations

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from services.shared.database.base import BaseModel


class RoleServiceAccess(BaseModel):
    """Links a role to a service with optional access level or scope."""

    __tablename__ = "role_service_accesses"
    __table_args__ = (
        UniqueConstraint("role_id", "service_id", name="uq_role_service"),
    )

    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    access_level = Column(String(50), nullable=True)  # e.g. read, manage, admin
    is_active = Column(Boolean, default=True, nullable=False)

    role = relationship("Role", back_populates="service_access_links")
    service = relationship("Service", back_populates="role_accesses")

    def __repr__(self) -> str:
        return f"<RoleServiceAccess(role_id={self.role_id}, service_id={self.service_id}, access_level={self.access_level})>"


