"""
Pydantic schemas for camera operations.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_serializer


def _alias(name: str) -> str:
    """Helper to define serialization alias."""
    return name


class CameraBase(BaseModel):
    """
    Shared attributes for camera schemas.
    """

    model_config = ConfigDict(populate_by_name=True)

    model: str = Field(
        ...,
        max_length=255,
        description="Camera model identifier",
    )
    mac: str = Field(
        ...,
        max_length=32,
        description="MAC address of the camera",
    )
    firmware_version: Optional[str] = Field(
        default=None,
        max_length=128,
        validation_alias=AliasChoices("firmwareVersion", "firmware_version"),
        serialization_alias="firmwareVersion",
    )
    system_boot_time: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("systemBootTime", "system_boot_time"),
        serialization_alias="systemBootTime",
        description="System boot timestamp in string format",
    )
    wireless: Optional[bool] = Field(
        default=False,
        description="Wireless capability flag",
    )
    dhcp_enable: Optional[bool] = Field(
        default=True,
        validation_alias=AliasChoices("dhcpEnable", "dhcp_enable"),
        serialization_alias="dhcpEnable",
        description="DHCP enablement flag",
    )
    ipaddress: Optional[str] = Field(
        default=None,
        description="IPv4 address of the camera",
    )
    netmask: Optional[str] = Field(
        default=None,
        description="Subnet mask",
    )
    gateway: Optional[str] = Field(
        default=None,
        description="Gateway IP",
    )
    device_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("deviceName", "device_name"),
        serialization_alias="deviceName",
        description="Human-friendly device name",
    )
    device_location: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("deviceLocation", "device_location"),
        serialization_alias="deviceLocation",
        description="Physical location of the camera",
    )


class CameraCreate(CameraBase):
    """
    Payload to create a camera.
    """

    pass


class CameraUpdate(BaseModel):
    """
    Payload to update a camera.
    """

    model_config = ConfigDict(populate_by_name=True)

    model: Optional[str] = Field(default=None, max_length=255)
    mac: Optional[str] = Field(default=None, max_length=32)
    firmware_version: Optional[str] = Field(
        default=None,
        max_length=128,
        validation_alias=AliasChoices("firmwareVersion", "firmware_version"),
        serialization_alias="firmwareVersion",
    )
    system_boot_time: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("systemBootTime", "system_boot_time"),
        serialization_alias="systemBootTime",
    )
    wireless: Optional[bool] = Field(default=None)
    dhcp_enable: Optional[bool] = Field(
        default=None,
        validation_alias=AliasChoices("dhcpEnable", "dhcp_enable"),
        serialization_alias="dhcpEnable",
    )
    ipaddress: Optional[str] = Field(default=None)
    netmask: Optional[str] = Field(default=None)
    gateway: Optional[str] = Field(default=None)
    device_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("deviceName", "device_name"),
        serialization_alias="deviceName",
    )
    device_location: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("deviceLocation", "device_location"),
        serialization_alias="deviceLocation",
    )


class CameraRead(CameraBase):
    """
    Response schema for camera records.
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    @field_serializer("created_at", "updated_at", when_used="json")
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()


