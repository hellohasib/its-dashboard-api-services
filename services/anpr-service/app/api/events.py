"""
LPR event API routes for the ANPR service.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from services.shared.database.session import get_db
from app.schemas import LprEventCreate, LprEventRead, LprEventList
from app.services import EventService
from app.services.event_service import CameraNotFoundError

router = APIRouter()


@router.post("/", response_model=LprEventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: LprEventCreate,
    db: Session = Depends(get_db),
) -> LprEventRead:
    """
    Ingest a new LPR event payload.
    """
    service = EventService(db)
    try:
        return service.create_event(payload)
    except CameraNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get("/", response_model=List[LprEventList])
def list_events(
    camera_id: Optional[int] = None,
    plate_number: Optional[str] = Query(default=None, min_length=3),
    event_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    matched_list: Optional[str] = None,
    violation_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[LprEventList]:
    """
    Retrieve a paginated list of LPR events with optional filters.
    """
    return EventService(db).list_events(
        camera_id=camera_id,
        plate_number=plate_number,
        event_type=event_type,
        start_time=start_time,
        end_time=end_time,
        matched_list=matched_list,
        violation_type=violation_type,
        skip=skip,
        limit=limit,
    )


@router.get("/{event_id}", response_model=LprEventRead)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
) -> LprEventRead:
    """
    Retrieve details for a single LPR event.
    """
    event = EventService(db).get_event(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found",
        )
    return event


