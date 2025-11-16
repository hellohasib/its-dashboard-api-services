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
from services.shared.audit import record_event
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

        updated_fields = {
            key: getattr(user_data, key)
            for key in ["full_name", "phone", "department"]
            if getattr(user_data, key) is not None
        }
        record_event(
            action="user.profile.update",
            actor_id=str(user.id),
            target_id=str(user.id),
            target_type="user",
            description="User updated own profile",
            metadata={"updated_fields": updated_fields},
        )

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
        record_event(
            action="user.password.change",
            actor_id=str(user.id),
            target_id=str(user.id),
            target_type="user",
            description="User changed password",
        )
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
        updated_user = self.get_user_with_roles(user.id)

        record_event(
            action="user.roles.update",
            actor_id=str(assigned_by) if assigned_by is not None else str(user.id),
            target_id=str(user.id),
            target_type="user",
            description="User roles updated",
            metadata={"roles": [role.name for role in updated_user.roles]},
        )

        return updated_user

    def admin_update_user(self, user: User, user_data: AdminUserUpdate, assigned_by: Optional[int] = None) -> User:
        """Update user details as a super admin"""
        updated_fields = {}
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
            updated_fields["full_name"] = user_data.full_name
        if user_data.phone is not None:
            user.phone = user_data.phone
            updated_fields["phone"] = user_data.phone
        if user_data.department is not None:
            user.department = user_data.department
            updated_fields["department"] = user_data.department
        if user_data.notes is not None:
            user.notes = user_data.notes
            updated_fields["notes"] = user_data.notes
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
            updated_fields["is_active"] = user_data.is_active
        if user_data.is_verified is not None:
            user.is_verified = user_data.is_verified
            updated_fields["is_verified"] = user_data.is_verified

        self.db.commit()
        self.db.refresh(user)
        
        # Update roles if provided
        if user_data.roles is not None:
            user = self.update_user_roles(user, user_data.roles, assigned_by=assigned_by)
        
        if updated_fields:
            record_event(
                action="user.admin.update",
                actor_id=str(assigned_by) if assigned_by is not None else None,
                target_id=str(user.id),
                target_type="user",
                description="Admin updated user profile",
                metadata={"updated_fields": updated_fields},
            )

        return user

    def get_user_with_roles(self, user_id: int) -> Optional[User]:
        """Get user with roles loaded"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            # Trigger loading of roles
            _ = user.roles
        return user

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with their roles"""
        users = self.db.query(User).offset(skip).limit(limit).all()
        # Trigger loading of roles for all users
        for user in users:
            _ = user.roles
        return users

