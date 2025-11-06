# Database Migration Guide

## Step 1: Create Initial Migration

Navigate to the auth-service directory and create the initial migration:

```bash
cd services/auth-service
alembic revision --autogenerate -m "Initial auth service schema"
```

This will create a migration file in `alembic/versions/` with all the tables:
- users
- roles
- permissions
- refresh_tokens
- user_roles (association table)
- role_permissions (association table)

## Step 2: Review Migration

Before applying, review the generated migration file to ensure it's correct:
- Check that all tables are created
- Verify foreign key constraints
- Ensure indexes are created

## Step 3: Apply Migration

Run the migration to create tables:

```bash
alembic upgrade head
```

Or if using Docker:
```bash
docker-compose exec auth-service alembic upgrade head
```

## Step 4: Seed Initial Data

After migrations, seed the database with initial roles and permissions:

```bash
# From auth-service directory
python scripts/seed_data.py
```

Or using Docker:
```bash
docker-compose exec auth-service python scripts/seed_data.py
```

This will create:
- Default permissions (anpr:read, anpr:write, camera:read, etc.)
- Default roles (super_admin, admin, operator, viewer)
- Default admin user (admin@traffic-system.local / admin123)

⚠️ **IMPORTANT**: Change the default admin password in production!

## Step 5: Verify

Check that tables were created:

```sql
USE its_dashboard;
SHOW TABLES;
```

You should see:
- users
- roles
- permissions
- refresh_tokens
- user_roles
- role_permissions

## Common Commands

### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback one migration
```bash
alembic downgrade -1
```

### See migration history
```bash
alembic history
```

### See current revision
```bash
alembic current
```

## Troubleshooting

### Migration fails with "Table already exists"
- Check if tables were created manually
- Use `alembic stamp head` to mark current state

### Import errors in migration
- Ensure all models are imported in `alembic/env.py`
- Check Python path is correct

### Database connection errors
- Verify database credentials in `.env`
- Check database is running and accessible
- For Docker: ensure containers are on same network

