# Multi-stage build: Frontend + Backend in one container

# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend package files from external directory
COPY traffic-system-frontend-figma/package*.json ./

# Install dependencies
RUN npm ci --silent

# Copy frontend source from external directory
COPY traffic-system-frontend-figma/ ./

# Build frontend for production
RUN npm run build

# Stage 2: Backend with Frontend
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY traffic-system-backend/services/auth-service/requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Copy shared directory
COPY traffic-system-backend/services/shared /app/services/shared

# Copy application code
COPY traffic-system-backend/services/auth-service /app/services/auth-service

# Copy built frontend from stage 1
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

# Set working directory to the auth-service directory
WORKDIR /app/services/auth-service

# Set PYTHONPATH to include the services directory so 'services.shared' can be imported
ENV PYTHONPATH=/app/services

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run application - use app.main since we're in the auth-service directory
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
