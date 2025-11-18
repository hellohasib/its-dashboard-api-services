# ATMS Unified Container Architecture

## Overview

The ATMS system has been consolidated into a **unified container architecture** where the React frontend and FastAPI backend are served from the same container. This simplifies deployment and reduces the number of moving parts.

## Architecture

### Previous Architecture (Separate Containers)
```
┌─────────────────┐
│  Frontend       │  Port 3000
│  (Nginx)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Auth Service   │  Port 8001
│  (FastAPI)      │
└─────────────────┘
```

### New Architecture (Unified Container)
```
┌─────────────────────────────────┐
│  Auth Service Container         │
│                                  │
│  ┌──────────────────────────┐  │
│  │  FastAPI Application     │  │  Port 8001
│  │  ├─ /api/v1/*  (APIs)    │  │
│  │  ├─ /docs      (Swagger) │  │
│  │  ├─ /health    (Health)  │  │
│  │  └─ /*         (Frontend)│  │
│  └──────────────────────────┘  │
│                                  │
│  Built Frontend (dist/)          │
│  ├─ index.html                  │
│  ├─ assets/                     │
│  └─ ...                         │
└─────────────────────────────────┘
```

## How It Works

### 1. Multi-Stage Docker Build

The `services/auth-service/Dockerfile` uses a multi-stage build:

```dockerfile
# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
# Frontend is in external directory ../traffic-system-frontend-figma
COPY traffic-system-frontend-figma/ ./
RUN npm ci && npm run build

# Stage 2: Backend + Built Frontend
FROM python:3.11-slim
# ... Python setup ...
COPY --from=frontend-builder /frontend/dist /app/frontend/dist
```

> **Note**: The frontend code is in `../traffic-system-frontend-figma/`. Docker build context is the parent directory. See [EXTERNAL_FRONTEND.md](./EXTERNAL_FRONTEND.md).

**Benefits:**
- Single image contains both frontend and backend
- No Node.js in final image (smaller size)
- Consistent deployment

### 2. FastAPI Serves Both API and Frontend

The `services/auth-service/app/main.py` has been modified to:

```python
# Mount static assets
app.mount("/assets", StaticFiles(directory="/app/frontend/dist/assets"))

# API routes at /api/v1/*
app.include_router(auth.router, prefix="/api/v1")

# Catch-all route for SPA (React Router)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Serve static files or index.html for SPA routing
```

**Route Priority:**
1. `/api/v1/*` → API endpoints
2. `/docs` → Swagger UI
3. `/health` → Health check
4. `/assets/*` → Static files (JS, CSS, images)
5. `/*` → React app (index.html for SPA routing)

### 3. Single Port for Everything

Everything is served on **port 8001**:
- Frontend UI: `http://localhost:8001/`
- Auth API: `http://localhost:8001/api/v1/auth/*`
- API Docs: `http://localhost:8001/docs`
- Health: `http://localhost:8001/health`

## Updated docker-compose.yml

```yaml
services:
  auth-service:
    build:
      context: .
      dockerfile: ./services/auth-service/Dockerfile
    ports:
      - "8001:8000"  # Frontend and API on same port
    # ... other config ...
    
  # Frontend service removed - now part of auth-service
  
  anpr-service:
    # ... remains separate ...
```

## Service URLs

### For Users (Browser)
- **Application**: http://localhost:8001
- **Auth API Docs**: http://localhost:8001/docs
- **ANPR API Docs**: http://localhost:8002/docs

### Internal (Docker Network)
- **Auth Service**: `http://auth-service:8000`
- **ANPR Service**: `http://anpr-service:8000`

### API Calls from Frontend
```javascript
// Relative URLs (same origin)
fetch('/api/v1/auth/login', ...)      // Auth endpoints
fetch('/api/v1/users', ...)           // User endpoints

// ANPR Service (different container, still needs proxy)
// Option 1: Add proxy in auth-service
// Option 2: Call directly to port 8002
```

## Environment Variables

### Frontend (Built-time)
```env
# .env.production (used during npm build)
VITE_API_URL=/api/v1                  # Relative path for auth APIs
VITE_ANPR_API_URL=http://localhost:8002/api/v1  # ANPR service
```

### Backend (Runtime)
```env
DB_HOST=mysql
DB_PORT=3306
# ... other backend variables ...
```

## Benefits of Unified Container

### 1. **Simplified Deployment**
- One less container to manage
- Fewer port mappings
- Simpler networking

