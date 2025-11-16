"""
Event service layer.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    AttributeEvent,
    Camera,
    ListEvent,
    LprEvent,
    VehicleCountingEvent,
    ViolationEvent,
)
from app.schemas import (
    LprEventCreate,
    LprEventList,
    LprEventRead,
)


class CameraNotFoundError(Exception):
    """Raised when a camera matching the event payload cannot be located."""

    def __init__(self, message: str = "Camera not registered for this event"):
        super().__init__(message)


class EventService:
    """
    Business logic for LPR events.
    """

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------
    def create_event(self, payload: LprEventCreate) -> LprEventRead:
        camera_id = self._resolve_camera_id(payload)
        if camera_id is None:
            raise CameraNotFoundError(
                "Unable to resolve camera from payload. Ensure the camera is registered and the IP address matches."
            )

        # Mutate payload so downstream consumers observe the resolved camera id
        payload.camera_id = camera_id
        device = payload.device_info
        event_info = payload.event_info
        plate = payload.plate_info

        event = LprEvent(
            camera_id=camera_id,
            device_name=device.device_name,
            device_ip=device.device_ip,
            device_model=device.device_model,
            device_firmware_version=device.firmware_version,
            event_type=event_info.event_type,
            event_uid=event_info.event_id,
            event_time=event_info.event_time,
            event_description=event_info.event_description,
            plate_number=plate.plate_number,
            plate_color=plate.plate_color,
            vehicle_color=plate.vehicle_color,
            vehicle_type=plate.vehicle_type,
            vehicle_brand=plate.brand,
            travel_direction=plate.direction,
            speed=plate.speed,
            confidence=plate.confidence,
            image_url=plate.image_url,
            plate_roi_x=plate.plate_roi.x if plate.plate_roi else None,
            plate_roi_y=plate.plate_roi.y if plate.plate_roi else None,
            plate_roi_width=plate.plate_roi.width if plate.plate_roi else None,
            plate_roi_height=plate.plate_roi.height if plate.plate_roi else None,
        )

        if payload.list_event:
            event.list_event = ListEvent(
                matched_list=payload.list_event.matched_list,
                list_id=payload.list_event.list_id,
                matched_by=payload.list_event.matched_by,
                confidence=payload.list_event.confidence,
                description=payload.list_event.description,
            )

        if payload.attribute_event:
            event.attribute_event = AttributeEvent(
                vehicle_presence=payload.attribute_event.vehicle_presence,
                vehicle_make=payload.attribute_event.vehicle_make,
                vehicle_color=payload.attribute_event.vehicle_color,
                vehicle_size=payload.attribute_event.vehicle_size,
                vehicle_direction=payload.attribute_event.vehicle_direction,
            )

        if payload.violation_event:
            event.violation_event = ViolationEvent(
                violation_type=payload.violation_event.violation_type,
                speed_limit=payload.violation_event.speed_limit,
                measured_speed=payload.violation_event.measured_speed,
                violation_status=payload.violation_event.violation_status,
                violation_image=payload.violation_event.violation_image,
            )

        if payload.vehicle_counting:
            event.vehicle_counting_event = VehicleCountingEvent(
                lane_id=payload.vehicle_counting.lane_id,
                counting_region=payload.vehicle_counting.counting_region,
                count_in=payload.vehicle_counting.count_in,
                count_out=payload.vehicle_counting.count_out,
                current_count=payload.vehicle_counting.current_count,
            )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return self._to_read_schema(event)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def get_event(self, event_id: int) -> Optional[LprEventRead]:
        event = (
            self.db.query(LprEvent)
            .options(
                joinedload(LprEvent.list_event),
                joinedload(LprEvent.attribute_event),
                joinedload(LprEvent.violation_event),
                joinedload(LprEvent.vehicle_counting_event),
            )
            .filter(LprEvent.id == event_id)
            .first()
        )
        return self._to_read_schema(event) if event else None

    def list_events(
        self,
        *,
        camera_id: Optional[int] = None,
        plate_number: Optional[str] = None,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        matched_list: Optional[str] = None,
        violation_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[LprEventList]:
        stmt = (
            select(LprEvent)
            .outerjoin(ListEvent)
            .outerjoin(ViolationEvent)
            .options(
                joinedload(LprEvent.list_event),
                joinedload(LprEvent.violation_event),
            )
        )

        if camera_id is not None:
            stmt = stmt.where(LprEvent.camera_id == camera_id)
        if plate_number:
            stmt = stmt.where(LprEvent.plate_number.ilike(f"%{plate_number}%"))
        if event_type:
            stmt = stmt.where(LprEvent.event_type == event_type)
        if start_time:
            stmt = stmt.where(LprEvent.event_time >= start_time)
        if end_time:
            stmt = stmt.where(LprEvent.event_time <= end_time)
        if matched_list:
            stmt = stmt.where(ListEvent.matched_list == matched_list)
        if violation_type:
            stmt = stmt.where(ViolationEvent.violation_type == violation_type)

        stmt = stmt.order_by(LprEvent.event_time.desc()).offset(skip).limit(limit)

        events = self.db.execute(stmt).scalars().unique().all()
        return [self._to_list_schema(event) for event in events]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _resolve_camera_id(self, payload: LprEventCreate) -> Optional[int]:
        if payload.camera_id:
            candidate_id = payload.camera_id
            if candidate_id > 0:
                camera = self.db.get(Camera, candidate_id)
                if camera:
                    return camera.id

        # Attempt lookup via IP address
        device_ip = payload.device_info.device_ip if payload.device_info else None
        if device_ip:
            stmt = select(Camera).where(Camera.ipaddress == device_ip)
            camera = self.db.execute(stmt).scalar_one_or_none()
            if camera:
                return camera.id

        # Attempt lookup by device name
        if payload.device_info and payload.device_info.device_name:
            stmt = select(Camera).where(Camera.device_name == payload.device_info.device_name)
            camera = self.db.execute(stmt).scalar_one_or_none()
            if camera:
                return camera.id

        return None

    def _to_read_schema(self, event: Optional[LprEvent]) -> Optional[LprEventRead]:
        if not event:
            return None

        plate_roi = None
        if all(
            value is not None
            for value in (
                event.plate_roi_x,
                event.plate_roi_y,
                event.plate_roi_width,
                event.plate_roi_height,
            )
        ):
            plate_roi = {
                "x": event.plate_roi_x,
                "y": event.plate_roi_y,
                "width": event.plate_roi_width,
                "height": event.plate_roi_height,
            }

        payload = {
            "id": event.id,
            "camera_id": event.camera_id,
            "device_info": {
                "device_name": event.device_name,
                "device_ip": event.device_ip,
                "device_model": event.device_model,
                "firmware_version": event.device_firmware_version,
            },
            "event_info": {
                "event_type": event.event_type,
                "event_id": event.event_uid,
                "event_time": event.event_time,
                "event_description": event.event_description,
            },
            "plate_info": {
                "plate_number": event.plate_number,
                "plate_color": event.plate_color,
                "vehicle_color": event.vehicle_color,
                "vehicle_type": event.vehicle_type,
                "brand": event.vehicle_brand,
                "direction": event.travel_direction,
                "speed": event.speed,
                "confidence": event.confidence,
                "image_url": event.image_url,
                "plate_roi": plate_roi,
            },
            "list_event": self._to_list_event_schema(event.list_event),
            "attribute_event": self._to_attribute_schema(event.attribute_event),
            "violation_event": self._to_violation_schema(event.violation_event),
            "vehicle_counting": self._to_vehicle_counting_schema(event.vehicle_counting_event),
            "created_at": event.created_at,
            "updated_at": event.updated_at,
        }

        return LprEventRead.model_validate(payload)

    def _to_list_schema(self, event: LprEvent) -> LprEventList:
        list_event = event.list_event
        violation = event.violation_event

        payload = {
            "id": event.id,
            "camera_id": event.camera_id,
            "event_type": event.event_type,
            "event_uid": event.event_uid,
            "event_time": event.event_time,
            "plate_number": event.plate_number,
            "device_name": event.device_name,
            "matched_list": list_event.matched_list if list_event else None,
            "violation_type": violation.violation_type if violation else None,
            "speed": event.speed,
            "confidence": event.confidence,
            "image_url": event.image_url,
        }

        return LprEventList.model_validate(payload)

    @staticmethod
    def _to_list_event_schema(list_event: Optional[ListEvent]) -> Optional[dict]:
        if not list_event:
            return None
        return {
            "matched_list": list_event.matched_list,
            "list_id": list_event.list_id,
            "matched_by": list_event.matched_by,
            "confidence": list_event.confidence,
            "description": list_event.description,
        }

    @staticmethod
    def _to_attribute_schema(attribute_event: Optional[AttributeEvent]) -> Optional[dict]:
        if not attribute_event:
            return None
        return {
            "vehicle_presence": attribute_event.vehicle_presence,
            "vehicle_make": attribute_event.vehicle_make,
            "vehicle_color": attribute_event.vehicle_color,
            "vehicle_size": attribute_event.vehicle_size,
            "vehicle_direction": attribute_event.vehicle_direction,
        }

    @staticmethod
    def _to_violation_schema(violation_event: Optional[ViolationEvent]) -> Optional[dict]:
        if not violation_event:
            return None
        return {
            "violation_type": violation_event.violation_type,
            "speed_limit": violation_event.speed_limit,
            "measured_speed": violation_event.measured_speed,
            "violation_status": violation_event.violation_status,
            "violation_image": violation_event.violation_image,
        }

    @staticmethod
    def _to_vehicle_counting_schema(
        vehicle_counting_event: Optional[VehicleCountingEvent],
    ) -> Optional[dict]:
        if not vehicle_counting_event:
            return None
        return {
            "lane_id": vehicle_counting_event.lane_id,
            "counting_region": vehicle_counting_event.counting_region,
            "count_in": vehicle_counting_event.count_in,
            "count_out": vehicle_counting_event.count_out,
            "current_count": vehicle_counting_event.current_count,
        }


