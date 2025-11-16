"""
Request logging middleware for FastAPI services.
"""
from __future__ import annotations

import logging
import time
from typing import Iterable, Optional, Sequence, Set, Tuple

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from services.shared.utils import logging_context as log_ctx
from services.shared.utils.logger import SERVICE_NAME as DEFAULT_SERVICE_NAME, get_logger

CorrelationHeaders = ("x-correlation-id", "x-request-id", "traceparent")


def _normalize_path(path: str) -> str:
    if not path:
        return "/"
    return path if path.startswith("/") else f"/{path}"


def _client_ip(request: Request) -> Optional[str]:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Capture request metadata, timing, and correlation IDs."""

    def __init__(
        self,
        app,
        *,
        service_name: Optional[str] = None,
        logger_name: Optional[str] = None,
        skip_paths: Optional[Sequence[str]] = None,
        skip_prefixes: Optional[Sequence[str]] = None,
        correlation_header: str = "X-Correlation-ID",
        log_headers: Optional[Iterable[str]] = None,
    ) -> None:
        super().__init__(app)
        self.service_name = service_name or DEFAULT_SERVICE_NAME
        base_logger_name = logger_name or f"{self.service_name}.requests"
        self.logger = get_logger(base_logger_name)
        self.correlation_header = correlation_header
        self.log_headers = tuple({header.lower() for header in log_headers or ()})
        self._skip_paths: Set[str] = {
            _normalize_path(path) for path in (skip_paths or ())
        }
        self._skip_prefixes: Tuple[str, ...] = tuple(
            _normalize_path(prefix) for prefix in (skip_prefixes or ())
        )

    async def dispatch(
        self, request: Request, call_next
    ) -> Response:  # type: ignore[override]
        start_time = time.perf_counter()
        correlation_id = self._resolve_correlation_id(request)
        log_ctx.clear_context()
        log_ctx.set_correlation_id(correlation_id)
        log_ctx.bind_request_context(
            path=request.url.path,
            method=request.method,
            client_ip=_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            tenant_id=request.headers.get("x-tenant-id"),
            session_id=request.headers.get("x-session-id"),
        )

        request_id = request.headers.get("x-request-id")
        traceparent = request.headers.get("traceparent")
        route = request.scope.get("route")
        route_template = getattr(route, "path", None)
        log_ctx.update_logging_context(
            request_id=request_id,
            traceparent=traceparent,
            route_template=route_template,
        )

        response: Optional[Response] = None
        error: Optional[BaseException] = None

        try:
            response = await call_next(request)
            return response
        except BaseException as exc:  # pragma: no cover - passthrough for FastAPI
            error = exc
            raise
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            status_code = response.status_code if response else 500

            if response is not None:
                response.headers.setdefault(self.correlation_header, correlation_id)

            extra = {
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
                "method": request.method,
                "path": request.url.path,
                "route": route_template,
                "service_name": self.service_name,
            }

            if self.log_headers:
                extra["request_headers"] = {
                    header: request.headers.get(header) for header in self.log_headers
                }

            if error:
                extra.update(
                    {
                        "exception": error.__class__.__name__,
                        "error_message": str(error),
                    }
                )

            if not self._should_skip(request.url.path):
                level = logging.ERROR if error else logging.INFO
                message = "Request failed" if error else "Request completed"
                log_ctx.log_with_context(
                    self.logger,
                    level,
                    message,
                    extra=extra,
                )

            log_ctx.clear_context()

    def _resolve_correlation_id(self, request: Request) -> str:
        header_value = request.headers.get(self.correlation_header.lower())
        if header_value:
            return header_value

        for header in CorrelationHeaders:
            candidate = request.headers.get(header)
            if candidate:
                return candidate

        return log_ctx.generate_correlation_id(prefix=self.service_name)

    def _should_skip(self, path: str) -> bool:
        normalized = _normalize_path(path)
        if normalized in self._skip_paths:
            return True
        return any(
            normalized.startswith(prefix.rstrip("*"))
            for prefix in self._skip_prefixes
        )


def configure_request_logging(
    app: FastAPI,
    *,
    service_name: Optional[str] = None,
    skip_paths: Optional[Sequence[str]] = None,
    skip_prefixes: Optional[Sequence[str]] = None,
    correlation_header: str = "X-Correlation-ID",
    log_headers: Optional[Iterable[str]] = None,
) -> None:
    """
    Helper to attach request logging middleware with sane defaults.
    """
    app.add_middleware(
        RequestLoggingMiddleware,
        service_name=service_name,
        skip_paths=skip_paths,
        skip_prefixes=skip_prefixes,
        correlation_header=correlation_header,
        log_headers=log_headers,
    )

