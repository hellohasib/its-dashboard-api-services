"""
Auth Service Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.shared.config.settings import settings
from services.shared.utils.logger import setup_logger
from app.api import auth, users

logger = setup_logger(__name__)

app = FastAPI(
    title="Auth Service",
    description="Authentication and Authorization Service",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth-service"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Auth Service", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

