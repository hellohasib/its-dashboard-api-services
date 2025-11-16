"""
Audit event schema and emitter utilities.
"""
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from services.shared.utils import logging_context as log_ctx
from services.shared.utils.logger import SERVICE_NAME as DEFAULT_SERVICE_NAME, get_logger

AuditSink = Callable[["AuditEvent"], None]

_audit_logger = get_logger("audit")
_sinks: List[AuditSink] = []


@dataclass
class AuditEvent:
    """Structured audit event."""

    action: str
    actor_id: Optional[str] = None
    actor_type: str = "user"
    target_id: Optional[str] = None
    target_type: Optional[str] = None
    status: str = "success"
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_service: str = DEFAULT_SERVICE_NAME
    correlation_id: Optional[str] = None
    request_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        context = log_ctx.get_logging_context()
        self.correlation_id = self.correlation_id or context.get("correlation_id")
        self.request_id = self.request_id or context.get("request_id")
        self.ip_address = self.ip_address or context.get("client_ip")
        self.user_agent = self.user_agent or context.get("user_agent")
        self.metadata = dict(self.metadata or {})

        if not self.actor_id:
            self.actor_id = context.get("user_id")

        if "route" not in self.metadata and context.get("route_template"):
            self.metadata["route"] = context["route_template"]

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["timestamp"] = self.timestamp.isoformat()
        return payload


def _default_sink(event: AuditEvent) -> None:
    """Persist audit event to the structured log stream."""
    log_ctx.log_with_context(
        _audit_logger,
        logging.INFO,
        f"AUDIT {event.action}",
        extra={"audit_event": event.to_dict()},
    )


def register_sink(sink: AuditSink) -> None:
    """Register an additional sink (e.g., message queue, database)."""
    _sinks.append(sink)


def clear_sinks() -> None:
    """Remove all registered sinks (mainly for testing)."""
    _sinks.clear()


def emit(event: AuditEvent) -> AuditEvent:
    """Emit a pre-built audit event."""
    if not _sinks:
        _default_sink(event)
    else:
        for sink in list(_sinks):
            sink(event)
    return event


def record_event(
    action: str,
    *,
    actor_id: Optional[str] = None,
    actor_type: str = "user",
    target_id: Optional[str] = None,
    target_type: Optional[str] = None,
    status: str = "success",
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    source_service: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditEvent:
    """
    Convenience helper to build and emit an audit event.
    """
    event = AuditEvent(
        action=action,
        actor_id=actor_id,
        actor_type=actor_type,
        target_id=target_id,
        target_type=target_type,
        status=status,
        description=description,
        metadata=metadata or {},
        source_service=source_service or DEFAULT_SERVICE_NAME,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return emit(event)


__all__ = [
    "AuditEvent",
    "record_event",
    "emit",
    "register_sink",
    "clear_sinks",
]

