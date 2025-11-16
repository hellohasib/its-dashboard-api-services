"""
Camera model for the ANPR service.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from services.shared.database.base import BaseModel


class Camera(BaseModel):
    """
    Represents an ANPR camera configuration entry.
    """

    __tablename__ = "anpr_cameras"

    model = Column(String(255), nullable=False)
    mac = Column(String(32), unique=True, nullable=False, index=True)
    firmware_version = Column(String(128), nullable=True)
    system_boot_time = Column(DateTime(timezone=True), nullable=True)
    wireless = Column(Boolean, nullable=False, default=False)
    dhcp_enable = Column(Boolean, nullable=False, default=True)
    ipaddress = Column(String(45), unique=True, nullable=True, index=True)
    netmask = Column(String(45), nullable=True)
    gateway = Column(String(45), nullable=True)
    device_name = Column(String(255), nullable=True)
    device_location = Column(String(255), nullable=True)

    events = relationship(
        "LprEvent",
        back_populates="camera",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Camera(id={self.id}, model={self.model}, mac={self.mac})>"


