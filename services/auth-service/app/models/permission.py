"""
Permission Model
"""
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.orm import relationship
from services.shared.database.base import BaseModel


class Permission(BaseModel):
    """Permission model for RBAC"""
    __tablename__ = "permissions"

    name = Column(String(100), unique=True, index=True, nullable=False)
    resource = Column(String(100), nullable=False, index=True)  # e.g., 'anpr', 'camera', 'user'
    action = Column(String(50), nullable=False)  # e.g., 'read', 'write', 'delete', 'manage'
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="dynamic"
    )

    def __repr__(self):
        return f"<Permission(id={self.id}, name={self.name}, resource={self.resource}, action={self.action})>"

    @property
    def full_name(self) -> str:
        """Get full permission name as resource:action"""
        return f"{self.resource}:{self.action}"

