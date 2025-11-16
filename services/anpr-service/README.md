# ANPR Service

REST API layer for Automatic Number Plate Recognition (ANPR) data ingestion and camera management.

## Running with Docker (Recommended)

### Quick Start
```bash
cd /Users/hellohasib/Documents/Development/ITS-Dashboard/traffic-system-backend
docker-compose up -d anpr-service
```

The service will be available at: http://localhost:8002

See [DOCKER_SETUP.md](../../DOCKER_SETUP.md) for detailed Docker instructions.

## Running Locally (Development)

### Prerequisites
- Python 3.11+
- MySQL 8.0+
- Redis (optional)

### Setup
1. Install dependencies:
   ```bash
   cd /Users/hellohasib/Documents/Development/ITS-Dashboard/traffic-system-backend/services/anpr-service
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   ```bash
   export DB_HOST=localhost
   export DB_PORT=3306
   export DB_NAME=its_dashboard
   export DB_USER=app_user
   export DB_PASS=app_password
   export PYTHONPATH=/Users/hellohasib/Documents/Development/ITS-Dashboard/traffic-system-backend/services
   ```

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

4. Start the service:
   ```bash
   uvicorn app.main:app --reload --port 8002
   ```

## Database Schema

Tables created:
- `anpr_cameras` - Camera inventory and configuration
- `lpr_events` - Main LPR event records
- `list_events` - List matching events (whitelist/blacklist)
- `attribute_events` - Vehicle attribute details
- `violation_events` - Traffic violation records
- `vehicle_counting_events` - Vehicle counting statistics

## API Summary

Base path: `/api/v1`

- `GET /cameras` – List registered cameras (supports `skip` and `limit`).
- `GET /cameras/{camera_id}` – Retrieve a single camera.
- `POST /cameras` – Create or provision a camera record. Sample payload:
  ```json
  {
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
  }
  ```
- `PUT /cameras/{camera_id}` – Update an existing camera entry.
- `POST /events` – Ingest a full ANPR event (device, plate, list, attribute, violation, and counting details).
- `GET /events` – List events with optional filters (`camera_id`, `plate_number`, `event_type`, `start_time`, `end_time`, `matched_list`, `violation_type`, pagination).
- `GET /events/{event_id}` – Retrieve a single event with nested detail objects.

Enable docs locally by running with `DEBUG=true` to access Swagger UI at `/docs`.

## Quick Checks

- `uvicorn app.main:app --reload --port 8081` to start the service locally.
- `curl http://localhost:8081/health` to verify the service status.

For payload examples, see `JSON code.txt` in the repository root.