### 2. **Better Performance**
- No network hop between frontend and auth API
- Faster response times
- Reduced latency

### 3. **Easier CORS**
- Same origin for frontend and API
- No CORS issues for auth endpoints
- Simpler configuration

### 4. **Smaller Footprint**
- No Nginx container
- No separate Node.js runtime
- Reduced memory usage

### 5. **Simplified Development**
- Single service to rebuild
- Easier debugging
- Unified logs

## Trade-offs

### Advantages ✅
- Simpler architecture
- Fewer containers
- Better performance for auth APIs
- Easier CORS handling
- Single port for UI and auth API

### Considerations ⚠️
- Frontend rebuild requires backend rebuild
- Slightly longer build time (includes npm build)
- ANPR service still separate (requires proxy or direct calls)
- Less separation of concerns

## Development Workflow

### Production Build
```bash
# Build includes frontend + backend
docker-compose up -d --build auth-service

# Access everything on port 8001
curl http://localhost:8001              # Frontend
curl http://localhost:8001/api/v1/auth  # Auth API
curl http://localhost:8001/health       # Health
```

### Development Mode
```bash
# Backend with hot reload (no frontend rebuild)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# For frontend development, run separately:
cd frontend
npm run dev  # Runs on port 5173 with hot reload
```

## API Integration

### Same-Container APIs (Auth)
```typescript
// Frontend calls to auth-service APIs (same container)
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});
```

### Cross-Container APIs (ANPR)

**Option 1: Add Proxy in Auth Service**
```python
# In auth-service/app/main.py
from fastapi.responses import StreamingResponse
import httpx

@app.api_route("/api/anpr/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_anpr(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        url = f"http://anpr-service:8000/api/v1/{path}"
        response = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=await request.body()
        )
        return Response(content=response.content, status_code=response.status_code)
```

**Option 2: Direct Calls from Frontend**
```typescript
// Frontend calls directly to ANPR service (different port)
const response = await fetch('http://localhost:8002/api/v1/cameras');
```

## Migration from Previous Setup

### What Changed
1. ✅ Removed separate `frontend` service from docker-compose.yml
2. ✅ Modified `auth-service/Dockerfile` to build frontend
3. ✅ Updated `auth-service/app/main.py` to serve static files
4. ✅ Frontend now built during auth-service container build
5. ✅ All auth APIs remain at `/api/v1/*`
6. ✅ Frontend served on root path `/`

### What Stayed the Same
- ✅ ANPR service still separate
- ✅ MySQL, Redis, Loki unchanged
- ✅ API endpoints unchanged (still at /api/v1/*)
- ✅ Frontend code unchanged
- ✅ Backend code unchanged (except main.py routing)

## Quick Start

```bash
cd traffic-system-backend

# Start all services (frontend included in auth-service)
docker-compose up -d --build

# Access the application
open http://localhost:8001

# View logs
docker-compose logs -f auth-service
```

## Troubleshooting

### Frontend Not Loading
```bash
# Check if frontend was built
docker-compose exec auth-service ls -la /app/frontend/dist

# Rebuild with no cache
docker-compose build --no-cache auth-service
docker-compose up -d auth-service
```

### API Calls Failing
```bash
# Check API routes
curl http://localhost:8001/api/v1/auth/health
curl http://localhost:8001/docs

# Check logs
docker-compose logs -f auth-service
```

### Static Assets Not Loading
```bash
# Verify assets directory
docker-compose exec auth-service ls -la /app/frontend/dist/assets

# Check Vite build output
cd frontend && npm run build
ls -la dist/
```

## Future Enhancements

### Option 1: Full Unification
Consolidate ANPR service into auth-service as well:
- Single container for all backend services
- Unified API gateway
- Simplest possible deployment

### Option 2: API Gateway Pattern
Add dedicated API gateway:
- Nginx or Traefik as reverse proxy
- Routes `/api/auth/*` → auth-service
- Routes `/api/anpr/*` → anpr-service
- Serves frontend static files
- Most scalable approach

### Option 3: Keep Current (Recommended)
- Auth service + frontend (unified) ✅
- ANPR service (separate)
- Balance between simplicity and separation
- Easy to scale ANPR independently

## Summary

The ATMS frontend is now **integrated into the auth-service container**, served by FastAPI alongside the authentication APIs. This provides a simpler, more efficient architecture while maintaining the modularity of the ANPR service.

**Access the application**: http://localhost:8001 🚀

