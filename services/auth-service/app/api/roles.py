"""Role and service management endpoints for super admins."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query, status, Response
from sqlalchemy.orm import Session

from services.shared.database.session import get_db

from app.dependencies.auth import require_superuser, require_admin_or_superuser
from app.models.user import User
from app.schemas import (
    PermissionCreate,
    PermissionRead,
    PermissionSummary,
    PermissionUpdate,
    RoleCreate,
    RoleListItem,
    RoleRead,
    RoleServiceAccessRead,
    RoleServiceAccessUpdate,
    RoleUpdate,
    ServiceCreate,
    ServiceRead,
    ServiceUpdate,
)
from app.services import RoleManagementService

role_router = APIRouter(prefix="/roles")
service_router = APIRouter(prefix="/services")
permission_router = APIRouter(prefix="/permissions")


@role_router.get("/", response_model=List[RoleListItem])
def list_roles(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_superuser),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
) -> List[RoleListItem]:
    service = RoleManagementService(db)
    roles = service.list_roles(skip=skip, limit=limit)
    return [RoleListItem.model_validate(role) for role in roles]


@role_router.get("/permissions", response_model=List[PermissionSummary])
def list_permissions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_superuser),
    include_inactive: bool = Query(default=False),
) -> List[PermissionSummary]:
    service = RoleManagementService(db)
    permissions = service.list_permissions(include_inactive=include_inactive)
    return [PermissionSummary.model_validate(permission) for permission in permissions]


@role_router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(
    payload: RoleCreate,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
) -> RoleRead:
    service = RoleManagementService(db)
    role = service.create_role(payload, actor_id=current_user.id)
    return RoleRead.model_validate(role)


@role_router.get("/{role_id}", response_model=RoleRead)
def get_role(
    role_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
) -> RoleRead:
    service = RoleManagementService(db)
    role = service.get_role(role_id)
    return RoleRead.model_validate(role)


@role_router.put("/{role_id}", response_model=RoleRead)
def update_role(
    role_id: int,
    payload: RoleUpdate,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
) -> RoleRead:
    service = RoleManagementService(db)
    role = service.update_role(role_id, payload, actor_id=current_user.id)
    return RoleRead.model_validate(role)


@role_router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
) -> Response:
    service = RoleManagementService(db)
    service.delete_role(role_id, actor_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@role_router.patch(
    "/{role_id}/services/{service_id}", response_model=RoleServiceAccessRead
)
def update_role_service_access(
    role_id: int,
    service_id: int,
    payload: RoleServiceAccessUpdate,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
) -> RoleServiceAccessRead:
    service = RoleManagementService(db)
    link = service.update_service_access(role_id, service_id, payload, actor_id=current_user.id)
    return RoleServiceAccessRead.model_validate(link)


@service_router.get("/", response_model=List[ServiceRead])
def list_services(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
    include_inactive: bool = Query(default=False),
) -> List[ServiceRead]:
    service = RoleManagementService(db)
    services = service.list_services(include_inactive=include_inactive)
    return [ServiceRead.model_validate(item) for item in services]


@service_router.post("/", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(
    payload: ServiceCreate,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
) -> ServiceRead:
    service = RoleManagementService(db)
    record = service.create_service(payload, actor_id=current_user.id)
    return ServiceRead.model_validate(record)


@service_router.get("/{service_id}", response_model=ServiceRead)
def get_service(
    service_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
) -> ServiceRead:
    service = RoleManagementService(db)
    record = service.get_service(service_id)
    return ServiceRead.model_validate(record)


@service_router.put("/{service_id}", response_model=ServiceRead)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
) -> ServiceRead:
    service = RoleManagementService(db)
    record = service.update_service(service_id, payload, actor_id=current_user.id)
    return ServiceRead.model_validate(record)


@service_router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
) -> Response:
    service = RoleManagementService(db)
    service.delete_service(service_id, actor_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ------------------------------------------------------------------
# Permission CRUD endpoints (super_admin only)
# ------------------------------------------------------------------
@permission_router.get("/", response_model=List[PermissionRead])
def list_all_permissions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
    include_inactive: bool = Query(default=False),
) -> List[PermissionRead]:
    """
    List all permissions (super_admin only)
    """
    service = RoleManagementService(db)
    permissions = service.list_permissions(include_inactive=include_inactive)
    return [PermissionRead.model_validate(permission) for permission in permissions]


@permission_router.post("/", response_model=PermissionRead, status_code=status.HTTP_201_CREATED)
def create_permission(
    payload: PermissionCreate,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
) -> PermissionRead:
    """
    Create a new permission (super_admin only)
    """
    service = RoleManagementService(db)
    permission = service.create_permission(payload, actor_id=current_user.id)
    return PermissionRead.model_validate(permission)


@permission_router.get("/{permission_id}", response_model=PermissionRead)
def get_permission(
    permission_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
) -> PermissionRead:
    """
    Get permission by ID (super_admin only)
    """
    service = RoleManagementService(db)
    permission = service.get_permission(permission_id)
    return PermissionRead.model_validate(permission)


@permission_router.put("/{permission_id}", response_model=PermissionRead)
def update_permission(
    permission_id: int,
    payload: PermissionUpdate,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
) -> PermissionRead:
    """
    Update permission (super_admin only)
    """
    service = RoleManagementService(db)
    permission = service.update_permission(permission_id, payload, actor_id=current_user.id)
    return PermissionRead.model_validate(permission)


@permission_router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    permission_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
) -> Response:
    """
    Delete permission (super_admin only)
    """
    service = RoleManagementService(db)
    service.delete_permission(permission_id, actor_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
