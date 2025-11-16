"""
Event models for the ANPR service.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from services.shared.database.base import BaseModel


class LprEvent(BaseModel):
    """
    Represents an LPR event captured by a camera.
    """

    __tablename__ = "lpr_events"

    camera_id = Column(
        Integer,
        ForeignKey("anpr_cameras.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Device info
    device_name = Column(String(255), nullable=True)
    device_ip = Column(String(45), nullable=True, index=True)
    device_model = Column(String(255), nullable=True)
    device_firmware_version = Column(String(128), nullable=True)

    # Event info
    event_type = Column(String(50), nullable=False)
    event_uid = Column(String(255), nullable=False, unique=True, index=True)
    event_time = Column(DateTime(timezone=True), nullable=False, index=True)
    event_description = Column(String(512), nullable=True)

    # Plate info
    plate_number = Column(String(32), nullable=False, index=True)
    plate_color = Column(String(32), nullable=True)
    vehicle_color = Column(String(32), nullable=True)
    vehicle_type = Column(String(32), nullable=True)
    vehicle_brand = Column(String(64), nullable=True)
    travel_direction = Column(String(16), nullable=True)
    speed = Column(Float, nullable=True)
    confidence = Column(Integer, nullable=True)
    image_url = Column(String(512), nullable=True)

    # Plate ROI
    plate_roi_x = Column(Integer, nullable=True)
    plate_roi_y = Column(Integer, nullable=True)
    plate_roi_width = Column(Integer, nullable=True)
    plate_roi_height = Column(Integer, nullable=True)

    camera = relationship("Camera", back_populates="events")
    list_event = relationship(
        "ListEvent",
        uselist=False,
        back_populates="event",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    attribute_event = relationship(
        "AttributeEvent",
        uselist=False,
        back_populates="event",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    violation_event = relationship(
        "ViolationEvent",
        uselist=False,
        back_populates="event",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    vehicle_counting_event = relationship(
        "VehicleCountingEvent",
        uselist=False,
        back_populates="event",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<LprEvent(id={self.id}, plate={self.plate_number}, time={self.event_time})>"


class ListEvent(BaseModel):
    """
    Represents a list-match event associated with an LPR event.
    """

    __tablename__ = "list_events"

    event_id = Column(
        Integer,
        ForeignKey("lpr_events.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    matched_list = Column(String(64), nullable=True)
    list_id = Column(String(64), nullable=True)
    matched_by = Column(String(64), nullable=True)
    confidence = Column(Integer, nullable=True)
    description = Column(String(255), nullable=True)

    event = relationship("LprEvent", back_populates="list_event")


class AttributeEvent(BaseModel):
    """
    Represents additional vehicle attributes for an LPR event.
    """

    __tablename__ = "attribute_events"

    event_id = Column(
        Integer,
        ForeignKey("lpr_events.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    vehicle_presence = Column(Boolean, nullable=True)
    vehicle_make = Column(String(64), nullable=True)
    vehicle_color = Column(String(32), nullable=True)
    vehicle_size = Column(String(32), nullable=True)
    vehicle_direction = Column(String(16), nullable=True)

    event = relationship("LprEvent", back_populates="attribute_event")


class ViolationEvent(BaseModel):
    """
    Represents a violation (e.g., speeding) detected during an LPR event.
    """

    __tablename__ = "violation_events"

    event_id = Column(
        Integer,
        ForeignKey("lpr_events.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    violation_type = Column(String(64), nullable=True)
    speed_limit = Column(Float, nullable=True)
    measured_speed = Column(Float, nullable=True)
    violation_status = Column(String(32), nullable=True)
    violation_image = Column(String(512), nullable=True)

    event = relationship("LprEvent", back_populates="violation_event")


class VehicleCountingEvent(BaseModel):
    """
    Represents vehicle counting details for an LPR event.
    """

    __tablename__ = "vehicle_counting_events"

    event_id = Column(
        Integer,
        ForeignKey("lpr_events.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    lane_id = Column(Integer, nullable=True)
    counting_region = Column(String(128), nullable=True)
    count_in = Column(Integer, nullable=True)
    count_out = Column(Integer, nullable=True)
    current_count = Column(Integer, nullable=True)

    event = relationship("LprEvent", back_populates="vehicle_counting_event")


