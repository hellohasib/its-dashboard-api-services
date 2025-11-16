# ANPR Service - Quick Start Guide

## 🐳 Docker Setup (Easiest Method)

### Step 1: Navigate to Backend Directory
```bash
cd /Users/hellohasib/Documents/Development/ITS-Dashboard/traffic-system-backend
```

### Step 2: Create Environment File
If you don't have a `.env` file, create one with these minimal settings:
```bash
cat > .env << 'EOF'
DB_ROOT_PASSWORD=rootpassword
DB_NAME=its_dashboard
DB_USER=app_user
DB_PASS=app_password
DB_PORT=3307
SECRET_KEY=change-this-to-a-secure-random-string
APP_ENV=development
DEBUG=True
EOF
```

### Step 3: Start the Service
```bash
# Option A: Use the helper script
./start-anpr.sh

# Option B: Manual Docker Compose
docker-compose up -d mysql redis
sleep 10  # Wait for database
docker-compose up -d anpr-service
```

### Step 4: Verify It's Running
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f anpr-service

# Test health endpoint
curl http://localhost:8002/health
```

### Step 5: Access the API
- **API Base URL**: http://localhost:8002/api/v1
- **Health Check**: http://localhost:8002/health
- **API Documentation**: http://localhost:8002/docs (when DEBUG=True)

## 📡 Testing the API

### Create a Camera
```bash
curl -X POST http://localhost:8002/api/v1/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "model": "NCxx67-X5TPC",
    "mac": "c3:16:1c:11:2b:34",
    "firmwareVersion": "21.8.0.2",
    "systemBootTime": "07/11/2022 22:23:43",
    "wireless": 0,
    "dhcpEnable": 0,
    "ipaddress": "192.168.63.232",
    "netmask": "255.255.255.0",
    "gateway": "192.168.63.1",
    "deviceName": "Network Camera",
    "deviceLocation": "USA"
  }'
```

### List Cameras
```bash
curl http://localhost:8002/api/v1/cameras
```

### Ingest an LPR Event
```bash
curl -X POST http://localhost:8002/api/v1/events \
  -H "Content-Type: application/json" \
  -d @/Users/hellohasib/Documents/Development/ITS-Dashboard/JSON\ code.txt
```

### List Events
```bash
# All events
curl http://localhost:8002/api/v1/events

# Filter by plate number
curl "http://localhost:8002/api/v1/events?plate_number=KL07"

# Filter by camera
curl "http://localhost:8002/api/v1/events?camera_id=1"
```

## 🔍 Database Access

### Connect to MySQL
```bash
docker-compose exec mysql mysql -u app_user -papp_password its_dashboard
```

### View Tables
```sql
SHOW TABLES;
SELECT * FROM anpr_cameras;
SELECT * FROM lpr_events;
```

## 🛠️ Common Commands

### View Logs
```bash
docker-compose logs -f anpr-service
```

### Restart Service
```bash
docker-compose restart anpr-service
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build anpr-service
```

### Run Migrations Manually
```bash
docker-compose exec anpr-service alembic upgrade head
```

### Access Service Shell
```bash
docker-compose exec anpr-service bash
```

### Stop Everything
```bash
docker-compose down
```

### Reset Database (⚠️ Deletes all data)
```bash
docker-compose down -v
docker-compose up -d
```

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs for errors
docker-compose logs anpr-service

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache anpr-service
docker-compose up -d
```

### Database connection errors
```bash
# Verify MySQL is running
docker-compose ps mysql

# Check MySQL logs
docker-compose logs mysql

# Verify environment variables
docker-compose exec anpr-service env | grep DB_
```

### Migration errors
```bash
# Check current migration status
docker-compose exec anpr-service alembic current

# View migration history
docker-compose exec anpr-service alembic history

# Downgrade and re-upgrade
docker-compose exec anpr-service alembic downgrade base
docker-compose exec anpr-service alembic upgrade head
```

## 📚 API Endpoints Reference

### Cameras
- `GET /api/v1/cameras` - List all cameras
- `GET /api/v1/cameras/{id}` - Get camera by ID
- `POST /api/v1/cameras` - Create new camera
- `PUT /api/v1/cameras/{id}` - Update camera

### Events
- `GET /api/v1/events` - List events (with filters)
- `GET /api/v1/events/{id}` - Get event by ID
- `POST /api/v1/events` - Ingest new event

### Query Parameters for Events
- `camera_id` - Filter by camera ID
- `plate_number` - Search by plate number (partial match)
- `event_type` - Filter by event type
- `start_time` - Filter events after this time (ISO format)
- `end_time` - Filter events before this time (ISO format)
- `matched_list` - Filter by list match (e.g., "Whitelist")
- `violation_type` - Filter by violation type (e.g., "Speeding")
- `skip` - Pagination offset (default: 0)
- `limit` - Pagination limit (default: 100)

## 🔗 Related Documentation
- [Full README](README.md)
- [Docker Setup Guide](../../DOCKER_SETUP.md)
- [Sample Event Payload](/Users/hellohasib/Documents/Development/ITS-Dashboard/JSON%20code.txt)

