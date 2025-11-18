# Auth Service

This service exposes authentication, authorization, and role-management APIs.

## API Overview

The OpenAPI docs are available at `http://localhost:8001/docs` when `DEBUG=true`.

### Role Management

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET` | `/api/v1/roles/` | List roles with permissions and service access |
| `POST` | `/api/v1/roles/` | Create a new role (permissions + service access optional) |
| `GET` | `/api/v1/roles/{role_id}` | Retrieve role detail |
| `PUT` | `/api/v1/roles/{role_id}` | Update role metadata, permissions, or service access |
| `DELETE` | `/api/v1/roles/{role_id}` | Delete a non-system role |
| `PATCH` | `/api/v1/roles/{role_id}/services/{service_id}` | Update the access level for a role/service mapping |
| `GET` | `/api/v1/roles/permissions` | List available permissions |

### Service Catalogue

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET` | `/api/v1/services/` | List services (with optional inactive records) |
| `POST` | `/api/v1/services/` | Create a new logical service |
| `GET` | `/api/v1/services/{service_id}` | Retrieve a service definition |
| `PUT` | `/api/v1/services/{service_id}` | Update name/key/description/status |
| `DELETE` | `/api/v1/services/{service_id}` | Delete an unused service |

All endpoints require a super-admin access token (use the `super_admin` role or `is_superuser` flag).

## CLI Utilities

The CLI lives in `scripts/seed_data.py` and now exposes multiple sub-commands:

```bash
cd services/auth-service
python scripts/seed_data.py --help
```

Common commands:

- `python scripts/seed_data.py seed --with-admin --with-services` – Seed permissions, system roles, optional admin user, and default services.
- `python scripts/seed_data.py list-services` – View registered services.
- `python scripts/seed_data.py create-service --name "Analytics" --key analytics` – Add a service entry.
- `python scripts/seed_data.py create-role --name operator --permissions anpr:read anpr:write --service-access anpr:manage` – Create a role with permissions and service access.
- `python scripts/seed_data.py assign-service <role_id> <service_id> --access-level manage` – Adjust service access for an existing role.

> **Note:** The CLI expects the Python dependencies (e.g., SQLAlchemy) to be installed and the database connection environment variables to be configured.

## Migrations

A new Alembic migration (`c9d2a88e8f7a_add_service_access_models`) creates:

- `services` – logical service catalogue.
- `role_service_accesses` – many-to-many mapping between roles and services with accessor metadata.

Run the migrations before using the new APIs/CLI:

```bash
cd services/auth-service
alembic upgrade head
```
