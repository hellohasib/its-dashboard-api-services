"""
Pydantic schemas for the ANPR service.
"""

from .camera import CameraCreate, CameraUpdate, CameraRead  # noqa: F401
from .event import (  # noqa: F401
    DeviceInfoSchema,
    EventInfoSchema,
    PlateROISchema,
    PlateInfoSchema,
    ListEventSchema,
    AttributeEventSchema,
    ViolationEventSchema,
    VehicleCountingSchema,
    LprEventCreate,
    LprEventRead,
    LprEventList,
)

__all__ = [
    "CameraCreate",
    "CameraUpdate",
    "CameraRead",
    "DeviceInfoSchema",
    "EventInfoSchema",
    "PlateROISchema",
    "PlateInfoSchema",
    "ListEventSchema",
    "AttributeEventSchema",
    "ViolationEventSchema",
    "VehicleCountingSchema",
    "LprEventCreate",
    "LprEventRead",
    "LprEventList",
]


