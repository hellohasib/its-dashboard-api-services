# Traffic System Backend - Microservices Architecture

Integrated Traffic System backend built with Python/FastAPI, following microservices architecture principles.

## Architecture

- **Auth Service**: Authentication and Authorization
- **ANPR Service**: License Plate Recognition data handling
- **Shared Core**: Common utilities, database connections, base classes

## Services

### Auth Service
- User authentication (JWT)
- Role-based access control (RBAC)
- Permission management
- Port: 8001

### ANPR Service
- LPR detection storage
- Camera management
- Violation tracking
- Port: 8002

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- MySQL 8.0+
- Redis

### Development Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Project Structure

```
traffic-system-backend/
├── services/
│   ├── auth-service/     # Authentication service
│   ├── anpr-service/     # ANPR service
│   └── shared/           # Shared utilities
├── docker-compose.yml
└── README.md
```

## Environment Variables

See `.env.example` for required environment variables.

## Development

Each service can be run independently:
```bash
cd services/auth-service
uvicorn app.main:app --reload
```

## License

MIT

