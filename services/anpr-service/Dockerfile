FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY traffic-system-backend/services/anpr-service/requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Copy shared directory
COPY traffic-system-backend/services/shared /app/services/shared

# Copy application code
COPY traffic-system-backend/services/anpr-service /app/services/anpr-service

# Set working directory to the anpr-service directory
WORKDIR /app/services/anpr-service

# Set PYTHONPATH to include the services directory so 'services.shared' can be imported
ENV PYTHONPATH=/app/services

# Copy and set entrypoint script
COPY traffic-system-backend/services/anpr-service/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run application with migrations
ENTRYPOINT ["/entrypoint.sh"]

