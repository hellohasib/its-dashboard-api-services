"""
User service for user management
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional
from app.models.user import User
from app.schemas.auth import UserUpdate, PasswordChange
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
    
    def get_user_with_roles(self, user_id: int) -> Optional[User]:
        """Get user with roles loaded"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            # Trigger loading of roles
            _ = user.roles
        return user

