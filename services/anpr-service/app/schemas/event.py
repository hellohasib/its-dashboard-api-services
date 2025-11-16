"""
Pydantic schemas for LPR event operations.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
)


class DeviceInfoSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    device_name: str = Field(
        ...,
        validation_alias=AliasChoices("DeviceName", "deviceName", "device_name"),
        serialization_alias="DeviceName",
    )
    device_ip: str = Field(
        ...,
        validation_alias=AliasChoices("DeviceIP", "deviceIp", "device_ip"),
        serialization_alias="DeviceIP",
    )
    device_model: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("DeviceModel", "deviceModel", "device_model"),
        serialization_alias="DeviceModel",
    )
    firmware_version: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("FirmwareVersion", "firmwareVersion", "firmware_version"),
        serialization_alias="FirmwareVersion",
    )


class EventInfoSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    event_type: str = Field(
        ...,
        validation_alias=AliasChoices("EventType", "eventType", "event_type"),
        serialization_alias="EventType",
    )
    event_id: str = Field(
        ...,
        validation_alias=AliasChoices("EventID", "eventId", "event_id"),
        serialization_alias="EventID",
    )
    event_time: datetime = Field(
        ...,
        validation_alias=AliasChoices("EventTime", "eventTime", "event_time"),
        serialization_alias="EventTime",
    )
    event_description: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("EventDescription", "eventDescription", "event_description"),
        serialization_alias="EventDescription",
    )

    @field_serializer("event_time", when_used="json")
    def serialize_event_time(self, value: datetime) -> str:
        return value.isoformat()


class PlateROISchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    x: int = Field(
        ...,
        validation_alias=AliasChoices("X", "x"),
        serialization_alias="X",
    )
    y: int = Field(
        ...,
        validation_alias=AliasChoices("Y", "y"),
        serialization_alias="Y",
    )
    width: int = Field(
        ...,
        validation_alias=AliasChoices("Width", "width"),
        serialization_alias="Width",
    )
    height: int = Field(
        ...,
        validation_alias=AliasChoices("Height", "height"),
        serialization_alias="Height",
    )


class PlateInfoSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    plate_number: str = Field(
        ...,
        validation_alias=AliasChoices("PlateNumber", "plateNumber", "plate_number"),
        serialization_alias="PlateNumber",
    )
    plate_color: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("PlateColor", "plateColor", "plate_color"),
        serialization_alias="PlateColor",
    )
    vehicle_color: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("VehicleColor", "vehicleColor", "vehicle_color"),
        serialization_alias="VehicleColor",
    )
    vehicle_type: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("VehicleType", "vehicleType", "vehicle_type"),
        serialization_alias="VehicleType",
    )
    brand: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("Brand", "brand"),
        serialization_alias="Brand",
    )
    direction: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("Direction", "direction"),
        serialization_alias="Direction",
    )
    speed: Optional[float] = Field(
        default=None,
        validation_alias=AliasChoices("Speed", "speed"),
        serialization_alias="Speed",
    )
    confidence: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("Confidence", "confidence"),
        serialization_alias="Confidence",
    )
    plate_roi: Optional[PlateROISchema] = Field(
        default=None,
        validation_alias=AliasChoices("PlateROI", "plateROI", "plate_roi"),
        serialization_alias="PlateROI",
    )
    image_url: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("ImageURL", "imageUrl", "image_url"),
        serialization_alias="ImageURL",
    )


class ListEventSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    matched_list: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("MatchedList", "matchedList", "matched_list"),
        serialization_alias="MatchedList",
    )
    list_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("ListID", "listId", "list_id"),
        serialization_alias="ListID",
    )
    matched_by: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("MatchedBy", "matchedBy", "matched_by"),
        serialization_alias="MatchedBy",
    )
    confidence: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("Confidence", "confidence"),
        serialization_alias="Confidence",
    )
    description: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("ListDescription", "listDescription", "list_description", "description"),
        serialization_alias="ListDescription",
    )


class AttributeEventSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vehicle_presence: Optional[bool] = Field(
        default=None,
        validation_alias=AliasChoices("VehiclePresence", "vehiclePresence", "vehicle_presence"),
        serialization_alias="VehiclePresence",
    )
    vehicle_make: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("VehicleMake", "vehicleMake", "vehicle_make"),
        serialization_alias="VehicleMake",
    )
    vehicle_color: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("VehicleColor", "vehicleColor", "vehicle_color"),
        serialization_alias="VehicleColor",
    )
    vehicle_size: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("VehicleSize", "vehicleSize", "vehicle_size"),
        serialization_alias="VehicleSize",
    )
    vehicle_direction: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("VehicleDirection", "vehicleDirection", "vehicle_direction"),
        serialization_alias="VehicleDirection",
    )


class ViolationEventSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    violation_type: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("ViolationType", "violationType", "violation_type"),
        serialization_alias="ViolationType",
    )
    speed_limit: Optional[float] = Field(
        default=None,
        validation_alias=AliasChoices("SpeedLimit", "speedLimit", "speed_limit"),
        serialization_alias="SpeedLimit",
    )
    measured_speed: Optional[float] = Field(
        default=None,
        validation_alias=AliasChoices("MeasuredSpeed", "measuredSpeed", "measured_speed"),
        serialization_alias="MeasuredSpeed",
    )
    violation_status: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("ViolationStatus", "violationStatus", "violation_status"),
        serialization_alias="ViolationStatus",
    )
    violation_image: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("ViolationImage", "violationImage", "violation_image"),
        serialization_alias="ViolationImage",
    )


class VehicleCountingSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lane_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("LaneID", "laneId", "lane_id"),
        serialization_alias="LaneID",
    )
    counting_region: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("CountingRegion", "countingRegion", "counting_region"),
        serialization_alias="CountingRegion",
    )
    count_in: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("CountIn", "countIn", "count_in"),
        serialization_alias="CountIn",
    )
    count_out: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("CountOut", "countOut", "count_out"),
        serialization_alias="CountOut",
    )
    current_count: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("CurrentCount", "currentCount", "current_count"),
        serialization_alias="CurrentCount",
    )


class LprEventCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    camera_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("cameraId", "camera_id"),
        serialization_alias="cameraId",
    )
    device_info: DeviceInfoSchema = Field(
        ...,
        validation_alias=AliasChoices("DeviceInfo", "deviceInfo", "device_info"),
        serialization_alias="DeviceInfo",
    )
    event_info: EventInfoSchema = Field(
        ...,
        validation_alias=AliasChoices("EventInfo", "eventInfo", "event_info"),
        serialization_alias="EventInfo",
    )
    plate_info: PlateInfoSchema = Field(
        ...,
        validation_alias=AliasChoices("PlateInfo", "plateInfo", "plate_info"),
        serialization_alias="PlateInfo",
    )
    list_event: Optional[ListEventSchema] = Field(
        default=None,
        validation_alias=AliasChoices("ListEvent", "listEvent", "list_event"),
        serialization_alias="ListEvent",
    )
    attribute_event: Optional[AttributeEventSchema] = Field(
        default=None,
        validation_alias=AliasChoices("AttributeEvent", "attributeEvent", "attribute_event"),
        serialization_alias="AttributeEvent",
    )
    violation_event: Optional[ViolationEventSchema] = Field(
        default=None,
        validation_alias=AliasChoices("ViolationEvent", "violationEvent", "violation_event"),
        serialization_alias="ViolationEvent",
    )
    vehicle_counting: Optional[VehicleCountingSchema] = Field(
        default=None,
        validation_alias=AliasChoices("VehicleCounting", "vehicleCounting", "vehicle_counting"),
        serialization_alias="VehicleCounting",
    )


class LprEventRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    camera_id: Optional[int] = Field(default=None, serialization_alias="cameraId")
    device_info: DeviceInfoSchema = Field(serialization_alias="DeviceInfo")
    event_info: EventInfoSchema = Field(serialization_alias="EventInfo")
    plate_info: PlateInfoSchema = Field(serialization_alias="PlateInfo")
    list_event: Optional[ListEventSchema] = Field(default=None, serialization_alias="ListEvent")
    attribute_event: Optional[AttributeEventSchema] = Field(default=None, serialization_alias="AttributeEvent")
    violation_event: Optional[ViolationEventSchema] = Field(default=None, serialization_alias="ViolationEvent")
    vehicle_counting: Optional[VehicleCountingSchema] = Field(default=None, serialization_alias="VehicleCounting")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    @field_serializer("created_at", "updated_at", when_used="json")
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()


class LprEventList(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    camera_id: Optional[int] = Field(default=None, serialization_alias="cameraId")
    event_type: str = Field(serialization_alias="eventType")
    event_uid: str = Field(serialization_alias="eventId")
    event_time: datetime = Field(serialization_alias="eventTime")
    plate_number: str = Field(serialization_alias="plateNumber")
    device_name: Optional[str] = Field(default=None, serialization_alias="deviceName")
    matched_list: Optional[str] = Field(default=None, serialization_alias="matchedList")
    violation_type: Optional[str] = Field(default=None, serialization_alias="violationType")
    speed: Optional[float] = Field(default=None, serialization_alias="speed")
    confidence: Optional[int] = Field(default=None, serialization_alias="confidence")
    image_url: Optional[str] = Field(default=None, serialization_alias="imageUrl")

    @field_serializer("event_time", when_used="json")
    def serialize_event_time(self, value: datetime) -> str:
        return value.isoformat()


