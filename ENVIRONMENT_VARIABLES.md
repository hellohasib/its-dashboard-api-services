# Environment Variables Configuration

This document describes all environment variables used in the ATMS system.

## Quick Setup

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Database Configuration

### MySQL
```env
DB_HOST=mysql                    # Database host (use 'mysql' for Docker, 'localhost' for local)
DB_PORT=3306                     # MySQL port (3306 inside Docker, 3307 on host)
DB_NAME=its_dashboard            # Database name
DB_USER=app_user                 # Application database user
DB_PASS=app_password             # Application user password
DB_ROOT_PASSWORD=rootpassword    # MySQL root password (for initial setup)
```

**Note**: When running services locally outside Docker, use `localhost:3307` for DB_HOST:DB_PORT.

## Redis Configuration

```env
REDIS_HOST=redis                 # Redis host (use 'redis' for Docker, 'localhost' for local)
REDIS_PORT=6379                  # Redis port
```

## JWT Authentication

```env
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=525600    # 365 days (long-lived for development)
REFRESH_TOKEN_EXPIRE_DAYS=365         # 1 year
```

**Security**: Change `SECRET_KEY` in production to a strong random string:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Application Configuration

```env
APP_ENV=development              # Environment: development, staging, production
DEBUG=True                       # Enable debug mode (False in production)
```

## Service Configuration

Each service has a name and namespace for logging/tracing:
```env
SERVICE_NAME=auth-service        # Service identifier
SERVICE_NAMESPACE=traffic-system # System namespace
```

## Logging Configuration

```env
LOG_LEVEL=INFO                   # Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json                  # Log format: json, text
LOG_DESTINATION=console          # Destination: console, file, loki
```

### Log Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages (recommended for development)
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical issues

## Observability

### OpenTelemetry Collector
```env
OTLP_ENDPOINT=http://otel-collector:4317    # OpenTelemetry gRPC endpoint
OTEL_COLLECTOR_GRPC_PORT=4317               # OTLP gRPC port (internal)
OTEL_COLLECTOR_HTTP_PORT=4318               # OTLP HTTP port (internal)
```

### Loki (Log Aggregation)
```env
LOKI_ENDPOINT=http://loki:3100              # Loki endpoint
LOKI_HTTP_PORT=3100                         # Loki HTTP port (host)
LOKI_TIMEOUT_SECONDS=5                      # Timeout for Loki requests
```

## Frontend Configuration

### API Endpoints
```env
VITE_API_URL=http://localhost:8001          # Auth service URL (for frontend)
VITE_ANPR_API_URL=http://localhost:8002     # ANPR service URL (for frontend)
```

**Note**: These URLs are used by the browser, so they should point to the host machine's ports.

## Service-to-Service Communication

Backend services communicate internally using Docker network:
```env
AUTH_SERVICE_URL=http://auth-service:8000   # Internal auth service URL
```

## Complete .env Example

```env
# Database Configuration
DB_HOST=mysql
DB_PORT=3306
DB_NAME=its_dashboard
DB_USER=app_user
DB_PASS=app_password
DB_ROOT_PASSWORD=rootpassword

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=525600
REFRESH_TOKEN_EXPIRE_DAYS=365

# Application Configuration
APP_ENV=development
DEBUG=True

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_DESTINATION=console

# Observability
OTLP_ENDPOINT=http://otel-collector:4317
LOKI_ENDPOINT=http://loki:3100
LOKI_TIMEOUT_SECONDS=5
LOKI_HTTP_PORT=3100
OTEL_COLLECTOR_GRPC_PORT=4317
OTEL_COLLECTOR_HTTP_PORT=4318

# Frontend API URLs (for local development)
VITE_API_URL=http://localhost:8001
VITE_ANPR_API_URL=http://localhost:8002
```

## Environment-Specific Configuration

### Development
```env
APP_ENV=development
DEBUG=True
LOG_LEVEL=DEBUG
ACCESS_TOKEN_EXPIRE_MINUTES=525600
```

### Production
```env
APP_ENV=production
DEBUG=False
LOG_LEVEL=INFO
ACCESS_TOKEN_EXPIRE_MINUTES=30
SECRET_KEY=<strong-random-key>
```

### Testing
```env
APP_ENV=testing
DEBUG=True
DB_NAME=its_dashboard_test
LOG_LEVEL=DEBUG
```

## Docker Compose Variables

Some variables are only used by Docker Compose for port mapping:

```env
# Host port mappings (external access)
# Frontend
FRONTEND_PORT=3000

# Backend Services
AUTH_PORT=8001
ANPR_PORT=8002

# Database
DB_HOST_PORT=3307          # Host port (to avoid conflicts with local MySQL)

# Observability
LOKI_HTTP_PORT=3100
OTEL_COLLECTOR_GRPC_PORT=4317
OTEL_COLLECTOR_HTTP_PORT=4318
```

## Validation

To validate your environment configuration:

```bash
# Check if .env file exists
ls -la .env

# View (sanitized) environment
docker-compose config | grep -E "VITE_|DB_|LOG_"

# Test database connection
docker-compose exec auth-service python -c "from app.core.database import engine; engine.connect()"
```

## Security Best Practices

1. **Never commit `.env` files** to version control
2. Use strong random values for `SECRET_KEY`
3. Change default passwords in production
4. Limit `ACCESS_TOKEN_EXPIRE_MINUTES` in production (30-60 minutes)
5. Set `DEBUG=False` in production
6. Use environment-specific `.env` files:
   - `.env.development`
   - `.env.staging`
   - `.env.production`

## Troubleshooting

### Variable Not Being Used
- Ensure the service is restarted after changing `.env`
- Check `docker-compose.yml` includes the variable in the `environment` section
- Use `docker-compose config` to verify values

### Connection Refused Errors
- Verify `DB_HOST` and `REDIS_HOST` are correct for your environment
- For Docker: use service names (`mysql`, `redis`)
- For local: use `localhost`

### Token Expiration Issues
- Check `ACCESS_TOKEN_EXPIRE_MINUTES` is set appropriately
- Verify system clocks are synchronized
- Clear old tokens from Redis: `docker-compose exec redis redis-cli FLUSHDB`

