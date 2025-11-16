"""
ANPR service API routers.
"""
from fastapi import APIRouter

from . import cameras, events

api_router = APIRouter()
api_router.include_router(cameras.router, prefix="/cameras", tags=["cameras"])
api_router.include_router(events.router, prefix="/events", tags=["events"])

__all__ = ["api_router"]


