"""
Seed initial data for auth service
Run this after migrations to populate initial roles and permissions
"""
import sys
import os

# Add parent directories to path to find services module
current_dir = os.path.dirname(os.path.abspath(__file__))
auth_service_dir = os.path.dirname(current_dir)
services_dir = os.path.dirname(auth_service_dir)
root_dir = os.path.dirname(services_dir)

# Add to Python path (root directory must be first for services.shared to work)
sys.path.insert(0, root_dir)
sys.path.insert(0, services_dir)
sys.path.insert(0, auth_service_dir)

from services.shared.database.session import SessionLocal
from app.models.role import Role
from app.models.permission import Permission
from app.models.user import User
from app.models.role_permission import RolePermission
from app.utils.security import get_password_hash
from services.shared.utils.logger import setup_logger

logger = setup_logger(__name__)


def seed_permissions(db):
    """Seed default permissions"""
    permissions_data = [
        # ANPR permissions
        {"name": "anpr:read", "resource": "anpr", "action": "read", "description": "Read ANPR detections"},
        {"name": "anpr:write", "resource": "anpr", "action": "write", "description": "Create/Update ANPR detections"},
        {"name": "anpr:delete", "resource": "anpr", "action": "delete", "description": "Delete ANPR detections"},
        {"name": "anpr:manage", "resource": "anpr", "action": "manage", "description": "Full ANPR management"},
        
        # Camera permissions
        {"name": "camera:read", "resource": "camera", "action": "read", "description": "View cameras"},
        {"name": "camera:write", "resource": "camera", "action": "write", "description": "Manage cameras"},
        {"name": "camera:delete", "resource": "camera", "action": "delete", "description": "Delete cameras"},
        
        # User management permissions
        {"name": "user:read", "resource": "user", "action": "read", "description": "View users"},
        {"name": "user:write", "resource": "user", "action": "write", "description": "Create/Update users"},
        {"name": "user:delete", "resource": "user", "action": "delete", "description": "Delete users"},
        {"name": "user:manage", "resource": "user", "action": "manage", "description": "Full user management"},
        
        # Role management permissions
        {"name": "role:read", "resource": "role", "action": "read", "description": "View roles"},
        {"name": "role:write", "resource": "role", "action": "write", "description": "Manage roles"},
        {"name": "role:delete", "resource": "role", "action": "delete", "description": "Delete roles"},
        
        # Reports permissions
        {"name": "report:read", "resource": "report", "action": "read", "description": "View reports"},
        {"name": "report:generate", "resource": "report", "action": "generate", "description": "Generate reports"},
        
        # System permissions
        {"name": "system:admin", "resource": "system", "action": "admin", "description": "System administration"},
    ]
    
    created_count = 0
    for perm_data in permissions_data:
        existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
            created_count += 1
            logger.info(f"Created permission: {perm_data['name']}")
    
    db.commit()
    logger.info(f"Created {created_count} permissions")
    return created_count


def seed_roles(db):
    """Seed default roles with permissions"""
    # Get all permissions
    all_perms = db.query(Permission).all()
    perm_map = {perm.name: perm for perm in all_perms}
    
    roles_data = [
        {
            "name": "super_admin",
            "description": "Super Administrator - Full system access",
            "is_system": True,
            "permissions": [p for p in perm_map.keys()]  # All permissions
        },
        {
            "name": "admin",
            "description": "Administrator - Manage users and configurations",
            "is_system": True,
            "permissions": [
                "user:read", "user:write", "user:manage",
                "role:read", "role:write",
                "camera:read", "camera:write", "camera:delete",
                "anpr:read", "anpr:write", "anpr:manage",
                "report:read", "report:generate",
            ]
        },
        {
            "name": "operator",
            "description": "Operator - Manage ANPR data and view reports",
            "is_system": True,
            "permissions": [
                "anpr:read", "anpr:write",
                "camera:read",
                "report:read", "report:generate",
            ]
        },
        {
            "name": "viewer",
            "description": "Viewer - Read-only access",
            "is_system": True,
            "permissions": [
                "anpr:read",
                "camera:read",
                "report:read",
            ]
        },
    ]
    
    created_count = 0
    for role_data in roles_data:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if existing:
            role = existing
            logger.info(f"Role {role_data['name']} already exists, updating permissions")
        else:
            role = Role(
                name=role_data["name"],
                description=role_data["description"],
                is_system=role_data["is_system"]
            )
            db.add(role)
            db.flush()  # Get role ID
            created_count += 1
            logger.info(f"Created role: {role_data['name']}")
        
        # Assign permissions
        role.permissions.clear()
        for perm_name in role_data["permissions"]:
            if perm_name in perm_map:
                role.permissions.append(perm_map[perm_name])
        
        db.flush()
    
    db.commit()
    logger.info(f"Created/updated {created_count} roles")
    return created_count


def seed_admin_user(db):
    """Seed default admin user"""
    # Get super_admin role
    super_admin_role = db.query(Role).filter(Role.name == "super_admin").first()
    if not super_admin_role:
        logger.error("Super admin role not found. Please run seed_roles first.")
        return None
    
    # Check if admin user exists
    admin_user = db.query(User).filter(User.email == "admin@traffic-system.local").first()
    if admin_user:
        logger.info("Admin user already exists")
        return admin_user
    
    # Create admin user
    admin_user = User(
        email="admin@traffic-system.local",
        username="admin",
        hashed_password=get_password_hash("admin123"),  # Change this in production!
        full_name="System Administrator",
        is_active=True,
        is_verified=True,
        is_superuser=True,
    )
    db.add(admin_user)
    db.flush()
    
    # Assign super_admin role
    admin_user.roles.append(super_admin_role)
    db.commit()
    
    logger.info("Created admin user: admin@traffic-system.local / admin123")
    logger.warning("⚠️  IMPORTANT: Change the default admin password in production!")
    return admin_user


def main():
    """Main seeding function"""
    db = SessionLocal()
    try:
        logger.info("Starting database seeding...")
        
        # Seed permissions first
        seed_permissions(db)
        
        # Seed roles (depends on permissions)
        seed_roles(db)
        
        # Seed admin user (depends on roles)
        seed_admin_user(db)
        
        logger.info("Database seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

