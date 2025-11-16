"""
Utilities for managing per-request logging context across services.
"""
from __future__ import annotations

import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Dict, Iterator, Optional

_LOG_CONTEXT: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
    "log_context", default=None
)


def _sanitize_values(values: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values to keep logs compact."""
    return {key: value for key, value in values.items() if value is not None}


def _get_context() -> Dict[str, Any]:
    ctx = _LOG_CONTEXT.get()
    return dict(ctx) if ctx else {}


def _set_context(new_context: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = _sanitize_values(new_context)
    _LOG_CONTEXT.set(sanitized)
    return sanitized


def clear_context(keys: Optional[list[str]] = None) -> Dict[str, Any]:
    """
    Clear all stored context or the provided keys.

    Args:
        keys: Keys to remove from the context. Clears everything when omitted.
    """
    if not keys:
        _LOG_CONTEXT.set({})
        return {}

    ctx = _get_context()
    for key in keys:
        ctx.pop(key, None)
    return _set_context(ctx)


def get_logging_context() -> Dict[str, Any]:
    """Return a copy of the currently active logging context."""
    return _get_context()


def update_logging_context(**kwargs: Any) -> Dict[str, Any]:
    """
    Merge new context values with the existing context.

    None values remove keys to avoid leaking stale data.
    """
    ctx = _get_context()
    for key, value in kwargs.items():
        if value is None:
            ctx.pop(key, None)
        else:
            ctx[key] = value
    return _set_context(ctx)


def generate_correlation_id(prefix: str = "req") -> str:
    """Create a correlation identifier that can be propagated across services."""
    return f"{prefix}-{uuid.uuid4().hex}"


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """
    Store the correlation ID in the logging context.

    Returns the active correlation ID.
    """
    correlation_id = correlation_id or generate_correlation_id()
    update_logging_context(correlation_id=correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """Retrieve the active correlation ID, if available."""
    return get_logging_context().get("correlation_id")


def bind_user_context(
    *,
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    roles: Optional[list[str]] = None,
) -> Dict[str, Any]:
    """Attach user-centric metadata to the logging context."""
    return update_logging_context(
        user_id=user_id,
        username=username,
        user_email=email,
        user_roles=",".join(roles) if roles else None,
    )


def bind_request_context(
    *,
    path: Optional[str] = None,
    method: Optional[str] = None,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    tenant_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Attach request metadata."""
    return update_logging_context(
        request_path=path,
        request_method=method,
        client_ip=client_ip,
        user_agent=user_agent,
        tenant_id=tenant_id,
        session_id=session_id,
    )


def log_with_context(
    logger: Any,
    level: int,
    message: str,
    *,
    extra: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> None:
    """
    Log a message enriched with both stored context and ad-hoc fields.

    Args:
        logger: A Logger or LoggerAdapter instance.
        level: Logging level (e.g. logging.INFO).
        message: Log message.
        extra: Additional structured fields for this event.
        kwargs: Additional kwargs forwarded to logger.log.
    """
    context_extra = {}
    if extra:
        context_extra.update(_sanitize_values(extra))
    kwargs.setdefault("context", context_extra)
    logger.log(level, message, **kwargs)


@contextmanager
def scoped_context(**kwargs: Any) -> Iterator[Dict[str, Any]]:
    """
    Temporarily push a context, restoring the previous state afterwards.

    Example:
        with scoped_context(job_id=\"sync-123\"):
            logger.info(\"Processing\")
    """
    current = _get_context()
    merged = _sanitize_values({**current, **kwargs})
    token = _LOG_CONTEXT.set(merged)
    try:
        yield dict(merged)
    finally:
        _LOG_CONTEXT.reset(token)

