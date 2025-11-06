# Setup Instructions

## Step 1: Project Foundation - Setup Complete ✅

All foundation files have been created. Here's what was set up:

### Project Structure
- ✅ Services directory structure (auth-service, anpr-service, shared)
- ✅ Docker configuration (docker-compose.yml, Dockerfiles)
- ✅ MySQL database configuration
- ✅ Redis configuration
- ✅ Shared database utilities (Base model, session management)
- ✅ Alembic migration setup for both services
- ✅ Logging configuration (JSON and text formats)

## Next Steps

### 1. Create Environment File
Create a `.env` file in the root directory (copy from `.env.example` if it exists):
```bash
cp .env.example .env
```

Or manually create `.env` with:
```env
DB_ROOT_PASSWORD=rootpassword
DB_NAME=traffic_system
DB_USER=app_user
DB_PASS=app_password
SECRET_KEY=your-secret-key-here
```

### 2. Start Services
```bash
# Start all services
docker-compose up -d

# Or with development hot-reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### 3. Verify Services
- Auth Service: http://localhost:8001/health
- ANPR Service: http://localhost:8002/health
- MySQL: localhost:3306
- Redis: localhost:6379

### 4. Run Database Migrations
```bash
# For auth service
cd services/auth-service
alembic upgrade head

# For ANPR service (after models are created)
cd services/anpr-service
alembic upgrade head
```

## Service Structure

```
traffic-system-backend/
├── services/
│   ├── auth-service/          # Authentication service
│   │   ├── app/               # Application code
│   │   ├── alembic/           # Database migrations
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── anpr-service/          # ANPR service
│   │   ├── app/               # Application code
│   │   ├── alembic/           # Database migrations
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── shared/                # Shared utilities
│       ├── database/          # DB base classes, session
│       ├── utils/             # Logger, exceptions
│       └── config/            # Shared settings
├── docker-compose.yml         # Production compose
├── docker-compose.dev.yml     # Development overrides
└── .env                       # Environment variables
```

## Troubleshooting

### Database Connection Issues
- Verify MySQL is running: `docker-compose ps`
- Check credentials in `.env` file
- Verify network connectivity: `docker-compose exec mysql mysql -uroot -p`

### Service Not Starting
- Check logs: `docker-compose logs auth-service`
- Verify ports aren't in use: `lsof -i :8001`
- Check Docker resources: `docker stats`

### Import Errors
- Ensure `services/shared` is in Python path
- Check that all `__init__.py` files exist
- Verify requirements are installed

## Development Tips

1. **Hot Reload**: Use `docker-compose.dev.yml` for auto-reload on code changes
2. **Database Access**: 
   ```bash
   docker-compose exec mysql mysql -uroot -p traffic_system
   ```
3. **Redis Access**:
   ```bash
   docker-compose exec redis redis-cli
   ```
4. **View Logs**:
   ```bash
   docker-compose logs -f auth-service
   ```

## Ready for Next Phase

✅ Foundation is complete! You can now proceed to:
- Step 2: Create Auth Service models and database schema
- Step 3: Implement authentication endpoints

