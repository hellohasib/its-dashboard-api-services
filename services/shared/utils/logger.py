"""
Centralized logging configuration with structured context support.
"""
from __future__ import annotations

import importlib
import json
import logging
import os
import socket
import sys
import warnings
from datetime import datetime
from typing import Any, Dict, Optional

try:
    import requests  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    requests = None  # type: ignore

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json").lower()  # json or text
LOG_DESTINATION = os.getenv("LOG_DESTINATION", "console").lower()

SERVICE_NAME = os.getenv("SERVICE_NAME", os.getenv("APP_NAME", "traffic-system"))
SERVICE_VERSION = os.getenv("SERVICE_VERSION", os.getenv("APP_VERSION", "0.0.0"))
SERVICE_ENVIRONMENT = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "development"))
SERVICE_NAMESPACE = os.getenv("SERVICE_NAMESPACE", "traffic-system")
HOSTNAME = os.getenv("HOSTNAME", socket.gethostname())


def _static_context() -> Dict[str, Any]:
    return {
        "service_name": SERVICE_NAME,
        "service_version": SERVICE_VERSION,
        "service_namespace": SERVICE_NAMESPACE,
        "environment": SERVICE_ENVIRONMENT,
        "host": HOSTNAME,
    }


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging with context injection."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        log_entry.update(_static_context())
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Inject context fields
        context = getattr(record, "context", None)
        if isinstance(context, dict):
            log_entry.update(context)

        # Backwards compatibility for legacy `extra`
        extra = getattr(record, "extra", None)
        if isinstance(extra, dict):
            log_entry.update(extra)

        return json.dumps(log_entry, default=str)


