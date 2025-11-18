# Migration to External Frontend - November 18, 2024

## What Changed

The ATMS system has been reconfigured to use **`traffic-system-frontend-figma`** as the single source of truth for frontend code, instead of maintaining a duplicate copy inside `traffic-system-backend/frontend/`.

## Changes Made

### 1. Removed Duplicate Frontend Directory
```bash
# Deleted: traffic-system-backend/frontend/
# Now using: ../traffic-system-frontend-figma/
```

### 2. Updated Docker Build Context

**Before:**
```yaml
services:
  auth-service:
    build:
      context: .  # traffic-system-backend directory
      dockerfile: ./services/auth-service/Dockerfile
```

**After:**
```yaml
services:
  auth-service:
    build:
      context: ..  # Parent directory (ITS-Dashboard)
      dockerfile: ./traffic-system-backend/services/auth-service/Dockerfile
```

### 3. Updated Dockerfiles

**Auth Service Dockerfile** - Updated paths:
```dockerfile
# Before:
COPY frontend/package*.json ./
COPY frontend/ ./
COPY services/auth-service/requirements.txt /tmp/

# After:
COPY traffic-system-frontend-figma/package*.json ./
COPY traffic-system-frontend-figma/ ./
COPY traffic-system-backend/services/auth-service/requirements.txt /tmp/
```

**ANPR Service Dockerfile** - Updated paths:
```dockerfile
# Before:
COPY services/anpr-service/requirements.txt /tmp/

# After:
COPY traffic-system-backend/services/anpr-service/requirements.txt /tmp/
```

### 4. Added Build Optimization

Created `.dockerignore` at parent level to exclude:
- `traffic-system-frontend-figma/node_modules`
- `traffic-system-frontend-figma/dist`
- `traffic-system-backend/__pycache__`
- Environment files
- IDE files

### 5. Updated Documentation

- ✅ Created `EXTERNAL_FRONTEND.md` - Explains the external directory setup
- ✅ Updated `README.md` - Project structure and local development
- ✅ Updated `UNIFIED_CONTAINER.md` - Build process explanation
- ✅ Updated `BUILD_INSTRUCTIONS.md` - Build commands and context
- ✅ Updated `.gitignore` - Removed frontend-specific entries

## Directory Structure

```
ITS-Dashboard/                          (Parent directory)
├── .dockerignore                       ← NEW: Build optimization
│
├── traffic-system-backend/             (Backend + Docker config)
│   ├── services/
│   │   ├── auth-service/
│   │   │   └── Dockerfile              ← UPDATED: References ../traffic-system-frontend-figma
│   │   ├── anpr-service/
│   │   │   └── Dockerfile              ← UPDATED: Updated paths
│   │   └── shared/
│   ├── docker-compose.yml              ← UPDATED: context: ..
│   ├── EXTERNAL_FRONTEND.md            ← NEW: External frontend docs
│   ├── MIGRATION_NOTES.md              ← NEW: This file
│   └── (frontend/ directory deleted)   ← REMOVED
│
└── traffic-system-frontend-figma/      ✨ Single source of truth
    ├── src/
    ├── package.json
    └── ...
```

## How to Build

### First Time Setup

```bash
# Ensure both directories exist as siblings
cd /Users/hellohasib/Documents/Development/ITS-Dashboard
ls -la
# Should show:
# - traffic-system-backend/
# - traffic-system-frontend-figma/

# Navigate to backend
cd traffic-system-backend

# Build (will access ../traffic-system-frontend-figma)
docker-compose build --no-cache auth-service

# Start
docker-compose up -d
```

### Regular Development

```bash
cd traffic-system-backend

# Build and start
docker-compose up -d --build

# Or use the startup script
./start.sh
```

## Local Frontend Development

To edit frontend code with hot reload:

