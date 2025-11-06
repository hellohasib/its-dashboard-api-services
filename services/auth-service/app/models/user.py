from __future__ import annotations

"""
User Model
"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from services.shared.database.base import BaseModel, Base
from .user_role import UserRole

if TYPE_CHECKING:
    from .role import Role


class User(BaseModel):
    """User model for authentication"""
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Profile fields
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    roles = relationship(
        "Role",
        secondary="user_roles",
        primaryjoin=lambda: User.id == UserRole.user_id,
        secondaryjoin=lambda: UserRole.role_id == Base.metadata.tables["roles"].c.id,
        back_populates="users",
        lazy="selectin"
    )
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role"""
        return any(role.name == role_name for role in self.roles)

    def has_permission(self, permission_name: str) -> bool:
        """
        Check if user has a specific permission
        Permission name can be in format 'resource:action' or just the permission name
        """
        for role in self.roles:
            for perm in role.permissions:
                # Check by full name (resource:action) or just name
                if perm.full_name == permission_name or perm.name == permission_name:
                    return True
        return False

