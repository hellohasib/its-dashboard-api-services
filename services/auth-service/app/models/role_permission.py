"""
Role-Permission Association Table
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from services.shared.database.base import Base


class RolePermission(Base):
    """Many-to-many relationship between Roles and Permissions"""
    __tablename__ = "role_permissions"
    __table_args__ = {'extend_existing': True}

    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Note: No id column - composite primary key (role_id, permission_id) is sufficient

    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"

