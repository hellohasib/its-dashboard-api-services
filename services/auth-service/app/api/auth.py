"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from services.shared.database.session import get_db
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.dependencies.auth import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    """
    auth_service = AuthService(db)
    user = auth_service.register_user(user_data)
    
    # Convert to response model
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_superuser=user.is_superuser,
        phone=user.phone,
        department=user.department,
        roles=[role.name for role in user.roles],
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login user and get access token
    """
    auth_service = AuthService(db)
    
    # Get client IP and user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    token_response = auth_service.login(
        login_data=login_data,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    return token_response


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    auth_service = AuthService(db)
    token_response = auth_service.refresh_access_token(refresh_data.refresh_token)
    return token_response


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking refresh token
    """
    auth_service = AuthService(db)
    success = auth_service.logout(refresh_data.refresh_token)
    
    if success:
        return {"message": "Successfully logged out"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )


@router.post("/logout-all", status_code=status.HTTP_200_OK)
async def logout_all(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Logout user from all devices
    """
    auth_service = AuthService(db)
    auth_service.logout_all(current_user.id)
    return {"message": "Successfully logged out from all devices"}



