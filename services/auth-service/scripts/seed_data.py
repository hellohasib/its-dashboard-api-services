"""
Auth service CLI utilities for seeding data and managing roles/services.
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable, List, Sequence, Optional

# Ensure shared packages are importable when the script is executed directly
current_dir = os.path.dirname(os.path.abspath(__file__))
auth_service_dir = os.path.dirname(current_dir)
services_dir = os.path.dirname(auth_service_dir)
root_dir = os.path.dirname(services_dir)

sys.path.insert(0, root_dir)
sys.path.insert(0, services_dir)
sys.path.insert(0, auth_service_dir)

from services.shared.database.session import SessionLocal
from services.shared.utils.logger import setup_logger

from app.models.permission import Permission
from app.models.role import Role
from app.models.service import Service
from app.models.user import User
from app.schemas.role import (
    RoleCreate,
    RoleServiceAccessCreate,
    RoleServiceAccessUpdate,
    RoleUpdate,
    ServiceCreate,
    ServiceUpdate,
)
from app.services import RoleManagementService
from app.utils.security import get_password_hash

logger = setup_logger(__name__)


# ---------------------------------------------------------------------------
# Seeding helpers (reused by CLI)
# ---------------------------------------------------------------------------

def seed_permissions(db) -> int:
    """Seed default permissions."""
    permissions_data = [
        {"name": "anpr:read", "resource": "anpr", "action": "read", "description": "Read ANPR detections"},
        {"name": "anpr:write", "resource": "anpr", "action": "write", "description": "Create/Update ANPR detections"},
        {"name": "anpr:delete", "resource": "anpr", "action": "delete", "description": "Delete ANPR detections"},
        {"name": "anpr:manage", "resource": "anpr", "action": "manage", "description": "Full ANPR management"},
        {"name": "camera:read", "resource": "camera", "action": "read", "description": "View cameras"},
        {"name": "camera:write", "resource": "camera", "action": "write", "description": "Manage cameras"},
        {"name": "camera:delete", "resource": "camera", "action": "delete", "description": "Delete cameras"},
        {"name": "user:read", "resource": "user", "action": "read", "description": "View users"},
        {"name": "user:write", "resource": "user", "action": "write", "description": "Create/Update users"},
        {"name": "user:delete", "resource": "user", "action": "delete", "description": "Delete users"},
        {"name": "user:manage", "resource": "user", "action": "manage", "description": "Full user management"},
        {"name": "role:read", "resource": "role", "action": "read", "description": "View roles"},
        {"name": "role:write", "resource": "role", "action": "write", "description": "Manage roles"},
        {"name": "role:delete", "resource": "role", "action": "delete", "description": "Delete roles"},
        {"name": "report:read", "resource": "report", "action": "read", "description": "View reports"},
        {"name": "report:generate", "resource": "report", "action": "generate", "description": "Generate reports"},
        {"name": "system:admin", "resource": "system", "action": "admin", "description": "System administration"},
    ]

    created_count = 0
    for perm_data in permissions_data:
        existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
            created_count += 1
            logger.info("Created permission: %s", perm_data["name"])

    db.commit()
    logger.info("Created %s permissions", created_count)
    return created_count


def seed_roles(db) -> int:
    """Seed default roles with permissions."""
    all_perms = db.query(Permission).all()
    perm_map = {perm.name: perm for perm in all_perms}

    roles_data = [
        {
            "name": "super_admin",
            "description": "Super Administrator - Full system access",
            "is_system": True,
            "permissions": list(perm_map.keys()),
        },
        {
            "name": "admin",
            "description": "Administrator - Manage users and configurations",
            "is_system": True,
            "permissions": [
                "user:read",
                "user:write",
                "user:manage",
                "role:read",
                "role:write",
                "camera:read",
                "camera:write",
                "camera:delete",
                "anpr:read",
                "anpr:write",
                "anpr:manage",
                "report:read",
                "report:generate",
            ],
        },
        {
            "name": "operator",
            "description": "Operator - Manage ANPR data and view reports",
            "is_system": True,
            "permissions": [
                "anpr:read",
                "anpr:write",
                "camera:read",
                "report:read",
                "report:generate",
            ],
        },
        {
            "name": "viewer",
            "description": "Viewer - Read-only access",
            "is_system": True,
            "permissions": ["anpr:read", "camera:read", "report:read"],
        },
    ]

    created_count = 0
    for role_data in roles_data:
        role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not role:
            role = Role(
                name=role_data["name"],
                description=role_data["description"],
                is_system=role_data["is_system"],
            )
            db.add(role)
            db.flush()
            created_count += 1
            logger.info("Created role: %s", role_data["name"])
        else:
            logger.info("Role %s already exists, syncing permissions", role_data["name"])

        role.permissions.clear()
        for perm_name in role_data["permissions"]:
            perm = perm_map.get(perm_name)
            if perm:
                role.permissions.append(perm)

    db.commit()
    logger.info("Created/updated %s roles", created_count)
    return created_count


def seed_admin_user(db) -> User | None:
    """Seed default admin user."""
    super_admin_role = db.query(Role).filter(Role.name == "super_admin").first()
    if not super_admin_role:
        logger.error("Super admin role not found. Run seed_roles first.")
        return None

    admin_user = db.query(User).filter(User.email == "admin@traffic-system.local").first()
    if admin_user:
        logger.info("Admin user already exists")
        return admin_user

    admin_user = User(
        email="admin@traffic-system.local",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        full_name="System Administrator",
        is_active=True,
        is_verified=True,
        is_superuser=True,
    )
    db.add(admin_user)
    db.flush()
    admin_user.roles.append(super_admin_role)
    db.commit()

    logger.info("Created admin user: admin@traffic-system.local / admin123")
    logger.warning("IMPORTANT: Change the default admin password in production!")
    return admin_user


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _get_session():
    return SessionLocal()


def _resolve_permission_ids(db, identifiers: Sequence[str]) -> List[int]:
    ids: List[int] = []
    for identifier in identifiers:
        if identifier.isdigit():
            ids.append(int(identifier))
        else:
            perm = db.query(Permission).filter(Permission.name == identifier).first()
            if not perm:
                raise ValueError(f"Permission '{identifier}' not found")
            ids.append(perm.id)
    return ids


def _parse_service_access(db, entries: Sequence[str]) -> List[RoleServiceAccessCreate]:
    results: List[RoleServiceAccessCreate] = []
    for entry in entries:
        parts = entry.split(":")
        key = parts[0]
        access_level = parts[1] if len(parts) > 1 and parts[1] else None
        service = db.query(Service).filter(Service.key == key).first()
        if not service:
            raise ValueError(f"Service with key '{key}' not found")
        results.append(RoleServiceAccessCreate(service_id=service.id, access_level=access_level))
    return results


def cli_seed(args: argparse.Namespace) -> None:
    db = _get_session()
    try:
        seed_permissions(db)
        seed_roles(db)
        if args.with_admin:
            seed_admin_user(db)
        if args.with_services:
            ensure_default_services(db)
        logger.info("Seeding completed successfully")
    finally:
        db.close()


def cli_list_services(args: argparse.Namespace) -> None:
    db = _get_session()
    try:
        rms = RoleManagementService(db)
        services = rms.list_services(include_inactive=args.include_inactive)
        for svc in services:
            status_label = "active" if svc.is_active else "inactive"
            print(f"[{svc.id}] {svc.key} - {svc.name} ({status_label})")
    finally:
        db.close()


def cli_create_service(args: argparse.Namespace) -> None:
    db = _get_session()
    try:
        rms = RoleManagementService(db)
        payload = ServiceCreate(name=args.name, key=args.key, description=args.description, is_active=not args.inactive)
        svc = rms.create_service(payload, actor_id=None)
        print(f"Created service {svc.key} (id={svc.id})")
    finally:
        db.close()


def cli_update_service(args: argparse.Namespace) -> None:
    db = _get_session()
    try:
        rms = RoleManagementService(db)
        updates = ServiceUpdate(
            name=args.name,
            key=args.key,
            description=args.description,
            is_active=None if args.inactive is None else not args.inactive,
        )
        svc = rms.update_service(args.service_id, updates, actor_id=None)
        print(f"Updated service {svc.key} (id={svc.id})")
    finally:
        db.close()


def cli_delete_service(args: argparse.Namespace) -> None:
    db = _get_session()
    try:
        rms = RoleManagementService(db)
        rms.delete_service(args.service_id, actor_id=None)
        print(f"Deleted service id={args.service_id}")
    finally:
        db.close()


def cli_list_roles(args: argparse.Namespace) -> None:
    db = _get_session()
    try:
        rms = RoleManagementService(db)
        roles = rms.list_roles()
        for role in roles:
            perms = ", ".join(sorted({perm.full_name for perm in role.permissions}))
            services = ", ".join(f"{link.service.key}:{link.access_level or 'default'}" for link in role.service_access_links)
            status_label = "active" if role.is_active else "inactive"
            print(f"[{role.id}] {role.name} ({status_label})")
            if perms:
                print(f"  permissions: {perms}")
            if services:
                print(f"  services: {services}")
    finally:
        db.close()


def cli_create_role(args: argparse.Namespace) -> None:
    db = _get_session()
    try:
        rms = RoleManagementService(db)
        permission_ids = _resolve_permission_ids(db, args.permissions or [])
        service_access = _parse_service_access(db, args.service_access or [])
        payload = RoleCreate(
            name=args.name,
            description=args.description,
            is_active=not args.inactive,
            is_system=args.system,
            permission_ids=permission_ids or None,
            service_access=service_access or None,
        )
        role = rms.create_role(payload, actor_id=None)
        print(f"Created role {role.name} (id={role.id})")
    finally:
        db.close()


def cli_update_role(args: argparse.Namespace) -> None:
    db = _get_session()
    try:
        rms = RoleManagementService(db)
        permission_ids = None
        if args.permissions is not None:
            permission_ids = _resolve_permission_ids(db, args.permissions)
        service_access = None
        if args.service_access is not None:
            service_access = _parse_service_access(db, args.service_access)
        payload = RoleUpdate(
            name=args.name,
            description=args.description,
            is_active=None if args.inactive is None else not args.inactive,
            permission_ids=permission_ids,
            service_access=service_access,
        )
        role = rms.update_role(args.role_id, payload, actor_id=None)
        print(f"Updated role {role.name} (id={role.id})")
    finally:
        db.close()


def cli_delete_role(args: argparse.Namespace) -> None:
    db = _get_session()
    try:
        rms = RoleManagementService(db)
        rms.delete_role(args.role_id, actor_id=None)
        print(f"Deleted role id={args.role_id}")
    finally:
        db.close()


def cli_assign_service(args: argparse.Namespace) -> None:
    db = _get_session()
    try:
        rms = RoleManagementService(db)
        payload = RoleServiceAccessCreate(access_level=args.access_level, is_active=None if args.inactive is None else not args.inactive)
        link = rms.update_service_access(args.role_id, args.service_id, payload, actor_id=None)
        print(
            "Updated service access: role_id=%s service_id=%s access_level=%s is_active=%s",
            link.role_id,
            link.service_id,
            link.access_level,
            link.is_active,
        )
    finally:
        db.close()


def ensure_default_services(db) -> None:
    """Seed a default set of logical services if none exist."""
    defaults = [
        {"name": "ANPR Service", "key": "anpr", "description": "Automatic number plate recognition"},
        {"name": "Camera Service", "key": "camera", "description": "Camera management service"},
        {"name": "Reporting Service", "key": "reporting", "description": "Reporting and analytics"},
    ]
    for svc in defaults:
        existing = db.query(Service).filter(Service.key == svc["key"]).first()
        if not existing:
            db.add(Service(**svc, is_active=True))
            logger.info("Seeded service: %s", svc["key"])
    db.commit()


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Auth service administrative CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed_parser = subparsers.add_parser("seed", help="Seed default permissions, roles, and (optional) admin user")
    seed_parser.add_argument("--with-admin", action="store_true", help="Create default super admin account")
    seed_parser.add_argument("--with-services", action="store_true", help="Seed default logical services")
    seed_parser.set_defaults(func=cli_seed)

    list_services_parser = subparsers.add_parser("list-services", help="List registered services")
    list_services_parser.add_argument("--include-inactive", action="store_true")
    list_services_parser.set_defaults(func=cli_list_services)

    create_service_parser = subparsers.add_parser("create-service", help="Create a new service definition")
    create_service_parser.add_argument("--name", required=True)
    create_service_parser.add_argument("--key", required=True)
    create_service_parser.add_argument("--description")
    create_service_parser.add_argument("--inactive", action="store_true")
    create_service_parser.set_defaults(func=cli_create_service)

    update_service_parser = subparsers.add_parser("update-service", help="Update an existing service")
    update_service_parser.add_argument("service_id", type=int)
    update_service_parser.add_argument("--name")
    update_service_parser.add_argument("--key")
    update_service_parser.add_argument("--description")
    update_service_parser.add_argument("--inactive", action="store_true", default=None)
    update_service_parser.set_defaults(func=cli_update_service)

    delete_service_parser = subparsers.add_parser("delete-service", help="Delete a service")
    delete_service_parser.add_argument("service_id", type=int)
    delete_service_parser.set_defaults(func=cli_delete_service)

    list_roles_parser = subparsers.add_parser("list-roles", help="List roles and their assignments")
    list_roles_parser.set_defaults(func=cli_list_roles)

    create_role_parser = subparsers.add_parser("create-role", help="Create a new role")
    create_role_parser.add_argument("--name", required=True)
    create_role_parser.add_argument("--description")
    create_role_parser.add_argument("--inactive", action="store_true")
    create_role_parser.add_argument("--system", action="store_true", help="Mark as system role")
    create_role_parser.add_argument("--permissions", nargs="*", help="Permission names or IDs")
    create_role_parser.add_argument(
        "--service-access",
        nargs="*",
        help="Service access entries formatted as service_key[:access_level]",
    )
    create_role_parser.set_defaults(func=cli_create_role)

    update_role_parser = subparsers.add_parser("update-role", help="Update an existing role")
    update_role_parser.add_argument("role_id", type=int)
    update_role_parser.add_argument("--name")
    update_role_parser.add_argument("--description")
    update_role_parser.add_argument("--inactive", action="store_true", default=None)
    update_role_parser.add_argument("--permissions", nargs="*", help="Permission names or IDs (empty list clears)", default=None)
    update_role_parser.add_argument(
        "--service-access",
        nargs="*",
        help="Replace service access configuration using service_key[:access_level] entries",
        default=None,
    )
    update_role_parser.set_defaults(func=cli_update_role)

    delete_role_parser = subparsers.add_parser("delete-role", help="Delete a role")
    delete_role_parser.add_argument("role_id", type=int)
    delete_role_parser.set_defaults(func=cli_delete_role)

    assign_service_parser = subparsers.add_parser(
        "assign-service",
        help="Update service access for a role",
    )
    assign_service_parser.add_argument("role_id", type=int)
    assign_service_parser.add_argument("service_id", type=int)
    assign_service_parser.add_argument("--access-level")
    assign_service_parser.add_argument("--inactive", action="store_true", default=None)
    assign_service_parser.set_defaults(func=cli_assign_service)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = build_parser()
    if argv is None and len(sys.argv) == 1:
        argv = ["seed", "--with-admin", "--with-services"]
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except ValueError as exc:
        logger.error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()

