"""
Auth Service Main Application
Serves both API endpoints and frontend static files
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from services.shared.config.settings import settings
from services.shared.middleware import configure_request_logging
from services.shared.utils.logger import setup_logger
from app.api import auth, users, roles

logger = setup_logger(__name__)

app = FastAPI(
    title="ATMS - Automated Traffic Management System",
    description="Authentication and Authorization Service with Frontend",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Request logging middleware (must be registered before other middleware)
configure_request_logging(
    app,
    service_name="auth-service",
    skip_paths={"/health"},
    skip_prefixes={"/docs", "/openapi", "/assets"},
    log_headers=("x-request-id", "x-forwarded-for"),
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
# API_V1_PREFIX already includes /api/v1
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["Authentication"])
app.include_router(users.router, prefix=settings.API_V1_PREFIX, tags=["Users"])
app.include_router(roles.role_router, prefix=settings.API_V1_PREFIX, tags=["Roles"])
app.include_router(roles.service_router, prefix=settings.API_V1_PREFIX, tags=["Services"])
app.include_router(roles.permission_router, prefix=settings.API_V1_PREFIX, tags=["Permissions"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth-service"}


@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {"message": "ATMS API", "version": "1.0.0", "service": "auth-service"}


# Mount frontend static files
frontend_dist = Path("/app/frontend/dist")
if frontend_dist.exists():
    # Mount static assets (JS, CSS, images, etc.)
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """
        Serve frontend static files and handle SPA routing.
        For any non-API route, serve index.html to support React Router.
        """
        # Skip API routes - they should be handled by API routers
        if full_path.startswith("api/") or full_path == "health":
            # This shouldn't be reached if routes are properly registered
            # But if it is, return 404 instead of serving HTML
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        
        # If requesting a specific file that exists, serve it
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        # For all other routes (SPA routing), serve index.html
        index_path = frontend_dist / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        
        return {"error": "Frontend not found"}
else:
    logger.warning("Frontend dist directory not found. Frontend will not be served.")
    
    @app.get("/")
    async def root():
        """Root endpoint when frontend is not available"""
        return {
            "message": "ATMS Backend Service",
            "version": "1.0.0",
            "warning": "Frontend not built or not found"
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

