"""
Pydantic schemas for role, permission, and service access management.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PermissionBase(BaseModel):
    name: str = Field(..., max_length=100)
    resource: str = Field(..., max_length=100)
    action: str = Field(..., max_length=50)
    description: Optional[str] = None
    is_active: bool = True


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    resource: Optional[str] = Field(default=None, max_length=100)
    action: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PermissionRead(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PermissionSummary(BaseModel):
    id: int
    name: str
    resource: str
    action: str
    description: Optional[str] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class ServiceBase(BaseModel):
    name: str = Field(..., max_length=150)
    key: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=150)
    key: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ServiceRead(ServiceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoleServiceAccessBase(BaseModel):
    service_id: int
    access_level: Optional[str] = Field(default=None, max_length=50)
    is_active: bool = True


class RoleServiceAccessCreate(RoleServiceAccessBase):
    pass


class RoleServiceAccessUpdate(BaseModel):
    access_level: Optional[str] = Field(default=None, max_length=50)
    is_active: Optional[bool] = None


class RoleServiceAccessRead(RoleServiceAccessBase):
    id: int
    service: ServiceRead
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoleBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = Field(default=None, description="Initial permissions to attach.")
    service_access: Optional[List[RoleServiceAccessCreate]] = Field(
        default=None, description="Initial service access configuration."
    )
    is_system: bool = False


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None
    service_access: Optional[List[RoleServiceAccessCreate]] = None


class RoleRead(RoleBase):
    id: int
    is_system: bool
    permissions: List[PermissionSummary] = []
    services: List[ServiceRead] = []
    service_access_links: List[RoleServiceAccessRead] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoleListItem(RoleBase):
    id: int
    is_system: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


