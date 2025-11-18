"""
Role management service for super admin operations.
"""

from __future__ import annotations

from typing import Iterable, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from services.shared.audit import record_event

from app.models import Permission, Role, RoleServiceAccess, Service
from app.schemas.role import (
    PermissionCreate,
    PermissionUpdate,
    RoleCreate,
    RoleServiceAccessCreate,
    RoleServiceAccessUpdate,
    RoleUpdate,
    ServiceCreate,
    ServiceUpdate,
)


class RoleManagementService:
    """Business logic for managing roles, permissions, and service access."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Role operations
    # ------------------------------------------------------------------
    def list_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        return (
            self.db.query(Role)
            .options(
                joinedload(Role.permissions),
                joinedload(Role.services),
                joinedload(Role.service_access_links).joinedload(RoleServiceAccess.service),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_role(self, role_id: int) -> Role:
        role = (
            self.db.query(Role)
            .options(
                joinedload(Role.permissions),
                joinedload(Role.services),
                joinedload(Role.service_access_links).joinedload(RoleServiceAccess.service),
            )
            .filter(Role.id == role_id)
            .first()
        )
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        return role

    def create_role(self, payload: RoleCreate, *, actor_id: Optional[int] = None) -> Role:
        existing = self.db.query(Role).filter(Role.name == payload.name).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role name already exists")

        role = Role(
            name=payload.name,
            description=payload.description,
            is_active=payload.is_active,
            is_system=payload.is_system,
        )
        self.db.add(role)
        self.db.flush()

        if payload.permission_ids:
            permissions = self._fetch_permissions_or_404(payload.permission_ids)
            role.permissions = list(permissions)

        if payload.service_access:
            self._apply_service_access(role, payload.service_access)

        self.db.commit()
        self.db.refresh(role)

        record_event(
            action="role.create",
            actor_id=str(actor_id) if actor_id else None,
            target_id=str(role.id),
            target_type="role",
            description=f"Created role {role.name}",
            metadata={
                "permissions": [perm.id for perm in role.permissions],
                "services": [link.service_id for link in role.service_access_links],
            },
        )
        return role

    def update_role(self, role_id: int, payload: RoleUpdate, *, actor_id: Optional[int] = None) -> Role:
        role = self.get_role(role_id)
        if role.is_system and (payload.name or payload.is_active is False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="System roles cannot be renamed or deactivated",
            )

        updated_fields = {}
        if payload.name and payload.name != role.name:
            conflict = self.db.query(Role).filter(Role.name == payload.name, Role.id != role.id).first()
            if conflict:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role name already exists")
            role.name = payload.name
            updated_fields["name"] = payload.name
        if payload.description is not None:
            role.description = payload.description
            updated_fields["description"] = payload.description
        if payload.is_active is not None and payload.is_active != role.is_active:
            role.is_active = payload.is_active
            updated_fields["is_active"] = payload.is_active

        if payload.permission_ids is not None:
            permissions = self._fetch_permissions_or_404(payload.permission_ids)
            role.permissions = list(permissions)
            updated_fields["permissions"] = payload.permission_ids

        if payload.service_access is not None:
            self._apply_service_access(role, payload.service_access)
            updated_fields["service_access"] = [access.model_dump() for access in payload.service_access]

        self.db.commit()
        self.db.refresh(role)

        record_event(
            action="role.update",
            actor_id=str(actor_id) if actor_id else None,
            target_id=str(role.id),
            target_type="role",
            description=f"Updated role {role.name}",
            metadata=updated_fields,
        )
        return role

    def delete_role(self, role_id: int, *, actor_id: Optional[int] = None) -> None:
        role = self.get_role(role_id)
        if role.is_system:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="System roles cannot be deleted")
        self.db.delete(role)
        self.db.commit()
        record_event(
            action="role.delete",
            actor_id=str(actor_id) if actor_id else None,
            target_id=str(role_id),
            target_type="role",
            description="Deleted role",
        )

    # ------------------------------------------------------------------
    # Service access helpers
    # ------------------------------------------------------------------
    def _apply_service_access(self, role: Role, access_payloads: Iterable[RoleServiceAccessCreate]) -> None:
        payloads = list(access_payloads)
        payload_service_ids = {item.service_id for item in payloads}
        existing_links = {link.service_id: link for link in role.service_access_links}

        for service_id, link in list(existing_links.items()):
            if service_id not in payload_service_ids:
                self.db.delete(link)

        for item in payloads:
            service = (
                self.db.query(Service)
                .filter(Service.id == item.service_id, Service.is_active == True)
                .first()
            )
            if not service:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Service {item.service_id} not found or inactive",
                )

            link = existing_links.get(item.service_id)
            if link:
                link.access_level = item.access_level
                link.is_active = item.is_active
            else:
                link = RoleServiceAccess(
                    role_id=role.id,
                    service_id=service.id,
                    access_level=item.access_level,
                    is_active=item.is_active,
                )
                self.db.add(link)

    def update_service_access(
        self,
        role_id: int,
        service_id: int,
        payload: RoleServiceAccessUpdate,
        *,
        actor_id: Optional[int] = None,
    ) -> RoleServiceAccess:
        role = self.get_role(role_id)
        link = next((link for link in role.service_access_links if link.service_id == service_id), None)
        if not link:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service access not found for role")

        if payload.access_level is not None:
            link.access_level = payload.access_level
        if payload.is_active is not None:
            link.is_active = payload.is_active

        self.db.commit()
        self.db.refresh(link)

        record_event(
            action="role.service_access.update",
            actor_id=str(actor_id) if actor_id else None,
            target_id=str(role_id),
            target_type="role",
            description="Updated role service access",
            metadata={"service_id": service_id, **payload.model_dump(exclude_none=True)},
        )
        return link

    # ------------------------------------------------------------------
    # Service catalogue operations
    # ------------------------------------------------------------------
    def list_services(self, *, include_inactive: bool = False) -> List[Service]:
        query = self.db.query(Service)
        if not include_inactive:
            query = query.filter(Service.is_active == True)
        return query.order_by(Service.name.asc()).all()

    def list_permissions(self, *, include_inactive: bool = False) -> List[Permission]:
        query = self.db.query(Permission)
        if not include_inactive:
            query = query.filter(Permission.is_active == True)
        return query.order_by(Permission.resource.asc(), Permission.action.asc()).all()

    # ------------------------------------------------------------------
    # Permission operations
    # ------------------------------------------------------------------
    def get_permission(self, permission_id: int) -> Permission:
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        if not permission:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
        return permission

    def create_permission(self, payload: PermissionCreate, *, actor_id: Optional[int] = None) -> Permission:
        # Check if permission with same name already exists
        existing = self.db.query(Permission).filter(Permission.name == payload.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permission with this name already exists"
            )

        permission = Permission(
            name=payload.name,
            resource=payload.resource,
            action=payload.action,
            description=payload.description,
            is_active=payload.is_active,
        )
        self.db.add(permission)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permission already exists"
            )
        self.db.refresh(permission)

        record_event(
            action="permission.create",
            actor_id=str(actor_id) if actor_id else None,
            target_id=str(permission.id),
            target_type="permission",
            description=f"Created permission {permission.name}",
            metadata={"resource": permission.resource, "action": permission.action},
        )
        return permission

    def update_permission(
        self, permission_id: int, payload: PermissionUpdate, *, actor_id: Optional[int] = None
    ) -> Permission:
        permission = self.get_permission(permission_id)
        
        updated_fields = {}
        if payload.name is not None and payload.name != permission.name:
            # Check for name conflict
            conflict = self.db.query(Permission).filter(
                Permission.name == payload.name,
                Permission.id != permission_id
            ).first()
            if conflict:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Permission with this name already exists"
                )
            permission.name = payload.name
            updated_fields["name"] = payload.name

        if payload.resource is not None:
            permission.resource = payload.resource
            updated_fields["resource"] = payload.resource

        if payload.action is not None:
            permission.action = payload.action
            updated_fields["action"] = payload.action

        if payload.description is not None:
            permission.description = payload.description
            updated_fields["description"] = payload.description

        if payload.is_active is not None:
            permission.is_active = payload.is_active
            updated_fields["is_active"] = payload.is_active

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permission update failed due to conflict"
            )
        self.db.refresh(permission)

        record_event(
            action="permission.update",
            actor_id=str(actor_id) if actor_id else None,
            target_id=str(permission.id),
            target_type="permission",
            description=f"Updated permission {permission.name}",
            metadata=updated_fields,
        )
        return permission

    def delete_permission(self, permission_id: int, *, actor_id: Optional[int] = None) -> None:
        permission = self.get_permission(permission_id)
        
        # Check if permission is assigned to any roles
        role_count = self.db.query(self.db.query(Permission).filter(Permission.id == permission_id).join(
            Permission.roles
        ).count()).scalar()
        
        if role_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission is assigned to {role_count} role(s). Remove it from roles before deleting."
            )

        permission_name = permission.name
        self.db.delete(permission)
        self.db.commit()

        record_event(
            action="permission.delete",
            actor_id=str(actor_id) if actor_id else None,
            target_id=str(permission_id),
            target_type="permission",
            description=f"Deleted permission {permission_name}",
        )

    def get_service(self, service_id: int) -> Service:
        service = self.db.query(Service).filter(Service.id == service_id).first()
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
        return service

    def create_service(self, payload: ServiceCreate, *, actor_id: Optional[int] = None) -> Service:
        service = Service(
            name=payload.name,
            key=payload.key,
            description=payload.description,
            is_active=payload.is_active,
        )
        self.db.add(service)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Service name or key already exists")
        self.db.refresh(service)

        record_event(
            action="service.create",
            actor_id=str(actor_id) if actor_id else None,
            target_id=str(service.id),
            target_type="service",
            description=f"Created service {service.key}",
        )
        return service

    def update_service(self, service_id: int, payload: ServiceUpdate, *, actor_id: Optional[int] = None) -> Service:
        service = self.get_service(service_id)
        if payload.name is not None:
            service.name = payload.name
        if payload.key is not None:
            service.key = payload.key
        if payload.description is not None:
            service.description = payload.description
        if payload.is_active is not None:
            service.is_active = payload.is_active

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Service name or key already exists")
        self.db.refresh(service)

        record_event(
            action="service.update",
            actor_id=str(actor_id) if actor_id else None,
            target_id=str(service.id),
            target_type="service",
            description=f"Updated service {service.key}",
            metadata=payload.model_dump(exclude_none=True),
        )
        return service

    def delete_service(self, service_id: int, *, actor_id: Optional[int] = None) -> None:
        service = self.get_service(service_id)
        linked = self.db.query(RoleServiceAccess).filter(RoleServiceAccess.service_id == service_id).first()
        if linked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service is assigned to roles; detach before deleting",
            )
        self.db.delete(service)
        self.db.commit()
        record_event(
            action="service.delete",
            actor_id=str(actor_id) if actor_id else None,
            target_id=str(service_id),
            target_type="service",
            description="Deleted service",
        )

    # ------------------------------------------------------------------
    # Helper utilities
    # ------------------------------------------------------------------
    def _fetch_permissions_or_404(self, permission_ids: Iterable[int]) -> Iterable[Permission]:
        ids = list(permission_ids)
        if not ids:
            return []

        permissions = (
            self.db.query(Permission)
            .filter(Permission.id.in_(ids), Permission.is_active == True)
            .all()
        )
        found_ids = {perm.id for perm in permissions}
        missing = [pid for pid in ids if pid not in found_ids]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permissions not found or inactive: {', '.join(map(str, missing))}",
            )
        return permissions

