# Logging Guide

## Overview
- Shared logging utilities provide structured JSON logs enriched with correlation IDs, user context, and service metadata.
- Request middleware automatically generates correlation IDs, records timing, and enriches downstream logs.
- Audit helpers capture high-value user activity events that can be shipped to external systems.
- Docker Compose includes an optional OpenTelemetry Collector and Loki stack for centralized log aggregation.

## Shared Logger & Context
- Import `get_logger` or `setup_logger` from `services.shared.utils.logger`.
- Use `services.shared.utils.logging_context` to bind request-specific data (`correlation_id`, `user_id`, `tenant_id`, etc.).
- Logs are emitted in JSON by default; switch to text with `LOG_FORMAT=text` for local debugging.
- Configure destinations with environment variables:
  - `LOG_DESTINATION`: `console` (default), `otlp`, or `loki`.
  - `SERVICE_NAME`, `SERVICE_NAMESPACE`: override service metadata when needed.
  - `OTLP_ENDPOINT`, `LOKI_ENDPOINT`, `LOKI_TENANT_ID`, `LOKI_TIMEOUT_SECONDS`: downstream sink settings.
- Example usage:

```python
from services.shared.utils.logger import get_logger
from services.shared.utils import logging_context as log_ctx

logger = get_logger(__name__)

def process_user(user_id: str) -> None:
    log_ctx.bind_user_context(user_id=user_id)
    log_ctx.log_with_context(
        logger,
        logging.INFO,
        "Processing user session",
        extra={"action": "session_start"},
    )
```

## Request Logging Middleware
- `RequestLoggingMiddleware` (in `services.shared.middleware.request_logging`) adds correlation IDs, captures request/response metadata, and measures latency.
- Register it early in each FastAPI app:

```python
from services.shared.middleware import configure_request_logging

configure_request_logging(
    app,
    service_name="auth-service",
    skip_paths={"/health"},
    skip_prefixes={"/docs", "/openapi"},
    log_headers=("x-request-id", "x-forwarded-for"),
)
```

- Middleware populates the logging context so downstream code and audit events inherit correlation IDs and user metadata.

## Audit Events
- The `services.shared.audit` module exposes an `AuditEvent` schema and helper `record_event`.
- Events reuse the current logging context and include actor/target identifiers, status, and metadata.
- Emit audit events from business logic:

```python
from services.shared.audit import record_event

record_event(
    action="user.roles.update",
    actor_id=str(admin_id),
    target_id=str(user.id),
    target_type="user",
    metadata={"roles": new_roles},
)
```

- Additional sinks (e.g., message brokers, databases) can be registered with `register_sink`.

## Central Log Pipeline (Docker Compose)
- `docker-compose.yml` provisions Loki (`traffic-loki`) and an OpenTelemetry Collector (`traffic-otel-collector`) using `docker/otel-collector-config.yaml`.
- Services include default environment variables to opt into centralized logging:
  - Set `LOG_DESTINATION=otlp` to send logs via OTLP gRPC to the collector.
  - Collector fans out to Loki and stdout; view logs via Loki-compatible tools (Grafana, Tempo, etc.).
- Example startup:

```shell
LOG_DESTINATION=otlp docker-compose up -d
```

- To disable centralized logging, leave `LOG_DESTINATION` unset (falls back to console).

## Adding New Services
- Import shared utilities and call `configure_request_logging(app, service_name="service-name")`.
- Set `SERVICE_NAME` in the service deployment (Docker Compose, Kubernetes, etc.) for accurate metadata.
- Emit audit events in critical flows using `record_event`.
- Ensure service images include optional dependencies if they intend to send logs to OTLP (`opentelemetry-sdk`) or Loki (`requests`).

## Operational Tips
- Use correlation IDs (`X-Correlation-ID` header) to trace activity across services.
- Run `docker logs traffic-otel-collector` for collector diagnostics.
- Adjust retention or exporters by editing `docker/otel-collector-config.yaml`.
- For production environments, forward collector output to your managed logging platform or secure storage.

