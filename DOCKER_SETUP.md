# Docker Setup Guide

## Prerequisites
- Docker and Docker Compose installed
- `.env` file configured (copy from `.env.example` if needed)

## Quick Start

### 1. Create Environment File
Copy the example environment file and update values as needed:
```bash
cd /Users/hellohasib/Documents/Development/ITS-Dashboard/traffic-system-backend
cp .env.example .env
```

Edit `.env` and set at least:
- `SECRET_KEY` (generate a secure random string)
- Database passwords if needed

### 2. Start All Services
```bash
docker-compose up -d
```

This will start:
- MySQL database (port 3307)
- Redis (port 6379)
- Auth Service (port 8001)
- ANPR Service (port 8002)
- Frontend (port 3000)
- Loki (logging, port 3100)
- OpenTelemetry Collector (ports 4317, 4318)

### 3. Check Service Status
```bash
docker-compose ps
```

### 4. View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f anpr-service
docker-compose logs -f auth-service
```

## ANPR Service Specific Commands

### Access ANPR Service
- API: http://localhost:8002
- Health check: http://localhost:8002/health
- API docs (dev mode): http://localhost:8002/docs

### Run Migrations Manually
If you need to run migrations separately:
```bash
docker-compose exec anpr-service alembic upgrade head
```

### Access ANPR Service Shell
```bash
docker-compose exec anpr-service bash
```

### Rebuild ANPR Service
After code changes:
```bash
docker-compose up -d --build anpr-service
```

## Database Access

### Connect to MySQL
```bash
docker-compose exec mysql mysql -u app_user -p its_dashboard
# Password: app_password (or from your .env)
```

### View ANPR Tables
```sql
USE its_dashboard;
SHOW TABLES;
DESCRIBE anpr_cameras;
DESCRIBE lpr_events;
SELECT * FROM anpr_cameras;
```

## Stopping Services

### Stop all services
```bash
docker-compose down
```

### Stop and remove volumes (⚠️ deletes data)
```bash
docker-compose down -v
```

## Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs anpr-service

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache anpr-service
docker-compose up -d
```

### Database connection issues
```bash
# Verify MySQL is healthy
docker-compose ps mysql

# Check if database exists
docker-compose exec mysql mysql -u root -p -e "SHOW DATABASES;"
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d
```

## Development Workflow

### Hot Reload (Development)
The ANPR service volume is mounted, so code changes will auto-reload:
```bash
# Edit files locally
# Service will restart automatically
docker-compose logs -f anpr-service
```

### Run Tests
```bash
docker-compose exec anpr-service pytest
```

## Production Considerations

1. Set `APP_ENV=production` in `.env`
2. Set `DEBUG=False`
3. Use strong passwords for database
4. Generate a secure `SECRET_KEY`
5. Configure proper CORS origins
6. Set up proper logging and monitoring
7. Use secrets management instead of `.env` file

