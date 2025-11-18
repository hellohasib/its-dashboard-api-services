# ATMS Changelog

## [2.0.0] - 2024-11-18 - Unified Container Architecture

### 🎯 Major Changes

#### Frontend Integration into Auth Service
- **BREAKING CHANGE**: Frontend is now served from auth-service container instead of separate container
- Reduced from 7 containers to 6 containers (removed standalone frontend)
- Single port (8001) now serves both frontend UI and authentication APIs

### ✨ New Features

#### Unified Container
- Multi-stage Docker build combining Node.js (frontend build) and Python (backend runtime)
- FastAPI now serves both React static files and API endpoints
- Eliminated CORS issues between frontend and auth API (same origin)
- Simplified deployment with fewer moving parts

#### Improved Documentation
- Added `UNIFIED_CONTAINER.md` - Detailed architecture explanation
- Added `BUILD_INSTRUCTIONS.md` - Comprehensive build guide
- Updated `README.md` - Reflects new architecture
- Updated `QUICKSTART.md` - Updated for single-port access
- Updated `start.sh` - Reflects new port configuration

### 🔧 Technical Changes

#### Docker Configuration
- **docker-compose.yml**:
  - Removed separate `frontend` service
  - Updated `auth-service` to include frontend build
  - Updated health checks
  - Simplified port mappings

- **docker-compose.dev.yml**:
  - Removed frontend development service
  - Backend hot reload remains functional
  - For frontend dev, run locally outside Docker

#### Auth Service Dockerfile
```dockerfile
# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/ ./
RUN npm ci && npm run build

# Stage 2: Backend + Built Frontend  
FROM python:3.11-slim
# ... setup ...
COPY --from=frontend-builder /frontend/dist /app/frontend/dist
```

#### FastAPI Main App (auth-service)
```python
# Mount static assets
app.mount("/assets", StaticFiles(directory="/app/frontend/dist/assets"))

# API routes at /api/v1/*
app.include_router(auth.router, prefix="/api/v1")

# Catch-all for SPA routing
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Serve static files or index.html
```

### 📊 Service Changes

| Service | Before | After |
|---------|--------|-------|
| **Frontend** | Port 3000 (Nginx) | Port 8001 (FastAPI + Auth) |
| **Auth API** | Port 8001 | Port 8001 (unified) |
| **ANPR API** | Port 8002 | Port 8002 (unchanged) |
| **Total Containers** | 7 | 6 |

### 🚀 Access Points

#### Before
- Frontend: `http://localhost:3000`
- Auth API: `http://localhost:8001`
- ANPR API: `http://localhost:8002`

#### After
- **Application** (Frontend + Auth API): `http://localhost:8001`
- ANPR API: `http://localhost:8002`

### API Routes

- `/` - React frontend (served by FastAPI)
- `/api/v1/*` - Authentication APIs
- `/docs` - Swagger API documentation
- `/health` - Health check endpoint
- `/assets/*` - Static files (JS, CSS, images)

### 📦 What Was Removed

- ❌ Separate frontend Docker container
- ❌ Nginx configuration for frontend
- ❌ Separate frontend service in docker-compose
- ❌ Port 3000 (no longer needed)
- ❌ Complex CORS configuration between frontend and auth

### ✅ What Was Added

- ✅ Multi-stage Dockerfile for auth-service
- ✅ FastAPI static file serving
- ✅ SPA routing support in FastAPI
- ✅ Unified container architecture
- ✅ BUILD_INSTRUCTIONS.md
- ✅ UNIFIED_CONTAINER.md
- ✅ Updated all documentation

### 🎁 Benefits

1. **Simpler Architecture**
   - One less container to manage
   - Fewer port mappings
   - Simpler networking

2. **Better Performance**
   - No network hop between frontend and auth API
   - Faster auth API calls (same process)
   - Reduced latency

3. **Easier CORS**
   - Same origin eliminates CORS for auth endpoints
   - Simpler configuration
   - Better security

4. **Smaller Footprint**
   - No separate Nginx container
   - Reduced memory usage (~200MB saved)
   - Fewer Docker images to pull

5. **Unified Deployment**
   - Single service to rebuild for frontend changes
   - Consistent versioning
   - Easier rollbacks

### ⚠️ Breaking Changes

#### Port Changes
- **Old**: Frontend on port 3000, Auth on port 8001
- **New**: Both on port 8001

#### API Paths (No Change)
- APIs still at `/api/v1/*`
- Swagger docs still at `/docs`
- Health check still at `/health`

#### Environment Variables
- `VITE_API_URL` should now use relative paths: `/api/v1`
- No longer need separate `FRONTEND_PORT` variable

### 🔄 Migration Steps

If updating from previous version:

```bash
# 1. Stop old containers
docker-compose down

# 2. Pull latest code
git pull

# 3. Rebuild auth-service (includes frontend now)
docker-compose build --no-cache auth-service

# 4. Start services
docker-compose up -d

# 5. Access on new port
open http://localhost:8001
```

### 📝 Developer Notes

#### Local Development

**Option 1: Everything in Docker**
```bash
docker-compose up -d --build
# Frontend rebuild requires auth-service rebuild
```

**Option 2: Frontend Local, Backend Docker (Faster)**
```bash
# Start backend services
docker-compose up -d auth-service anpr-service mysql redis

# Run frontend locally with hot reload
cd frontend
npm install
npm run dev  # http://localhost:5173
```

#### Build Time
- First build: 5-10 minutes (downloads all dependencies)
- Subsequent builds: 2-5 minutes (Docker layer caching)
- Frontend-only changes: ~2 minutes
- Backend-only changes: ~1 minute

### 🐛 Known Issues

None at this time.

### 🔮 Future Enhancements

#### Potential Options

1. **Full Unification** (Future)
   - Consolidate ANPR service into auth-service too
   - Single container for all APIs
   - Simplest deployment possible

2. **API Gateway Pattern** (Future)
   - Add dedicated Nginx/Traefik gateway
   - Route `/api/auth/*` → auth-service
   - Route `/api/anpr/*` → anpr-service
   - Most scalable for future growth

3. **Keep Current** (Recommended)
   - Auth + Frontend unified ✅
   - ANPR separate (allows independent scaling)
   - Good balance

### 📚 Documentation

All documentation has been updated:
- ✅ README.md
- ✅ QUICKSTART.md
- ✅ UNIFIED_CONTAINER.md (new)
- ✅ BUILD_INSTRUCTIONS.md (new)
- ✅ ENVIRONMENT_VARIABLES.md
- ✅ INTEGRATION_SUMMARY.md
- ✅ start.sh
- ✅ stop.sh

### 🎉 Summary

The ATMS system now features a **unified container architecture** where the React frontend and FastAPI auth service are combined into a single container. This simplifies deployment, improves performance, and reduces complexity while maintaining all functionality.

**Key Takeaway**: Access everything on `http://localhost:8001` 🚀

---

## [1.0.0] - 2024-11-17 - Initial Integration

### Initial Features
- Separate frontend container (Nginx)
- Auth service (FastAPI)
- ANPR service (FastAPI)
- MySQL database
- Redis cache
- Loki logging
- OpenTelemetry collector

### Architecture
- 7 separate Docker containers
- Frontend on port 3000
- Auth API on port 8001
- ANPR API on port 8002

