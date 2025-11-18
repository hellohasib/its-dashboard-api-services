# ATMS - Automated Traffic Management System

Complete Integrated Traffic System with microservices backend (Python/FastAPI) and modern React frontend.

## Architecture

### Backend Services
- **Auth Service**: Authentication and Authorization (Port: 8001)
- **ANPR Service**: License Plate Recognition data handling (Port: 8002)
- **Shared Core**: Common utilities, database connections, base classes

### Frontend
- **React App**: Modern TypeScript/React web interface (integrated with Auth Service)
- Built with Vite, Tailwind CSS, and React Router
- Served by FastAPI on port 8001 (unified container)

### Infrastructure
- **MySQL 8.0**: Primary database
- **Redis**: Caching and session management
- **Loki**: Log aggregation
- **OpenTelemetry Collector**: Observability

## Quick Start

### Prerequisites
- Docker and Docker Compose
- (Optional) Node.js 20+ for local frontend development
- (Optional) Python 3.11+ for local backend development

### Production Deployment

1. **Clone and configure**:
   ```bash
   git clone <repository>
   cd traffic-system-backend
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d --build
   ```

3. **Access the application**:
   - **Frontend & Auth API**: http://localhost:8001 (Unified Container)
   - Auth API Docs: http://localhost:8001/docs
   - ANPR API: http://localhost:8002
   - ANPR API Docs: http://localhost:8002/docs
   - Loki: http://localhost:3100

> **Note**: The frontend and auth-service are now served from the same container on port 8001.

### Development Mode

For development with hot reload:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This enables:
- Frontend hot reload on code changes (Port: 5173)
- Backend auto-reload for both services
- Volume mounts for live code updates

## Project Structure

```
ITS-Dashboard/
├── traffic-system-backend/   # Backend services + Docker config
│   ├── services/
│   │   ├── auth-service/     # Authentication microservice (serves frontend)
│   │   ├── anpr-service/     # ANPR microservice
│   │   └── shared/           # Shared utilities & middleware
│   ├── docker/               # Docker configuration files
│   ├── docker-compose.yml    # Production orchestration (context: ..)
│   ├── docker-compose.dev.yml # Development overrides
│   └── README.md
│
└── traffic-system-frontend-figma/  # React frontend (external)
    ├── src/
    │   ├── components/       # Reusable UI components
    │   ├── pages/            # Page components
    │   ├── layouts/          # Layout components
    │   └── App.tsx           # Main app component
    └── package.json
```

> **Note**: The frontend code lives in `../traffic-system-frontend-figma/` and is referenced during Docker build. See [EXTERNAL_FRONTEND.md](./EXTERNAL_FRONTEND.md) for details.

## Services Overview

### Auth Service (Port 8001)
- JWT-based authentication
- Role-based access control (RBAC)
- User and permission management
- Service-to-service authentication

**API Documentation**: http://localhost:8001/docs

### ANPR Service (Port 8002)
- License plate detection data
- Camera resource management
- Event tracking
- Traffic statistics

**API Documentation**: http://localhost:8002/docs

### Frontend (Unified with Auth Service - Port 8001)
- Dashboard with real-time statistics
- Resource management interface
- Road event tracking
- User management
- Traffic analytics
- Served by FastAPI alongside authentication APIs

## Environment Variables

Key environment variables (see `.env.example` for full list):

```env
# Database
DB_NAME=its_dashboard
DB_USER=app_user
DB_PASS=app_password

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# Application
APP_ENV=development
DEBUG=True
```

## Docker Commands

### Production
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f frontend
docker-compose logs -f auth-service

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Development
```bash
# Start with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Rebuild specific service
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build frontend

# Stop dev environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
```

### Maintenance
```bash
# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Check service health
docker-compose ps

# Execute commands in containers
docker-compose exec auth-service bash
docker-compose exec frontend sh
```

## Local Development (Without Docker)

### Backend Services
```bash
# Auth Service
cd services/auth-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# ANPR Service
cd services/anpr-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

### Frontend
```bash
# Frontend is in external directory
cd ../traffic-system-frontend-figma
npm install
npm run dev  # Starts on port 5173
```

## Database Migrations

Migrations are handled via Alembic in each service:

```bash
# Auto-run on container start, or manually:
docker-compose exec auth-service alembic upgrade head
docker-compose exec anpr-service alembic upgrade head
```

## Health Checks

All services include health checks:

```bash
# Auth Service (includes frontend)
curl http://localhost:8001/health

# ANPR Service
curl http://localhost:8002/health
```

## Troubleshooting

### Port Conflicts
If ports are already in use, modify the port mappings in `docker-compose.yml`:
```yaml
ports:
  - "3001:80"  # Change 3000 to 3001
```

### Database Connection Issues
1. Check MySQL is healthy: `docker-compose ps`
2. View logs: `docker-compose logs mysql`
3. Verify environment variables in `.env`

### Frontend Not Loading
1. Check build logs: `docker-compose logs auth-service`
2. Verify frontend was built: `docker-compose exec auth-service ls -la /app/frontend/dist`
3. Rebuild: `docker-compose up -d --build auth-service`

## API Integration

The frontend is served from the same container as the auth-service:
- **Frontend**: `http://localhost:8001/` (served by FastAPI)
- **Auth API**: `http://localhost:8001/api/v1/*` (same container)
- **ANPR API**: `http://localhost:8002/api/v1/*` (separate container)

> **Note**: The frontend and auth APIs are now unified in one container, eliminating CORS issues for authentication endpoints.

## Documentation

- [Quick Start Guide](./QUICKSTART.md) - Get started in 5 minutes
- [Unified Container Architecture](./UNIFIED_CONTAINER.md) - How frontend + backend integration works
- [External Frontend Setup](./EXTERNAL_FRONTEND.md) - Frontend directory structure explained
- [Environment Variables](./ENVIRONMENT_VARIABLES.md) - All configuration options
- [Build Instructions](./BUILD_INSTRUCTIONS.md) - How to build the system
- [Database Setup](./DATABASE_SETUP.md) - Database configuration
- [Docker Setup](./DOCKER_SETUP.md) - Docker details
- [Authentication](./services/auth-service/AUTHENTICATION_IMPLEMENTATION.md) - Auth implementation
- [ANPR Service](./services/anpr-service/README.md) - ANPR service docs
- [Frontend Documentation](../traffic-system-frontend-figma/README.md) - Frontend details

## License

MIT

