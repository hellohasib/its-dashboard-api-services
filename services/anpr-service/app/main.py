"""
ANPR Service Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.shared.config.settings import settings
from services.shared.middleware import configure_request_logging
from services.shared.utils.logger import setup_logger
from app.api import api_router

logger = setup_logger(__name__)

app = FastAPI(
    title="ANPR Service",
    description="License Plate Recognition Data Service",
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

# Request logging middleware
configure_request_logging(
    app,
    service_name="anpr-service",
    skip_paths={"/health"},
    skip_prefixes={"/docs", "/openapi"},
    log_headers=("x-request-id", "x-forwarded-for"),
)

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "anpr-service"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "ANPR Service", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