```bash
# Start backend in Docker
cd traffic-system-backend
docker-compose up -d auth-service anpr-service mysql redis

# Run frontend locally
cd ../traffic-system-frontend-figma
npm install
npm run dev  # http://localhost:5173

# Edit files in traffic-system-frontend-figma/src/
# Changes will hot-reload instantly
```

## Verification

### 1. Verify Directory Structure
```bash
cd /Users/hellohasib/Documents/Development/ITS-Dashboard
ls -la
# Should show both: traffic-system-backend/ and traffic-system-frontend-figma/
```

### 2. Verify No Duplicate Frontend
```bash
cd traffic-system-backend
ls -la | grep frontend
# Should return nothing (frontend dir removed)
```

### 3. Test Build
```bash
cd traffic-system-backend
docker-compose build auth-service
# Should succeed without errors
```

### 4. Verify Frontend in Container
```bash
docker-compose up -d auth-service
docker-compose exec auth-service ls -la /app/frontend/dist
# Should show: index.html, assets/, etc.
```

### 5. Test Application
```bash
# Access frontend
curl -I http://localhost:8001/
# Should return: 200 OK

# Access API
curl http://localhost:8001/api/v1/health
# Should return: {"status": "healthy", ...}
```

## Benefits

✅ **No Code Duplication**
- Frontend code exists in one place only
- No need to sync changes between directories

✅ **Cleaner Repository**
- Backend repo contains only backend code
- Frontend repo contains only frontend code

✅ **Easier Development**
- Edit frontend in `traffic-system-frontend-figma/`
- Docker build picks up changes automatically

✅ **Flexible Architecture**
- Can easily swap frontend implementations
- Frontend and backend can evolve independently

## Troubleshooting

### Build Error: "Cannot find traffic-system-frontend-figma"

**Problem**: Docker can't access the frontend directory.

**Solution**: Ensure both directories are in the same parent:
```bash
cd /Users/hellohasib/Documents/Development/ITS-Dashboard
ls -la
# Must show BOTH directories
```

### Build is Slow or Hangs

**Problem**: Large build context.

**Solution**: Verify `.dockerignore` exists at parent level:
```bash
cd /Users/hellohasib/Documents/Development/ITS-Dashboard
cat .dockerignore
# Should exclude node_modules, dist, __pycache__, etc.
```

### Frontend Changes Not Reflected

**Problem**: Docker cache is stale.

**Solution**: Rebuild without cache:
```bash
cd traffic-system-backend
docker-compose build --no-cache auth-service
docker-compose up -d auth-service
```

### Volume Mount Issues in Dev Mode

**Problem**: Dev mode volume mounts may not work.

**Solution**: Volume paths are still relative to docker-compose.yml:
```yaml
# This still works:
volumes:
  - ./services:/app/services
# Mounts from traffic-system-backend/services
```

## Rolling Back

If you need to revert to the old setup:

```bash
# 1. Copy frontend back
cd traffic-system-backend
cp -r ../traffic-system-frontend-figma frontend/

# 2. Update docker-compose.yml
# Change context: .. to context: .

# 3. Update Dockerfiles
# Change traffic-system-frontend-figma/ to frontend/
# Change traffic-system-backend/ to ./

# 4. Rebuild
docker-compose build --no-cache
```

## Next Steps

1. ✅ **Test the build** - Verify everything works
2. ✅ **Update CI/CD** - Ensure both repos are checked out
3. ✅ **Team notification** - Inform team of new structure
4. ✅ **Documentation** - Share EXTERNAL_FRONTEND.md with team

## Summary

The frontend code now lives **exclusively** in `traffic-system-frontend-figma/`. The Docker build process references this external directory during the build. This eliminates code duplication and makes development cleaner.

**Key Points:**
- 📁 Frontend: `traffic-system-frontend-figma/` (single source of truth)
- 🐳 Docker: Uses parent directory as build context
- 🔨 Build: References external frontend automatically
- 💻 Dev: Edit frontend in original location, hot reload works

**Migration Complete!** 🎉

