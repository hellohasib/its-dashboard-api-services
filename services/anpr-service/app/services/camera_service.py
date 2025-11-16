"""
Camera service layer.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Camera
from app.schemas import CameraCreate, CameraUpdate, CameraRead


class CameraService:
    """
    Business logic for camera operations.
    """

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------------------
    # Query helpers
    # ---------------------------------------------------------------------
    def list_cameras(self, skip: int = 0, limit: int = 100) -> List[CameraRead]:
        stmt = select(Camera).offset(skip).limit(limit)
        cameras = self.db.execute(stmt).scalars().all()
        return [self._to_read_schema(camera) for camera in cameras]

    def get_camera(self, camera_id: int) -> Optional[CameraRead]:
        camera = self.db.get(Camera, camera_id)
        return self._to_read_schema(camera) if camera else None

    def get_camera_by_mac(self, mac: str) -> Optional[CameraRead]:
        stmt = select(Camera).where(Camera.mac == mac)
        camera = self.db.execute(stmt).scalar_one_or_none()
        return self._to_read_schema(camera) if camera else None

    def get_camera_by_ip(self, ipaddress: str) -> Optional[CameraRead]:
        stmt = select(Camera).where(Camera.ipaddress == ipaddress)
        camera = self.db.execute(stmt).scalar_one_or_none()
        return self._to_read_schema(camera) if camera else None

    # ---------------------------------------------------------------------
    # Mutations
    # ---------------------------------------------------------------------
    def create_camera(self, payload: CameraCreate) -> CameraRead:
        data = payload.model_dump(by_alias=False, exclude_none=True)
        system_boot_time_str = data.pop("system_boot_time", None)

        camera = Camera(**data)
        camera.system_boot_time = self._parse_system_boot_time(system_boot_time_str)

        self.db.add(camera)
        self.db.commit()
        self.db.refresh(camera)

        return self._to_read_schema(camera)

    def update_camera(self, camera_id: int, payload: CameraUpdate) -> CameraRead:
        camera = self.db.get(Camera, camera_id)
        if not camera:
            raise ValueError(f"Camera {camera_id} not found")

        update_data = payload.model_dump(by_alias=False, exclude_unset=True)
        system_boot_time_str = update_data.pop("system_boot_time", None)

        for field, value in update_data.items():
            setattr(camera, field, value)

        if system_boot_time_str is not None:
            camera.system_boot_time = self._parse_system_boot_time(system_boot_time_str)

        self.db.add(camera)
        self.db.commit()
        self.db.refresh(camera)

        return self._to_read_schema(camera)

    # ---------------------------------------------------------------------
    # Internal utilities
    # ---------------------------------------------------------------------
    @staticmethod
    def _parse_system_boot_time(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None

        parsers = [
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
        ]

        for fmt in parsers:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        # Fallback: try ISO parsing without raising
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"Invalid systemBootTime format: {value}") from exc

    @staticmethod
    def _to_read_schema(camera: Optional[Camera]) -> Optional[CameraRead]:
        if not camera:
            return None

        payload = {
            "id": camera.id,
            "model": camera.model,
            "mac": camera.mac,
            "firmware_version": camera.firmware_version,
            "system_boot_time": camera.system_boot_time.isoformat()
            if camera.system_boot_time
            else None,
            "wireless": camera.wireless,
            "dhcp_enable": camera.dhcp_enable,
            "ipaddress": camera.ipaddress,
            "netmask": camera.netmask,
            "gateway": camera.gateway,
            "device_name": camera.device_name,
            "device_location": camera.device_location,
            "created_at": camera.created_at,
            "updated_at": camera.updated_at,
        }

        return CameraRead.model_validate(payload)


