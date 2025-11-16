"""
User management API routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from services.shared.database.session import get_db
from app.schemas.auth import (
    UserUpdate,
    PasswordChange,
    UserResponse,
    UserRolesUpdate,
    AdminUserUpdate,
)
from app.services.user_service import UserService
from app.dependencies.auth import (
    get_current_active_user,
    require_permission,
    require_admin_or_superuser,
)
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_admin_or_superuser),
    db: Session = Depends(get_db)
):
    """
    Get all users (admin or superuser only)
    """
    user_service = UserService(db)
    users = user_service.get_all_users(skip=skip, limit=limit)
    
    return [
        UserResponse(
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
        for user in users
    ]


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's profile
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        is_superuser=current_user.is_superuser,
        phone=current_user.phone,
        department=current_user.department,
        roles=[role.name for role in current_user.roles],
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    """
    user_service = UserService(db)
    updated_user = user_service.update_user_profile(current_user, user_data)
    
    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        username=updated_user.username,
        full_name=updated_user.full_name,
        is_active=updated_user.is_active,
        is_verified=updated_user.is_verified,
        is_superuser=updated_user.is_superuser,
        phone=updated_user.phone,
        department=updated_user.department,
        roles=[role.name for role in updated_user.roles],
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
    )


@router.post("/me/change-password", status_code=status.HTTP_200_OK)
async def change_my_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password
    """
    user_service = UserService(db)
    user_service.change_password(current_user, password_data)
    return {"message": "Password changed successfully"}


@router.put("/{user_id}/roles", response_model=UserResponse)
async def update_user_roles(
    user_id: int,
    role_data: UserRolesUpdate,
    current_user: User = Depends(require_permission("role:write")),
    db: Session = Depends(get_db)
):
    """Update roles for a specific user"""
    user_service = UserService(db)
    user = user_service.get_user_with_roles(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    updated_user = user_service.update_user_roles(user, role_data.roles, assigned_by=current_user.id)

    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        username=updated_user.username,
        full_name=updated_user.full_name,
        is_active=updated_user.is_active,
        is_verified=updated_user.is_verified,
        is_superuser=updated_user.is_superuser,
        phone=updated_user.phone,
        department=updated_user.department,
        roles=[role.name for role in updated_user.roles],
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
    )


@router.patch("/{user_id}", response_model=UserResponse)
async def admin_update_user(
    user_id: int,
    user_data: AdminUserUpdate,
    current_user: User = Depends(require_admin_or_superuser),
    db: Session = Depends(get_db)
):
    """Update a user's details (admin or super admin only)"""
    user_service = UserService(db)
    user = user_service.get_user_with_roles(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    updated_user = user_service.admin_update_user(user, user_data, assigned_by=current_user.id)
    # Reload roles to ensure response reflects latest state
    updated_user = user_service.get_user_with_roles(updated_user.id)

    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        username=updated_user.username,
        full_name=updated_user.full_name,
        is_active=updated_user.is_active,
        is_verified=updated_user.is_verified,
        is_superuser=updated_user.is_superuser,
        phone=updated_user.phone,
        department=updated_user.department,
        roles=[role.name for role in updated_user.roles],
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
    )

