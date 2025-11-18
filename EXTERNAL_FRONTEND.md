# External Frontend Configuration

## Overview

The ATMS frontend code is maintained in a **separate directory** (`traffic-system-frontend-figma`) outside the backend repository. The Docker build process references this external directory during the build.

## Directory Structure

```
ITS-Dashboard/
├── traffic-system-backend/          # Backend services + Docker config
│   ├── services/
│   │   ├── auth-service/
│   │   │   └── Dockerfile          # References ../traffic-system-frontend-figma
│   │   ├── anpr-service/
│   │   └── shared/
│   ├── docker-compose.yml          # Build context: .. (parent directory)
│   └── (NO frontend directory)
│
└── traffic-system-frontend-figma/  # ✨ Single source of truth for frontend
    ├── src/
    ├── package.json
    ├── vite.config.ts
    └── ...
```

## How It Works

### 1. Docker Build Context

The `docker-compose.yml` uses the **parent directory** as the build context:

```yaml
services:
  auth-service:
    build:
      context: ..  # Parent directory (ITS-Dashboard)
      dockerfile: ./traffic-system-backend/services/auth-service/Dockerfile
```

This allows the Dockerfile to access both:
- `traffic-system-backend/` (for backend code)
- `traffic-system-frontend-figma/` (for frontend code)

### 2. Multi-Stage Dockerfile

The `auth-service/Dockerfile` references the external frontend:

```dockerfile
# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend

# Copy from external directory
COPY traffic-system-frontend-figma/package*.json ./
RUN npm ci --silent

COPY traffic-system-frontend-figma/ ./
RUN npm run build

# Stage 2: Backend + Built Frontend
FROM python:3.11-slim
# ... backend setup ...

# Copy built frontend from Stage 1
COPY --from=frontend-builder /frontend/dist /app/frontend/dist
```

### 3. Build Process

```bash
cd traffic-system-backend

# Docker starts from parent directory
# Accesses: ../traffic-system-frontend-figma/
docker-compose build auth-service
```

## Benefits

✅ **Single Source of Truth**: Frontend code lives in one place  
✅ **No Duplication**: No need to copy frontend files  
✅ **Easy Development**: Edit frontend in original location  
✅ **Clean Separation**: Backend and frontend repos stay separate  
✅ **Flexible**: Can easily swap frontend implementations  

## Development Workflow

### Option 1: Full Docker Build

```bash
cd traffic-system-backend
docker-compose up -d --build

# Frontend changes require rebuild
docker-compose build auth-service
docker-compose up -d auth-service
```

### Option 2: Local Frontend Development (Recommended)

```bash
# Start backend services only
cd traffic-system-backend
docker-compose up -d auth-service anpr-service mysql redis

# Run frontend locally with hot reload
cd ../traffic-system-frontend-figma
npm install
npm run dev  # http://localhost:5173

# Edit frontend files - instant reload!
# No Docker rebuild needed
```

## Important Notes

### 1. Directory Location Required

Both directories **must be siblings** in the same parent directory:

```
✅ CORRECT:
ITS-Dashboard/
├── traffic-system-backend/
└── traffic-system-frontend-figma/

❌ WRONG:
/different/path/traffic-system-backend/
/another/path/traffic-system-frontend-figma/
```

### 2. Build Context Size

Since the build context is the parent directory, Docker sends both directories to the build daemon. To optimize:

- `.dockerignore` file at parent level excludes unnecessary files
- Frontend `node_modules/` and `dist/` are ignored
- Backend `__pycache__/` files are ignored

### 3. CI/CD Considerations

In CI/CD pipelines, ensure both directories are available:

```yaml
# GitHub Actions example
- name: Checkout backend
  uses: actions/checkout@v3
  with:
    path: traffic-system-backend

- name: Checkout frontend
  uses: actions/checkout@v3
  with:
    repository: your-org/traffic-system-frontend-figma
    path: traffic-system-frontend-figma

- name: Build
  working-directory: traffic-system-backend
  run: docker-compose build
```

## Troubleshooting

### Build fails: "Cannot find traffic-system-frontend-figma"

**Problem**: Docker can't find the frontend directory.

**Solution**: Ensure both directories are siblings:
```bash
ls -la ..
# Should show both:
# traffic-system-backend/
# traffic-system-frontend-figma/
```

### Build is slow

**Problem**: Large build context being sent to Docker.

**Solution**: 
1. Check `.dockerignore` exists at parent level
2. Ensure `node_modules` and `dist` are excluded:
```bash
cat ../.dockerignore | grep -E "node_modules|dist"
```

### Frontend changes not reflected

**Problem**: Docker is using cached build.

**Solution**: Force rebuild without cache:
```bash
docker-compose build --no-cache auth-service
docker-compose up -d auth-service
```

### Volume mount conflicts

**Problem**: Development mode volume mounts may conflict.

**Solution**: Volume mounts are relative to docker-compose.yml location:
```yaml
volumes:
  - ./services:/app/services  # Still works from traffic-system-backend/
```

## Commands Reference

### Build Commands

```bash
# From traffic-system-backend directory

# Build all services
docker-compose build

# Build only auth-service (includes frontend)
docker-compose build auth-service

# Force rebuild without cache
docker-compose build --no-cache auth-service

# Build and start
docker-compose up -d --build
```

### Development Commands

```bash
# Backend in Docker, Frontend local (fast iteration)
cd traffic-system-backend
docker-compose up -d mysql redis auth-service anpr-service

cd ../traffic-system-frontend-figma
npm run dev

# Full Docker (production-like)
cd traffic-system-backend
docker-compose up -d --build
```

### Verification Commands

```bash
# Check frontend was built into container
docker-compose exec auth-service ls -la /app/frontend/dist

# Test frontend access
curl -I http://localhost:8001/

# Test API access
curl http://localhost:8001/api/v1/health
```

## Migrating to Monorepo (Future)

If you want to combine both into a single repo later:

```
atms-monorepo/
├── frontend/          # Moved from traffic-system-frontend-figma
├── backend/           # Moved from traffic-system-backend
└── docker-compose.yml # At root level
```

Then update docker-compose.yml:
```yaml
services:
  auth-service:
    build:
      context: .        # Root directory
      dockerfile: ./backend/services/auth-service/Dockerfile
```

And update Dockerfile paths:
```dockerfile
COPY frontend/package*.json ./
COPY backend/services/auth-service/ /app/
```

## Summary

The ATMS system uses an **external frontend architecture** where:

- 🎨 **Frontend**: Lives in `traffic-system-frontend-figma/`
- 🔧 **Backend**: Lives in `traffic-system-backend/`
- 🐳 **Docker**: References frontend during build
- 🚀 **Result**: Unified container with both frontend and backend

**Key Point**: The frontend directory `traffic-system-frontend-figma` is the **single source of truth**. Edit files there, and Docker will include them during the next build.

**Access the application**: http://localhost:8001 🚀

