"""
User-Role Association Table
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from services.shared.database.base import Base


class UserRole(Base):
    """Many-to-many relationship between Users and Roles"""
    __tablename__ = "user_roles"
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True, nullable=False, index=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id", name="fk_user_roles_assigned_by"), nullable=True)  # User who assigned this role
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Note: No id column - composite primary key (user_id, role_id) is sufficient

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"

