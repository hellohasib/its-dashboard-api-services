"""
User service for user management
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional, List
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.schemas.auth import UserUpdate, PasswordChange, AdminUserUpdate
from app.utils.security import verify_password, get_password_hash


class UserService:
    """User service for managing user accounts"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def update_user_profile(self, user: User, user_data: UserUpdate) -> User:
        """Update user profile"""
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.phone is not None:
            user.phone = user_data.phone
        if user_data.department is not None:
            user.department = user_data.department
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def change_password(self, user: User, password_data: PasswordChange) -> bool:
        """Change user password"""
        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.hashed_password = get_password_hash(password_data.new_password)
        user.password_changed_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def update_user_roles(self, user: User, role_names: List[str], assigned_by: Optional[int] = None) -> User:
        """Replace the user's roles with the provided list"""
        # Ensure role names are unique while preserving order
        unique_role_names = list(dict.fromkeys(role_names))

        # Fetch active roles matching the provided names
        if unique_role_names:
            roles = (
                self.db.query(Role)
                .filter(Role.name.in_(unique_role_names), Role.is_active == True)
                .all()
            )
        else:
            roles = []

        found_role_names = {role.name for role in roles}
        missing_roles = [name for name in unique_role_names if name not in found_role_names]
        if missing_roles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Roles not found or inactive: {', '.join(missing_roles)}"
            )

        # Remove existing role assignments
        self.db.query(UserRole).filter(UserRole.user_id == user.id).delete(synchronize_session=False)
        self.db.flush()

        # Assign new roles
        for role in roles:
            self.db.add(UserRole(user_id=user.id, role_id=role.id, assigned_by=assigned_by))

        # Update superuser flag based on super_admin role assignment
        user.is_superuser = any(role.name == "super_admin" for role in roles)

        self.db.commit()

        # Reload user with roles
        return self.get_user_with_roles(user.id)

    def admin_update_user(self, user: User, user_data: AdminUserUpdate) -> User:
        """Update user details as a super admin"""
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.phone is not None:
            user.phone = user_data.phone
        if user_data.department is not None:
            user.department = user_data.department
        if user_data.notes is not None:
            user.notes = user_data.notes
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        if user_data.is_verified is not None:
            user.is_verified = user_data.is_verified

        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_with_roles(self, user_id: int) -> Optional[User]:
        """Get user with roles loaded"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            # Trigger loading of roles
            _ = user.roles
        return user

