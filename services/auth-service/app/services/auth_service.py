"""
Authentication service
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from services.shared.audit import record_event
from services.shared.config.settings import settings


class AuthService:
    """Authentication service for handling user authentication"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, user_data: UserRegister) -> User:
        """
        Register a new user
        """
        # Check if email already exists
        if self.db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        if self.db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            phone=user_data.phone,
            department=user_data.department,
            is_active=True,
            is_verified=False,
            is_superuser=False,
            password_changed_at=datetime.utcnow(),
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        record_event(
            action="auth.register",
            actor_id=str(user.id),
            target_id=str(user.id),
            target_type="user",
            description="User account created",
            metadata={
                "email": user.email,
                "username": user.username,
            },
        )

        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password
        """
        user = self.db.query(User).filter(User.username == username).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def login(self, login_data: UserLogin, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> TokenResponse:
        """
        Login user and generate tokens
        """
        # First, try to find user by username
        user = self.db.query(User).filter(User.username == login_data.username).first()
        
        # If user exists but password is wrong, handle failed login
        if user and not verify_password(login_data.password, user.hashed_password):
            self._handle_failed_login(user)
            record_event(
                action="auth.login",
                actor_id=str(user.id),
                status="failure",
                description="Invalid credentials",
                metadata={"username": login_data.username},
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # If user doesn't exist, raise error (but don't increment attempts)
        if not user:
            record_event(
                action="auth.login",
                actor_id=None,
                status="failure",
                description="Invalid credentials",
                metadata={"username": login_data.username},
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Check if user is active
        if not user.is_active:
            record_event(
                action="auth.login",
                actor_id=str(user.id),
                status="failure",
                description="Inactive account",
                metadata={"username": login_data.username},
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            record_event(
                action="auth.login",
                actor_id=str(user.id),
                status="failure",
                description="Account locked",
                metadata={
                    "locked_until": user.locked_until.isoformat(),
                    "username": login_data.username,
                },
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is locked"
            )
        
        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        
        # Create tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token_str = create_refresh_token(data={"sub": str(user.id)})
        
        # Store refresh token in database
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = RefreshToken(
            token=refresh_token_str,
            user_id=user.id,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            is_revoked=False,
        )
        
        self.db.add(refresh_token)
        self.db.commit()

        record_event(
            action="auth.login",
            actor_id=str(user.id),
            target_id=str(user.id),
            target_type="user",
            description="User logged in",
            metadata={
                "refresh_token_id": refresh_token.id,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    
    def refresh_access_token(self, refresh_token_str: str) -> TokenResponse:
        """
        Refresh access token using refresh token
        """
        # Decode refresh token
        payload = decode_token(refresh_token_str)
        
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Check if refresh token exists in database and is valid
        refresh_token = self.db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token_str,
            RefreshToken.user_id == int(user_id),
            RefreshToken.is_revoked == False,
        ).first()
        
        if not refresh_token:
            record_event(
                action="auth.refresh",
                actor_id=str(user_id) if user_id else None,
                status="failure",
                description="Refresh token revoked or missing",
                metadata={"token": "***"},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found or revoked"
            )
        
        if refresh_token.is_expired():
            record_event(
                action="auth.refresh",
                actor_id=str(user_id) if user_id else None,
                status="failure",
                description="Refresh token expired",
                metadata={"token": "***"},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        
        # Get user
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            record_event(
                action="auth.refresh",
                actor_id=str(user_id) if user_id else None,
                status="failure",
                description="User not found or inactive",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        record_event(
            action="auth.refresh",
            actor_id=str(user.id),
            target_id=str(user.id),
            target_type="user",
            description="Access token refreshed",
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    
    def logout(self, refresh_token_str: str) -> bool:
        """
        Logout user by revoking refresh token
        """
        refresh_token = self.db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token_str,
            RefreshToken.is_revoked == False,
        ).first()
        
        if refresh_token:
            refresh_token.is_revoked = True
            refresh_token.revoked_at = datetime.utcnow()
            self.db.commit()
            record_event(
                action="auth.logout",
                actor_id=str(refresh_token.user_id),
                target_id=str(refresh_token.user_id),
                target_type="user",
                description="User logged out",
                metadata={"refresh_token_id": refresh_token.id},
            )
            return True
        
        record_event(
            action="auth.logout",
            status="failure",
            description="Refresh token not found",
        )
        return False
    
    def logout_all(self, user_id: int) -> bool:
        """
        Logout user from all devices by revoking all refresh tokens
        """
        refresh_tokens = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
        ).all()
        
        for token in refresh_tokens:
            token.is_revoked = True
            token.revoked_at = datetime.utcnow()
        
        self.db.commit()
        record_event(
            action="auth.logout_all",
            actor_id=str(user_id),
            target_id=str(user_id),
            target_type="user",
            description="All refresh tokens revoked",
            metadata={"revoked_tokens": len(refresh_tokens)},
        )
        return True
    
    def _handle_failed_login(self, user: Optional[User]):
        """
        Handle failed login attempt
        """
        if not user:
            return
        
        user.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts for 30 minutes
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        self.db.commit()

