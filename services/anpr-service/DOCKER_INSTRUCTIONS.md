# ANPR Service - Docker Instructions

## ✅ Setup Complete!

The ANPR service is now fully configured to run in Docker with:
- ✅ Database models for cameras and events
- ✅ Alembic migrations (auto-run on startup)
- ✅ FastAPI endpoints for camera management and event ingestion
- ✅ Docker Compose configuration
- ✅ Automatic migration on container start

## 🚀 Quick Start

### 1. Navigate to the backend directory
```bash
cd /Users/hellohasib/Documents/Development/ITS-Dashboard/traffic-system-backend
```

### 2. Ensure you have a `.env` file
If you don't have one, create it with minimal configuration:
```bash
cat > .env << 'EOF'
DB_ROOT_PASSWORD=rootpassword
DB_NAME=its_dashboard
DB_USER=app_user
DB_PASS=app_password
DB_PORT=3307
SECRET_KEY=your-secret-key-change-this-in-production
APP_ENV=development
DEBUG=True
EOF
```

### 3. Start the ANPR service
```bash
# Start all dependencies and ANPR service
docker-compose up -d anpr-service

# Or use the helper script
./start-anpr.sh
```

### 4. Verify it's running
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f anpr-service

# Test the API
curl http://localhost:8002/health
```

## 📡 Service URLs

- **API Base**: http://localhost:8002/api/v1
- **Health Check**: http://localhost:8002/health
- **API Documentation**: http://localhost:8002/docs (when DEBUG=True)

## 🧪 Test the API

### 1. Create a camera
```bash
curl -X POST http://localhost:8002/api/v1/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "model": "NCxx67-X5TPC",
    "mac": "c3:16:1c:11:2b:34",
    "firmwareVersion": "21.8.0.2",
    "ipaddress": "192.168.63.232",
    "deviceName": "Test Camera",
    "deviceLocation": "Main Gate"
  }'
```

### 2. List cameras
```bash
curl http://localhost:8002/api/v1/cameras
```

### 3. Ingest an event
```bash
curl -X POST http://localhost:8002/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "DeviceInfo": {
      "DeviceName": "Test Camera",
      "DeviceIP": "192.168.63.232",
      "DeviceModel": "NCxx67-X5TPC",
      "FirmwareVersion": "21.8.0.2"
    },
    "EventInfo": {
      "EventType": "LPR",
      "EventID": "TEST_001",
      "EventTime": "2025-11-16T12:00:00+05:30",
      "EventDescription": "Test event"
    },
    "PlateInfo": {
      "PlateNumber": "ABC123",
      "PlateColor": "White",
      "VehicleColor": "Silver",
      "VehicleType": "Car",
      "Confidence": 95
    }
  }'
```

### 4. List events
```bash
curl http://localhost:8002/api/v1/events
```

## 🔧 Common Operations

### View logs
```bash
docker-compose logs -f anpr-service
```

### Restart service
```bash
docker-compose restart anpr-service
```

### Rebuild after code changes
```bash
docker-compose up -d --build anpr-service
```

### Access database
```bash
docker-compose exec mysql mysql -u app_user -papp_password its_dashboard
```

### Run migrations manually
```bash
docker-compose exec anpr-service alembic upgrade head
```

### Access service shell
```bash
docker-compose exec anpr-service bash
```

### Stop service
```bash
docker-compose stop anpr-service
```

### Stop all services
```bash
docker-compose down
```

## 📊 Database Tables

The following tables are automatically created on first startup:

1. **anpr_cameras** - Camera inventory
   - Stores camera configuration (MAC, IP, model, location, etc.)

2. **lpr_events** - Main event records
   - Stores plate detections with device info, timestamps, plate details

3. **list_events** - List matching
   - Whitelist/blacklist matches for plates

4. **attribute_events** - Vehicle attributes
   - Additional vehicle details (make, color, size, etc.)

5. **violation_events** - Traffic violations
   - Speeding and other violation records

6. **vehicle_counting_events** - Counting data
   - Vehicle counting statistics per lane/region

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs anpr-service

# Check if MySQL is ready
docker-compose ps mysql

# Rebuild
docker-compose build --no-cache anpr-service
docker-compose up -d anpr-service
```

### Migration errors
```bash
# Check migration status
docker-compose exec anpr-service alembic current

# View migration history
docker-compose exec anpr-service alembic history

# Manually run migrations
docker-compose exec anpr-service alembic upgrade head
```

### Database connection issues
```bash
# Verify environment variables
docker-compose exec anpr-service env | grep DB_

# Test database connection
docker-compose exec anpr-service python -c "
from services.shared.database.session import engine
print(engine.connect())
"
```

### Port already in use
If port 8002 is already in use, edit `docker-compose.yml`:
```yaml
ports:
  - "8003:8000"  # Change 8002 to any available port
```

## 📚 Additional Resources

- [Quick Start Guide](QUICK_START.md) - Detailed API testing examples
- [README](README.md) - Full service documentation
- [Docker Setup Guide](../../DOCKER_SETUP.md) - Complete Docker documentation
- [Sample Event Payload](/Users/hellohasib/Documents/Development/ITS-Dashboard/JSON%20code.txt)

## 🎯 What's Next?

1. **Test the endpoints** using the examples above or via Swagger UI at http://localhost:8002/docs
2. **Integrate with your cameras** by configuring them to POST events to `/api/v1/events`
3. **Monitor logs** with `docker-compose logs -f anpr-service`
4. **Scale up** by adding more ANPR service instances if needed

## 💡 Tips

- The service automatically runs migrations on startup
- Code changes are hot-reloaded in development mode
- Use the Swagger UI at `/docs` for interactive API testing
- Check `/health` endpoint to verify service status
- All timestamps support timezone-aware datetime values

