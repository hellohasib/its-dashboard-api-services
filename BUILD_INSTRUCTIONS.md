# Building the ATMS System

## Quick Build

```bash
# Build and start everything
docker-compose up -d --build

# Access application
open http://localhost:8001
```

## Understanding the Build Process

### Multi-Stage Build (Auth Service + Frontend)

The auth-service Dockerfile uses a multi-stage build to include the React frontend:

```dockerfile
# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
# Frontend code is in external directory (sibling to backend)
COPY traffic-system-frontend-figma/ ./
RUN npm ci && npm run build

# Stage 2: Backend + Built Frontend
FROM python:3.11-slim
# ... Python setup ...
COPY --from=frontend-builder /frontend/dist /app/frontend/dist
```

**Important**: The frontend source code is in `../traffic-system-frontend-figma/` (external directory). Docker Compose uses the parent directory as build context. See [EXTERNAL_FRONTEND.md](./EXTERNAL_FRONTEND.md) for details.

### Build Steps

1. **Stage 1: Frontend Build**
   - Uses Node.js 20 Alpine image
   - Installs npm dependencies
   - Runs `npm run build` (Vite build)
   - Produces optimized static files in `dist/`

2. **Stage 2: Backend + Static Files**
   - Uses Python 3.11 Slim image
   - Installs Python dependencies
   - Copies backend code
   - Copies built frontend from Stage 1
   - Result: Single image with both frontend and backend

### Build Time

- **First Build**: 5-10 minutes (downloads all dependencies)
- **Subsequent Builds**: 2-5 minutes (uses Docker layer caching)
- **Frontend-Only Changes**: ~2 minutes (only rebuilds from frontend stage)
- **Backend-Only Changes**: ~1 minute (reuses frontend cache)

## Build Commands

### Full Rebuild

```bash
# Rebuild everything (no cache)
docker-compose build --no-cache auth-service

# Or rebuild all services
docker-compose build --no-cache
```

### Quick Rebuild (Using Cache)

```bash
# Rebuild with cache
docker-compose build auth-service

# Or let docker-compose decide what to rebuild
docker-compose up -d --build
```

### Service-Specific Builds

```bash
# Build only auth-service (includes frontend)
docker-compose build auth-service

# Build only ANPR service
docker-compose build anpr-service

# Build infrastructure services (rarely needed)
docker-compose pull mysql redis loki otel-collector
```

## Build Optimization

### Layer Caching

Docker caches layers to speed up builds. The Dockerfile is optimized for caching:

```dockerfile
# These layers rarely change (cached longest)
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# These layers change more frequently
COPY services/shared /app/services/shared
COPY services/auth-service /app/services/auth-service

# Frontend changes most frequently
COPY --from=frontend-builder /frontend/dist /app/frontend/dist
```

### When to Clear Cache

Clear cache when:
- Dependencies are updated but not reflected
- Build behaving unexpectedly
- Want to ensure clean build for production

```bash
docker-compose build --no-cache auth-service
```

## Troubleshooting Builds

### Build Fails at Frontend Stage

```bash
# Error: npm install fails
# Solution: Clear npm cache and rebuild
docker-compose build --no-cache auth-service
```

### Build Fails at Python Dependencies

```bash
# Error: mysqlclient build fails
# Solution: Ensure system dependencies are installed
# Check Dockerfile has: gcc, default-libmysqlclient-dev, pkg-config
```

### Build Takes Too Long

```bash
# If builds are consistently slow:
# 1. Check Docker Desktop resources (increase CPU/RAM)
# 2. Clear unused images/containers
docker system prune -a

# 3. Check network speed (npm/pip downloads)
# 4. Use BuildKit for faster builds
DOCKER_BUILDKIT=1 docker-compose build
```

### Frontend Build Errors

```bash
# Check frontend builds locally
cd frontend
npm install
npm run build

# If successful, the issue is with Docker build context
# Ensure .dockerignore doesn't exclude necessary files
```

## Image Sizes

Expected sizes:
- **auth-service**: ~800MB-1GB (Python + built frontend)
- **anpr-service**: ~800MB (Python only)
- **mysql**: ~500MB
- **redis**: ~50MB (Alpine)
- **loki**: ~100MB
- **otel-collector**: ~200MB

Total: ~2.5-3GB for all images

## Build for Production

### Production Build

```bash
# Set production environment
export APP_ENV=production
export DEBUG=False

# Build with production settings
docker-compose build auth-service

# Or use separate production compose file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
```

### Production Optimizations

1. **Multi-stage build** already minimizes image size
2. **No dev dependencies** (npm ci only installs production deps)
3. **Optimized Vite build** (minification, tree-shaking, code splitting)
4. **Alpine images** where possible (Redis, frontend builder)

## Continuous Integration

### GitHub Actions Example

```yaml
name: Build and Test

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: docker-compose build
      
      - name: Start services
        run: docker-compose up -d
      
      - name: Wait for services
        run: |
          timeout 60 bash -c 'until curl -f http://localhost:8001/health; do sleep 2; done'
      
      - name: Run tests
        run: |
          docker-compose exec -T auth-service pytest
      
      - name: Cleanup
        run: docker-compose down -v
```

## Build Artifacts

### What Gets Built

1. **Frontend (Vite Build)**
   - `dist/index.html` - Main HTML file
   - `dist/assets/*.js` - JavaScript bundles
   - `dist/assets/*.css` - CSS bundles
   - `dist/assets/*.png|svg|ico` - Images and icons

2. **Backend (Python)**
   - Compiled Python bytecode (`.pyc` files)
   - Installed packages in Python environment

### Verifying Build Success

```bash
# Check auth-service container has frontend
docker-compose exec auth-service ls -la /app/frontend/dist

# Should see:
# index.html
# assets/
# favicon.ico (if any)

# Test frontend access
curl -I http://localhost:8001/
# Should return: 200 OK

# Test API access
curl http://localhost:8001/api/v1/health
# Should return: {"status": "healthy"}
```

## Development vs Production Builds

### Development
- Hot reload enabled (volume mounts)
- Source maps included
- Debug mode enabled
- Verbose logging
- No minification

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production
- Optimized builds
- No source maps
- Minified assets
- Production logging
- No dev dependencies

```bash
docker-compose up -d
```

## Build Performance Tips

1. **Use BuildKit**
   ```bash
   export DOCKER_BUILDKIT=1
   docker-compose build
   ```

2. **Increase Docker Resources**
   - Docker Desktop → Settings → Resources
   - Increase CPUs to 4+ and RAM to 8GB+

3. **Use .dockerignore**
   ```
   node_modules
   __pycache__
   *.pyc
   .git
   .env
   ```

4. **Parallel Builds**
   ```bash
   docker-compose build --parallel
   ```

5. **Prune Regularly**
   ```bash
   docker system prune -f
   docker volume prune -f
   ```

## Summary

The ATMS build process creates a **unified container** with:
- ✅ React frontend (built with Vite)
- ✅ FastAPI backend (Python 3.11)
- ✅ All dependencies installed
- ✅ Optimized for production
- ✅ Fast rebuilds with layer caching

**Total build time**: 5-10 minutes (first), 2-5 minutes (subsequent)

**Result**: Single `auth-service` image serving both frontend and API on port 8001 🚀
