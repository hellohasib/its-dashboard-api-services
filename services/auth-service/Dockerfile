FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY services/auth-service/requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Copy shared directory
COPY services/shared /app/services/shared

# Copy application code
COPY services/auth-service /app/services/auth-service

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

