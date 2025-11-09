"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters, underscores, and hyphens')
        return v


class UserLogin(BaseModel):
    """User login schema"""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


class TokenData(BaseModel):
    """Token data schema"""
    sub: str  # subject (user id or username)
    type: str  # token type (access or refresh)
    exp: int  # expiration timestamp


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    is_superuser: bool
    phone: Optional[str]
    department: Optional[str]
    roles: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)


class UserRolesUpdate(BaseModel):
    """User roles update schema"""
    roles: List[str] = Field(..., description="List of role names to assign to the user")

    @validator("roles", pre=True)
    def validate_roles_provided(cls, value):
        """Ensure the roles field is provided"""
        if value is None:
            raise ValueError("Roles list is required")
        return value

    @validator("roles", each_item=True)
    def validate_role_name(cls, role_name: str) -> str:
        """Ensure each role name is non-empty"""
        sanitized = role_name.strip()
        if not sanitized:
            raise ValueError("Role name cannot be empty")
        return sanitized

    @validator("roles")
    def validate_unique_roles(cls, roles: List[str]) -> List[str]:
        """Ensure role names are unique"""
        if len(set(roles)) != len(roles):
            raise ValueError("Duplicate roles are not allowed")
        return roles


class AdminUserUpdate(BaseModel):
    """Super admin user update schema"""
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    roles: Optional[List[str]] = Field(None, description="List of role names to assign to the user")

    @validator("roles", each_item=True)
    def validate_role_name(cls, role_name: str) -> str:
        """Ensure each role name is non-empty"""
        sanitized = role_name.strip()
        if not sanitized:
            raise ValueError("Role name cannot be empty")
        return sanitized

    @validator("roles")
    def validate_unique_roles(cls, roles: Optional[List[str]]) -> Optional[List[str]]:
        """Ensure role names are unique"""
        if roles is not None and len(set(roles)) != len(roles):
            raise ValueError("Duplicate roles are not allowed")
        return roles


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

