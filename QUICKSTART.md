# ATMS Quick Start Guide

Get your Automated Traffic Management System up and running in 5 minutes.

## Prerequisites

- Docker Desktop installed and running
- 8GB RAM minimum (16GB recommended)
- Ports available: 8001, 8002, 3307, 6379, 3100

## Step 1: Clone and Navigate

```bash
cd traffic-system-backend
```

## Step 2: Environment Setup

Create your environment file:

```bash
# Copy the example environment file
cat > .env << 'EOF'
# Database Configuration
DB_HOST=mysql
DB_PORT=3306
DB_NAME=its_dashboard
DB_USER=app_user
DB_PASS=app_password
DB_ROOT_PASSWORD=rootpassword

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# JWT Configuration
SECRET_KEY=dev-secret-key-change-in-production-12345678
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=525600
REFRESH_TOKEN_EXPIRE_DAYS=365

# Application Configuration
APP_ENV=development
DEBUG=True

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_DESTINATION=console

# Observability
OTLP_ENDPOINT=http://otel-collector:4317
LOKI_ENDPOINT=http://loki:3100
LOKI_TIMEOUT_SECONDS=5
LOKI_HTTP_PORT=3100
OTEL_COLLECTOR_GRPC_PORT=4317
OTEL_COLLECTOR_HTTP_PORT=4318

# Frontend API URLs
VITE_API_URL=http://localhost:8001
VITE_ANPR_API_URL=http://localhost:8002
EOF
```

## Step 3: Start the System

### Production Mode (Recommended for First Run)

```bash
# Start all services
docker-compose up -d

# Watch the logs
docker-compose logs -f
```

Wait for all services to be healthy (about 2-3 minutes on first run).

### Development Mode (With Hot Reload)

```bash
# Start with development overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Step 4: Verify Services

Check all services are running:

```bash
docker-compose ps
```

You should see:
- ✓ traffic-auth-service (healthy) - **Includes Frontend**
- ✓ traffic-anpr-service (running)
- ✓ traffic-mysql (healthy)
- ✓ traffic-redis (healthy)
- ✓ traffic-loki (running)
- ✓ traffic-otel-collector (running)

## Step 5: Access the Application

Open your browser and navigate to:

### 🌐 Application (Frontend + Auth API)
**http://localhost:8001**

> **Note**: Frontend and Auth Service are now unified in one container!

### 📚 API Documentation

- **Auth Service API**: http://localhost:8001/docs
- **ANPR Service API**: http://localhost:8002/docs

### 📊 Monitoring

- **Loki Logs**: http://localhost:3100/ready

## Step 6: Initialize Database (First Time Only)

The database is automatically initialized with tables on first startup. To verify:

```bash
# Check auth service logs for migration
docker-compose logs auth-service | grep -i "alembic"

# Check ANPR service logs for migration
docker-compose logs anpr-service | grep -i "alembic"
```

## Step 7: Seed Initial Data (Optional)

```bash
# Run auth service seeder
docker-compose exec auth-service python scripts/seed_data.py
```

This creates:
- Default admin user: `admin@atms.com` / `admin123`
- Sample roles and permissions

## Quick Commands Reference

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f auth-service
docker-compose logs -f anpr-service
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart frontend
```

### Stop Everything
```bash
docker-compose down
```

### Rebuild After Code Changes
```bash
# Rebuild all
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build frontend
```

### Database Access
```bash
# MySQL CLI
docker-compose exec mysql mysql -u app_user -papp_password its_dashboard

# Redis CLI
docker-compose exec redis redis-cli
```

## Health Check Endpoints

```bash
# Auth Service (includes frontend)
curl http://localhost:8001/health

# ANPR Service  
curl http://localhost:8002/health

# MySQL
docker-compose exec mysql mysqladmin ping -h localhost

# Redis
docker-compose exec redis redis-cli ping
```

## Troubleshooting

### "Port is already in use"

Change the port mapping in `docker-compose.yml`:
```yaml
frontend:
  ports:
    - "3001:80"  # Changed from 3000 to 3001
```

### "Container exited with code 1"

Check the logs:
```bash
docker-compose logs <service-name>
```

Common issues:
- Database not ready: Wait 30 seconds and restart
- Port conflicts: Change ports in docker-compose.yml
- Environment variables: Verify .env file exists and is correct

### Frontend Shows Blank Page

1. Check if frontend was built successfully:
```bash
docker-compose logs auth-service | grep -i "frontend\|vite\|build"
```

2. Verify frontend files exist:
```bash
docker-compose exec auth-service ls -la /app/frontend/dist
```

3. Rebuild auth-service (includes frontend):
```bash
docker-compose up -d --build auth-service
```

### Database Connection Errors

1. Check MySQL is healthy:
```bash
docker-compose ps mysql
```

2. Test connection:
```bash
docker-compose exec mysql mysql -u app_user -papp_password its_dashboard -e "SELECT 1"
```

3. Restart services:
```bash
docker-compose restart auth-service anpr-service
```

## Development Workflow

### Backend Development (with Hot Reload)
```bash
# Start all services with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Edit code in services/auth-service or services/anpr-service
# Changes will auto-reload
```

### Frontend Development (Local)
```bash
# For faster frontend development, run locally:
cd frontend
npm install
npm run dev  # Starts on http://localhost:5173

# Configure to use Docker backend:
# Edit frontend/.env.development:
# VITE_API_URL=http://localhost:8001/api/v1
# VITE_ANPR_API_URL=http://localhost:8002/api/v1
```

### Full Stack Development
```bash
# Option 1: Everything in Docker (slower builds)
docker-compose up -d --build

# Option 2: Frontend local + Backend in Docker (faster iteration)
docker-compose up -d auth-service anpr-service mysql redis
cd frontend && npm run dev
```

### Database Migrations

When you modify models:

```bash
# Create migration
docker-compose exec auth-service alembic revision --autogenerate -m "description"

# Apply migration
docker-compose exec auth-service alembic upgrade head
```

## Next Steps

1. **Explore the Frontend**
   - Navigate through the dashboard
   - Check resource management
   - View traffic statistics

2. **Test the APIs**
   - Open http://localhost:8001/docs
   - Try authentication endpoints
   - Test ANPR endpoints

3. **Configure for Production**
   - Update SECRET_KEY
   - Set APP_ENV=production
   - Configure proper passwords
   - Set up SSL/TLS
   - Configure backup strategy

4. **Read Full Documentation**
   - [README.md](./README.md) - Complete system documentation
   - [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md) - All configuration options
   - [DOCKER_SETUP.md](./DOCKER_SETUP.md) - Advanced Docker configuration

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│         Auth Service (Unified Container)            │
│                  Port: 8001                         │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │  Frontend (React) - Served by FastAPI       │  │
│  │  • Dashboard, Resources, Maps, etc.         │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │  Auth API - /api/v1/*                       │  │
│  │  • Login, Users, Roles, Permissions         │  │
│  └─────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │
                       ├──────────────┐
                       │              │
                       ▼              ▼
          ┌─────────────────┐  ┌────────────────┐
          │  ANPR Service   │  │ MySQL + Redis  │
          │   Port: 8002    │  │ Loki + OTel    │
          └─────────────────┘  └────────────────┘
```

**Key Changes:**
- ✅ Frontend + Auth Service unified (Port 8001)
- ✅ No separate Nginx container
- ✅ FastAPI serves both UI and API
- ✅ Simpler architecture, fewer containers

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Review [README.md](./README.md)
3. Check [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md)
4. Review Docker documentation

---

**Ready to go!** Your ATMS system should now be running at http://localhost:3000 🚀

