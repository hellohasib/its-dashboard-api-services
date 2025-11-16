"""
Camera API routes for the ANPR service.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from services.shared.database.session import get_db
from app.schemas import CameraCreate, CameraUpdate, CameraRead
from app.services import CameraService

router = APIRouter()


@router.get("/", response_model=List[CameraRead])
def list_cameras(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[CameraRead]:
    """
    Retrieve a paginated list of cameras.
    """
    return CameraService(db).list_cameras(skip=skip, limit=limit)


@router.get("/{camera_id}", response_model=CameraRead)
def get_camera(
    camera_id: int,
    db: Session = Depends(get_db),
) -> CameraRead:
    """
    Retrieve camera details by ID.
    """
    camera = CameraService(db).get_camera(camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera {camera_id} not found",
        )
    return camera


@router.post("/", response_model=CameraRead, status_code=status.HTTP_201_CREATED)
def create_camera(
    payload: CameraCreate,
    db: Session = Depends(get_db),
) -> CameraRead:
    """
    Create a new camera entry.
    """
    service = CameraService(db)
    if service.get_camera_by_mac(payload.mac):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Camera with this MAC address already exists",
        )
    if payload.ipaddress and service.get_camera_by_ip(payload.ipaddress):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Camera with this IP address already exists",
        )
    return service.create_camera(payload)


@router.put("/{camera_id}", response_model=CameraRead)
def update_camera(
    camera_id: int,
    payload: CameraUpdate,
    db: Session = Depends(get_db),
) -> CameraRead:
    """
    Update an existing camera entry.
    """
    service = CameraService(db)
    camera = service.get_camera(camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera {camera_id} not found",
        )
    return service.update_camera(camera_id, payload)