class LokiHandler(logging.Handler):
    """Minimal Loki HTTP handler for shipping logs to Grafana Loki."""

    def __init__(
        self,
        endpoint: str,
        labels: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: float = 5.0,
    ) -> None:
        super().__init__()
        if requests is None:
            raise RuntimeError("requests package is required for Loki logging")
        self.endpoint = endpoint.rstrip("/")
        self.labels = labels or {}
        self.labels.setdefault("service", SERVICE_NAME)
        self.tenant_id = tenant_id
        self.auth = (username, password) if username and password else None
        self.timeout = timeout
        self._session = requests.Session()  # type: ignore

    def emit(self, record: logging.LogRecord) -> None:
        if requests is None:  # pragma: no cover - guard
            return
        try:
            log_line = self.format(record)
            timestamp = str(int(datetime.utcnow().timestamp() * 1_000_000_000))
            payload = {
                "streams": [
                    {
                        "stream": self.labels,
                        "values": [[timestamp, log_line]],
                    }
                ]
            }
            headers = {"Content-Type": "application/json"}
            if self.tenant_id:
                headers["X-Scope-OrgID"] = self.tenant_id

            response = self._session.post(
                f"{self.endpoint}/loki/api/v1/push",
                data=json.dumps(payload),
                headers=headers,
                auth=self.auth,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except Exception:  # pragma: no cover - network failures
            self.handleError(record)


def _create_otlp_handler(level: int) -> Optional[logging.Handler]:
    endpoint = os.getenv("OTLP_ENDPOINT")
    if not endpoint:
        warnings.warn(
            "OTLP_ENDPOINT is not set; falling back to console logging.",
            RuntimeWarning,
        )
        return None

    try:
        otlp_module = importlib.import_module(
            "opentelemetry.exporter.otlp.proto.grpc._log_exporter"
        )
        logs_module = importlib.import_module("opentelemetry.sdk._logs")
        export_module = importlib.import_module("opentelemetry.sdk._logs.export")
        resources_module = importlib.import_module("opentelemetry.sdk.resources")
    except ImportError:
        warnings.warn(
            "OpenTelemetry logging dependencies not installed; "
            "falling back to console logging.",
            RuntimeWarning,
        )
        return None

    try:
        OTLPLogExporter = getattr(otlp_module, "OTLPLogExporter")
        LoggerProvider = getattr(logs_module, "LoggerProvider")
        LoggingHandler = getattr(logs_module, "LoggingHandler")
        BatchLogProcessor = getattr(export_module, "BatchLogProcessor")
        Resource = getattr(resources_module, "Resource")
    except AttributeError:
        warnings.warn(
            "OpenTelemetry logging modules are missing required classes; "
            "falling back to console logging.",
            RuntimeWarning,
        )
        return None

    insecure = os.getenv("OTLP_INSECURE", "true").lower() == "true"
    resource = Resource.create(
        {
            "service.name": SERVICE_NAME,
            "service.version": SERVICE_VERSION,
            "service.namespace": SERVICE_NAMESPACE,
            "service.instance.id": HOSTNAME,
            "deployment.environment": SERVICE_ENVIRONMENT,
        }
    )
    provider = LoggerProvider(resource=resource)
    exporter = OTLPLogExporter(endpoint=endpoint, insecure=insecure)
    provider.add_log_record_processor(BatchLogProcessor(exporter))
    return LoggingHandler(level=level, logger_provider=provider)


def _create_loki_handler(level: int) -> Optional[logging.Handler]:
    endpoint = os.getenv("LOKI_ENDPOINT")
    if not endpoint:
        warnings.warn(
            "LOKI_ENDPOINT is not set; falling back to console logging.",
            RuntimeWarning,
        )
        return None

    if requests is None:
        warnings.warn(
            "requests package not available; falling back to console logging.",
            RuntimeWarning,
        )
        return None

    tenant_id = os.getenv("LOKI_TENANT_ID")
    username = os.getenv("LOKI_BASIC_AUTH_USERNAME")
    password = os.getenv("LOKI_BASIC_AUTH_PASSWORD")
    timeout = float(os.getenv("LOKI_TIMEOUT_SECONDS", "5"))

    labels_raw = os.getenv("LOKI_LABELS", "")
    labels: Dict[str, Any] = {}
    if labels_raw:
        try:
            labels = json.loads(labels_raw)
        except json.JSONDecodeError:
            warnings.warn(
                "LOKI_LABELS must be valid JSON; ignoring custom labels.",
                RuntimeWarning,
            )
    labels.setdefault("environment", SERVICE_ENVIRONMENT)

    handler = LokiHandler(
        endpoint=endpoint,
        labels=labels,
        tenant_id=tenant_id,
        username=username,
        password=password,
        timeout=timeout,
    )
    handler.setLevel(level)
    return handler


def _build_handler(level: int) -> logging.Handler:
    destination = LOG_DESTINATION
    handler: Optional[logging.Handler] = None

    if destination == "console":
        handler = logging.StreamHandler(sys.stdout)
    elif destination == "otlp":
        handler = _create_otlp_handler(level)
    elif destination == "loki":
        handler = _create_loki_handler(level)
    else:
        warnings.warn(
            f"Unknown LOG_DESTINATION '{destination}'; falling back to console.",
            RuntimeWarning,
        )

    if handler is None:
        handler = logging.StreamHandler(sys.stdout)

    handler.setLevel(level)
    return handler


def _build_formatter() -> logging.Formatter:
    if LOG_FORMAT == "json":
        return JSONFormatter()

    static_meta = _static_context()
    format_string = (
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s "
        f"| service_name={static_meta['service_name']} "
        f"environment={static_meta['environment']} "
        f"host={static_meta['host']}"
    )

    class ContextAwareTextFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            base = super().format(record)
            context = getattr(record, "context", None)
            if isinstance(context, dict) and context:
                context_pairs = " ".join(
                    f"{key}={value}" for key, value in context.items()
                )
                return f"{base} {context_pairs}"
            return base

    return ContextAwareTextFormatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")


from .logging_context import (  # noqa: E402  (import after definition to avoid cycle)
    get_logging_context,
)


class ContextLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that injects contextual fields into structured logs."""

    def process(self, msg: Any, kwargs: Dict[str, Any]) -> tuple[Any, Dict[str, Any]]:
        context = kwargs.pop("context", {})
        if not isinstance(context, dict):
            context = {}

        context_fields = {}
        request_context = get_logging_context()
        if request_context:
            context_fields.update(request_context)

        context_fields.update(context)

        extra = kwargs.get("extra", {})
        if isinstance(extra, dict):
            context_fields.update(extra)

        kwargs["extra"] = {"context": {**self.extra, **context_fields}}
        return msg, kwargs


def setup_logger(
    name: str,
    level: str = LOG_LEVEL,
    *,
    adapter: bool = True,
) -> logging.Logger | ContextLoggerAdapter:
    """
    Setup and return a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        adapter: When True (default) return ContextLoggerAdapter, otherwise logging.Logger
    
    Returns:
        Configured logger/adapter instance
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    base_logger = logging.getLogger(name)
    base_logger.setLevel(numeric_level)
    base_logger.propagate = False

    if not base_logger.handlers:
        handler = _build_handler(numeric_level)
        handler.setFormatter(_build_formatter())
        base_logger.addHandler(handler)

    if not adapter:
        return base_logger

    return ContextLoggerAdapter(base_logger, _static_context())


def get_logger(name: str) -> ContextLoggerAdapter:
    """Convenience helper to retrieve a context-aware logger."""
    return setup_logger(name)


# Default logger adapter
logger = get_logger("traffic-system")

